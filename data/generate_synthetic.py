from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "data" / "gst_filings.csv"
RNG = np.random.default_rng(42)

SECTORS = {
    "Textile": 1.15,
    "Granite": 1.35,
    "Automobile": 1.25,
    "FMCG": 0.95,
    "Leather": 1.05,
    "Steel": 1.45,
    "Electronics": 1.2,
    "Services": 0.8,
}
STATES = ["TN", "KA", "AP", "KL", "MH"]


def make_gstin(i: int, state_code: str) -> str:
    checksum = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i % 26]
    return f"33{state_code}{i:07d}{checksum}1Z{i % 9}"


def generate(rows: int = 120_000) -> pd.DataFrame:
    sectors = np.array(list(SECTORS))
    sector = RNG.choice(sectors, rows, p=[0.2, 0.1, 0.12, 0.2, 0.1, 0.08, 0.1, 0.1])
    state = RNG.choice(STATES, rows, p=[0.72, 0.08, 0.07, 0.06, 0.07])
    month = RNG.integers(1, 19, rows)
    period = np.array([f"2025-{((m - 1) % 12) + 1:02d}" if m <= 12 else f"2026-{m - 12:02d}" for m in month])
    anomaly = RNG.random(rows) < 0.018

    sector_factor = np.array([SECTORS[s] for s in sector])
    base_turnover = RNG.lognormal(mean=8.8, sigma=0.75, size=rows) * sector_factor
    drift_factor = np.where(month >= 9, 1.08, 1.0)
    taxable_turnover = base_turnover * drift_factor

    output_tax_liability = taxable_turnover * RNG.normal(0.115, 0.018, rows).clip(0.04, 0.22)
    itc_claimed = output_tax_liability * RNG.normal(0.58, 0.16, rows).clip(0.05, 1.1)
    filing_delay_days = RNG.poisson(6, rows)
    filing_gap_months = RNG.choice([0, 1, 2, 3], rows, p=[0.86, 0.1, 0.03, 0.01])

    taxable_turnover[anomaly] *= RNG.normal(0.68, 0.13, anomaly.sum()).clip(0.35, 0.95)
    itc_claimed[anomaly] *= RNG.normal(1.85, 0.35, anomaly.sum()).clip(1.2, 3.0)
    filing_delay_days[anomaly] += RNG.poisson(12, anomaly.sum())
    filing_gap_months[anomaly] = RNG.choice([1, 2, 3], anomaly.sum(), p=[0.2, 0.45, 0.35])

    net_tax_paid = np.maximum(output_tax_liability - itc_claimed, 0)
    gstin = np.array([make_gstin(i % 55_000, state[i]) for i in range(rows)])

    df = pd.DataFrame(
        {
            "gstin": gstin,
            "filing_period": period,
            "month_index": month,
            "sector_code": sector,
            "state_code": state,
            "taxable_turnover": taxable_turnover.round(2),
            "output_tax_liability": output_tax_liability.round(2),
            "itc_claimed": itc_claimed.round(2),
            "net_tax_paid": net_tax_paid.round(2),
            "filing_delay_days": filing_delay_days,
            "filing_gap_months": filing_gap_months,
            "anomaly_flag": anomaly.astype(int),
        }
    )

    itc_missing = RNG.random(rows) < 0.06
    delay_missing = RNG.random(rows) < 0.04
    df.loc[itc_missing, "itc_claimed"] = np.nan
    df.loc[delay_missing, "filing_delay_days"] = np.nan

    duplicates = df.sample(frac=0.012, random_state=42)
    return pd.concat([df, duplicates], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(df):,} rows to {OUT_FILE}")
    print(f"Anomaly prevalence: {df['anomaly_flag'].mean():.2%}")


if __name__ == "__main__":
    main()
