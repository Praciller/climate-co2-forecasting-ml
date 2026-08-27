from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

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
MODEL_MANIFEST_PATH = REPORTS_DIR / "model_manifest.json"
INTERVAL_REPORT_PATH = REPORTS_DIR / "interval_report.json"
RESIDUAL_REPORT_PATH = REPORTS_DIR / "residual_report.json"
MAX_FORECAST_HORIZON = int(os.getenv("CO2_FORECAST_MAX_HORIZON", "60"))

DATASET_NAME = "Mauna Loa Weekly Atmospheric CO2 Data"
DATASET_MODULE = "statsmodels.datasets.co2"
DATASET_UNIT = "ppmv"
DATASET_RETRIEVED_UPSTREAM = "2014-03-15"
DATASET_LICENSE = "Public domain"
PREPROCESSING_VERSION = "2.0.0"
ARTIFACT_SCHEMA_VERSION = "2.0.0"

# These dates are a governed contract, not ratios recomputed independently by
# each trainer. They preserve the original 70/15/15 feature-row boundaries.
TRAIN_END = pd.Timestamp("1989-01-31")
VALIDATION_END = pd.Timestamp("1995-06-30")
TEST_END = pd.Timestamp("2001-12-31")
SPLIT_BOUNDARIES = {
    "train_end": TRAIN_END.date().isoformat(),
    "validation_start": (TRAIN_END + pd.offsets.MonthEnd(1)).date().isoformat(),
    "validation_end": VALIDATION_END.date().isoformat(),
    "test_start": (VALIDATION_END + pd.offsets.MonthEnd(1)).date().isoformat(),
    "test_end": TEST_END.date().isoformat(),
}

SEASONAL_PERIOD = 12
INTERVAL_NOMINAL_COVERAGE = 0.90
MAX_CAUSAL_FILL_MONTHS = 3


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
