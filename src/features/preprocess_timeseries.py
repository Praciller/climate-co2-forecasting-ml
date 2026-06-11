from __future__ import annotations

import pandas as pd

from src.data.load_co2 import load_co2_dataset
from src.utils.config import (
    FEATURE_DATA_PATH,
    MONTHLY_DATA_PATH,
    PROJECT_ROOT,
    RAW_DATA_PATH,
    ensure_project_directories,
)

LAG_PERIODS = (1, 3, 6, 12)
ROLLING_WINDOWS = (3, 6, 12)
FEATURE_COLUMNS = [
    *(f"lag_{period}" for period in LAG_PERIODS),
    *(f"rolling_mean_{window}" for window in ROLLING_WINDOWS),
    *(f"rolling_std_{window}" for window in ROLLING_WINDOWS),
    "month",
    "quarter",
    "year",
]


def load_raw_frame() -> pd.DataFrame:
    if RAW_DATA_PATH.exists():
        return pd.read_csv(RAW_DATA_PATH, parse_dates=["date"], index_col="date")
    return load_co2_dataset()


def build_monthly_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if "co2" not in frame:
        raise ValueError("Expected a 'co2' column.")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise TypeError("Expected a DatetimeIndex.")
    if frame.index.has_duplicates:
        raise ValueError("Duplicate timestamps must be resolved before preprocessing.")

    monthly = (
        frame.sort_index()["co2"]
        .resample("ME")
        .mean()
        .interpolate(method="time", limit_direction="both")
        .to_frame()
    )
    features = monthly.copy()
    shifted = monthly["co2"].shift(1)

    for period in LAG_PERIODS:
        features[f"lag_{period}"] = monthly["co2"].shift(period)
    for window in ROLLING_WINDOWS:
        features[f"rolling_mean_{window}"] = shifted.rolling(window).mean()
        features[f"rolling_std_{window}"] = shifted.rolling(window).std(ddof=0)

    features["month"] = features.index.month
    features["quarter"] = features.index.quarter
    features["year"] = features.index.year
    return monthly, features.dropna().copy()


def chronological_split(frame: pd.DataFrame) -> pd.DataFrame:
    if len(frame) < 3:
        raise ValueError("At least three rows are required for chronological splitting.")

    train_end = max(1, int(len(frame) * 0.70))
    validation_end = max(train_end + 1, int(len(frame) * 0.85))
    validation_end = min(validation_end, len(frame) - 1)

    split = frame.copy()
    split["split"] = "test"
    split.iloc[:train_end, split.columns.get_loc("split")] = "train"
    split.iloc[train_end:validation_end, split.columns.get_loc("split")] = "validation"
    return split


def main() -> None:
    ensure_project_directories()
    monthly, features = build_monthly_features(load_raw_frame())
    split_features = chronological_split(features)
    monthly.to_csv(MONTHLY_DATA_PATH, index_label="date")
    split_features.to_csv(FEATURE_DATA_PATH, index_label="date")
    print(
        f"Saved monthly data to {MONTHLY_DATA_PATH.relative_to(PROJECT_ROOT)} "
        f"and features to {FEATURE_DATA_PATH.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()
