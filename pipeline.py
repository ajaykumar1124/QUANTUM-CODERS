from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "gst_filings.csv"
REPORT_DIR = ROOT / "reports"
RANDOM_STATE = 42

RAW_FEATURES = [
    "taxable_turnover",
    "output_tax_liability",
    "itc_claimed",
    "net_tax_paid",
    "filing_delay_days",
    "filing_gap_months",
]
ENGINEERED_FEATURES = [
    "itc_to_turnover_ratio",
    "mom_turnover_variance",
    "filing_delay_score",
    "itc_reversal_flag",
    "sector_deviation_score",
    "rolling_3m_itc_growth",
    "rule_prefilter_flag",
]


def ensure_dataset() -> None:
    if not DATA_FILE.exists():
        from data.generate_synthetic import main as generate_main

        generate_main()


def robust_scale(frame: pd.DataFrame) -> pd.DataFrame:
    median = frame.median(numeric_only=True)
    iqr = frame.quantile(0.75, numeric_only=True) - frame.quantile(0.25, numeric_only=True)
    return ((frame - median) / iqr.replace(0, 1)).replace([np.inf, -np.inf], 0).fillna(0)


def load_clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df = df.drop_duplicates(subset=["gstin", "filing_period"], keep="first").reset_index(drop=True)

    for col in RAW_FEATURES:
        df[col] = df.groupby("sector_code")[col].transform(lambda s: s.fillna(s.median()))
        df[col] = df[col].fillna(df[col].median())

    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["gstin", "month_index"]).reset_index(drop=True)
    safe_turnover = df["taxable_turnover"].replace(0, np.nan)
    safe_output_tax = df["output_tax_liability"].replace(0, np.nan)

    df["itc_to_turnover_ratio"] = (df["itc_claimed"] / safe_turnover).fillna(0)
    df["filing_delay_score"] = (df["filing_delay_days"] / 30).clip(0, 2)
    df["itc_reversal_flag"] = (df["net_tax_paid"] <= 0).astype(int)
    df["mom_turnover_variance"] = df.groupby("gstin")["taxable_turnover"].pct_change().replace([np.inf, -np.inf], 0).fillna(0).clip(-3, 3)
    df["rolling_3m_itc_growth"] = df.groupby("gstin")["itc_claimed"].pct_change(3).replace([np.inf, -np.inf], 0).fillna(0).clip(-3, 3)

    sector_median = df.groupby("sector_code")["taxable_turnover"].transform("median")
    sector_iqr = (
        df.groupby("sector_code")["taxable_turnover"].transform(lambda s: s.quantile(0.75) - s.quantile(0.25)).replace(0, 1)
    )
    df["sector_deviation_score"] = ((df["taxable_turnover"] - sector_median) / sector_iqr).fillna(0).clip(-5, 5)

    df["rule_prefilter_flag"] = (
        (df["itc_claimed"] / safe_turnover > 0.4)
        | ((df["taxable_turnover"] > 0) & (df["net_tax_paid"] <= 0))
        | (df["filing_gap_months"] > 2)
        | (df["itc_claimed"] / safe_output_tax > 1.05)
    ).astype(int)

    cols = RAW_FEATURES + ENGINEERED_FEATURES
    for period_mask in [df["month_index"] < 9, df["month_index"] >= 9]:
        df.loc[period_mask, cols] = robust_scale(df.loc[period_mask, cols])

    return df


def stratified_split(df: pd.DataFrame, test_size: float = 0.15) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(RANDOM_STATE)
    train, test = [], []
    keys = df[["anomaly_flag", "sector_code"]].astype(str).agg("-".join, axis=1)
    for _, indices in keys.groupby(keys).groups.items():
        idx = np.array(list(indices))
        rng.shuffle(idx)
        cut = max(1, int(len(idx) * test_size))
        test.extend(idx[:cut])
        train.extend(idx[cut:])
    return np.array(train), np.array(test)


def balance_training_set(x_train: np.ndarray, y_train: np.ndarray, target_ratio: int = 5) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(RANDOM_STATE)
    minority = x_train[y_train == 1]
    majority_count = int((y_train == 0).sum())
    desired = max(1, majority_count // target_ratio)
    if len(minority) >= desired:
        return x_train, y_train

    pick = rng.integers(0, len(minority), desired - len(minority))
    synthetic = minority[pick] + rng.normal(0, 0.03, (len(pick), x_train.shape[1]))
    return np.vstack([x_train, synthetic]), np.concatenate([y_train, np.ones(len(pick), dtype=int)])


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(z, -35, 35)))


def train_logistic(x: np.ndarray, y: np.ndarray, epochs: int = 420, lr: float = 0.035) -> np.ndarray:
    x_aug = np.c_[np.ones(len(x)), x]
    weights = np.zeros(x_aug.shape[1])
    for _ in range(epochs):
        pred = sigmoid(x_aug @ weights)
        grad = (x_aug.T @ (pred - y)) / len(y)
        weights -= lr * grad
    return weights


def predict_logistic(weights: np.ndarray, x: np.ndarray) -> np.ndarray:
    return sigmoid(np.c_[np.ones(len(x)), x] @ weights)


def auc_score(y_true: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    positives = y_true == 1
    n_pos = positives.sum()
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.0
    return float((ranks[positives].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def score_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "auc_roc": round(auc_score(y_true, y_score), 4),
        "false_positive_rate": round(float(fp / max(fp + tn, 1)), 4),
    }


def main() -> None:
    ensure_dataset()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    enriched = add_features(load_clean_data())
    train_idx, test_idx = stratified_split(enriched)
    y = enriched["anomaly_flag"].astype(int).to_numpy()
    y_train, y_test = y[train_idx], y[test_idx]

    raw_train = enriched.loc[train_idx, RAW_FEATURES].to_numpy(dtype=float)
    raw_test = enriched.loc[test_idx, RAW_FEATURES].to_numpy(dtype=float)
    baseline_center = np.median(raw_train, axis=0)
    baseline_spread = np.percentile(raw_train, 75, axis=0) - np.percentile(raw_train, 25, axis=0)
    baseline_score = np.abs((raw_test - baseline_center) / np.where(baseline_spread == 0, 1, baseline_spread)).mean(axis=1)
    baseline_pred = (baseline_score >= np.quantile(baseline_score, 0.98)).astype(int)

    all_features = RAW_FEATURES + ENGINEERED_FEATURES
    x_train = enriched.loc[train_idx, all_features].to_numpy(dtype=float)
    x_test = enriched.loc[test_idx, all_features].to_numpy(dtype=float)
    x_balanced, y_balanced = balance_training_set(x_train, y_train)
    weights = train_logistic(x_balanced, y_balanced)
    improved_score = predict_logistic(weights, x_test)

    rule_col = all_features.index("rule_prefilter_flag")
    threshold = np.quantile(improved_score, 0.965)
    improved_pred = ((improved_score >= threshold) | (x_test[:, rule_col] > 0.2)).astype(int)

    metrics = {
        "records_after_deduplication": int(len(enriched)),
        "anomaly_prevalence": round(float(y.mean()), 4),
        "baseline_raw_robust_anomaly_score": score_metrics(y_test, baseline_pred, baseline_score),
        "improved_enriched_logistic_model": score_metrics(y_test, improved_pred, improved_score),
        "features": all_features,
    }

    predictions = enriched.loc[test_idx, ["gstin", "filing_period", "sector_code", "state_code", "anomaly_flag"]].copy()
    predictions["baseline_score"] = baseline_score
    predictions["improved_score"] = improved_score
    predictions["improved_prediction"] = improved_pred

    (REPORT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    predictions.to_csv(REPORT_DIR / "predictions.csv", index=False)
    print(json.dumps(metrics, indent=2))
    print(f"Wrote reports to {REPORT_DIR}")


if __name__ == "__main__":
    main()
