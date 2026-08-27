from __future__ import annotations

import pandas as pd

from src.data.load_co2 import load_co2_dataset
from src.utils.config import (
    FEATURE_DATA_PATH,
    MAX_CAUSAL_FILL_MONTHS,
    MONTHLY_DATA_PATH,
    PROJECT_ROOT,
    RAW_DATA_PATH,
    TEST_END,
    TRAIN_END,
    VALIDATION_END,
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

    values = frame.sort_index()["co2"]
    monthly_values = values.resample("ME").mean()
    observed_week_count = values.resample("ME").count()
    missing_before = monthly_values.isna()
    monthly_values = monthly_values.ffill(limit=MAX_CAUSAL_FILL_MONTHS)
    if monthly_values.isna().any():
        unresolved = ", ".join(
            timestamp.date().isoformat()
            for timestamp in monthly_values[monthly_values.isna()].index
        )
        raise ValueError(
            "Monthly gaps exceed the causal fill contract or occur before the "
            f"first observation: {unresolved}"
        )

    monthly = monthly_values.to_frame("co2")
    monthly["observed_week_count"] = observed_week_count.astype(int)
    monthly["is_imputed"] = missing_before
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
    if frame.empty:
        raise ValueError("At least one row is required for chronological splitting.")
    if not frame.index.is_monotonic_increasing or frame.index.has_duplicates:
        raise ValueError("Split input must have a unique, increasing datetime index.")
    if frame.index.min() > TRAIN_END or frame.index.max() < TEST_END:
        raise ValueError("Frame does not cover the governed split boundaries.")
    if frame.index.max() > TEST_END:
        raise ValueError("Frame contains observations after the governed test boundary.")

    split = frame.copy()
    split["split"] = pd.Series(index=split.index, dtype="string")
    split.loc[split.index <= TRAIN_END, "split"] = "train"
    split.loc[
        (split.index > TRAIN_END) & (split.index <= VALIDATION_END),
        "split",
    ] = "validation"
    split.loc[
        (split.index > VALIDATION_END) & (split.index <= TEST_END),
        "split",
    ] = "test"
    if split["split"].isna().any() or set(split["split"]) != {
        "train",
        "validation",
        "test",
    }:
        raise ValueError("Governed split assignment is incomplete.")
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
