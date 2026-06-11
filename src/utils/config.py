from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
MODELS_DIR = PROJECT_ROOT / "models"

RAW_DATA_PATH = RAW_DATA_DIR / "co2_raw.csv"
MONTHLY_DATA_PATH = PROCESSED_DATA_DIR / "co2_monthly.csv"
FEATURE_DATA_PATH = PROCESSED_DATA_DIR / "co2_features.csv"
ANOMALIES_PATH = REPORTS_DIR / "anomalies.csv"
FORECAST_METRICS_PATH = REPORTS_DIR / "forecast_metrics.json"
LIVE_FORECAST_PATH = REPORTS_DIR / "live_forecast.json"
MAX_FORECAST_HORIZON = int(os.getenv("CO2_FORECAST_MAX_HORIZON", "60"))


def ensure_project_directories() -> None:
    for path in (
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        SAMPLE_DATA_DIR,
        REPORTS_DIR,
        FIGURES_DIR,
        MODELS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
