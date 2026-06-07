# QUANTUM CODERS - GST Revenue Anomaly Detection

TNSDC Naan Mudhalvan 2026 Advanced AI/ML Hackathon prototype for GST revenue anomaly detection.

The rebuilt project contains two reproducible parts:

- A full-stack TN-GRAD audit dashboard served by Node.js.
- A Python data pipeline that generates synthetic GST filings, engineers anomaly features, trains a baseline model and an enriched model, and writes metrics.

## Quick Start

```bash
npm start
```

Open `http://localhost:3000`.

Demo login:

```text
admin / tngst2026
demo / demo123
quantum / quantum@svcet
```

## Reproduce ML Results

Create a Python environment, install dependencies, then run the pipeline:

```bash
pip install -r requirements.txt
python data/generate_synthetic.py
python pipeline.py
```

Outputs:

- `data/gst_filings.csv` - generated synthetic GST filing dataset.
- `reports/metrics.json` - baseline vs enriched model metrics.
- `reports/predictions.csv` - test-set anomaly scores and predictions.

## Project Structure

```text
public/index.html           Dashboard UI
src/server.js               Node API and static server
data/generate_synthetic.py  Synthetic GST dataset generator
pipeline.py                 End-to-end ML pipeline
requirements.txt            Python runtime dependencies
reports/                    Pipeline outputs
```

## Prototype Scope

The dataset is synthetic because real GSTN taxpayer-level microdata is not public. The implemented pipeline follows the Level 2 technical report: duplicate cleanup, sector-aware imputation, behavioural feature engineering, rule-based pre-filtering, temporal drift correction, class balancing, and anomaly classification.
