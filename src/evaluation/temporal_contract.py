"""Executable checks for the repository's causal time-series contract."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.preprocess_timeseries import LAG_PERIODS, ROLLING_WINDOWS
from src.utils.config import TEST_END, TRAIN_END, VALIDATION_END


def _assert_feature_matches(
    features: pd.DataFrame,
    expected: pd.Series,
    column: str,
) -> None:
    expected_values = expected.reindex(features.index).to_numpy(dtype=float)
    actual_values = features[column].to_numpy(dtype=float)
    if not np.allclose(actual_values, expected_values, equal_nan=False):
        raise ValueError(f"Feature {column} violates the causal feature contract.")


def validate_temporal_contract(
    monthly: pd.DataFrame,
    features: pd.DataFrame,
) -> dict[str, str | int]:
    """Validate boundaries, causal features, and bounded monthly imputation."""
    for name, frame in (("monthly", monthly), ("features", features)):
        if not isinstance(frame.index, pd.DatetimeIndex):
            raise TypeError(f"{name} must use a DatetimeIndex.")
        if frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
            raise ValueError(f"{name} timestamps must be unique and increasing.")
    if "co2" not in monthly or "co2" not in features:
        raise ValueError("Monthly and feature frames must contain co2.")
    if not features.index.isin(monthly.index).all():
        raise ValueError("Every feature timestamp must exist in monthly history.")
    if not np.isfinite(monthly["co2"].to_numpy(dtype=float)).all():
        raise ValueError("Monthly co2 values must be finite after causal filling.")
    if not np.allclose(
        features["co2"].to_numpy(dtype=float),
        monthly.loc[features.index, "co2"].to_numpy(dtype=float),
    ):
        raise ValueError("Feature targets do not match monthly observations.")

    shifted = monthly["co2"].shift(1)
    for period in LAG_PERIODS:
        _assert_feature_matches(
            features,
            monthly["co2"].shift(period),
            f"lag_{period}",
        )
    for window in ROLLING_WINDOWS:
        _assert_feature_matches(
            features,
            shifted.rolling(window).mean(),
            f"rolling_mean_{window}",
        )
        _assert_feature_matches(
            features,
            shifted.rolling(window).std(ddof=0),
            f"rolling_std_{window}",
        )
    _assert_feature_matches(
        features,
        pd.Series(features.index.month, index=features.index, dtype=float),
        "month",
    )
    _assert_feature_matches(
        features,
        pd.Series(features.index.quarter, index=features.index, dtype=float),
        "quarter",
    )
    _assert_feature_matches(
        features,
        pd.Series(features.index.year, index=features.index, dtype=float),
        "year",
    )

    required_splits = {"train", "validation", "test"}
    if "split" not in features or set(features["split"].dropna()) != required_splits:
        raise ValueError("Features must contain the three governed split labels.")
    train = features.loc[features["split"] == "train"]
    validation = features.loc[features["split"] == "validation"]
    test = features.loc[features["split"] == "test"]
    if not (
        train.index.max() == TRAIN_END
        and validation.index.min() > TRAIN_END
        and validation.index.max() == VALIDATION_END
        and test.index.min() > VALIDATION_END
        and test.index.max() == TEST_END
    ):
        raise ValueError("Feature rows do not match governed temporal boundaries.")
    if not train.index.max() < validation.index.min() < test.index.min():
        raise ValueError("Train, validation, and test rows must be strictly ordered.")

    imputed_months = 0
    if {"is_imputed", "observed_week_count"}.issubset(monthly.columns):
        for timestamp in monthly.index[monthly["is_imputed"].astype(bool)]:
            previous = monthly.loc[monthly.index < timestamp, "co2"]
            if previous.empty or not np.isclose(
                monthly.loc[timestamp, "co2"], previous.iloc[-1]
            ):
                raise ValueError("Imputation must use only the previous observation.")
            imputed_months += 1

    return {
        "feature_information_cutoff": "origin_date",
        "train_end": TRAIN_END.date().isoformat(),
        "validation_start": (TRAIN_END + pd.offsets.MonthEnd(1)).date().isoformat(),
        "validation_end": VALIDATION_END.date().isoformat(),
        "test_start": (VALIDATION_END + pd.offsets.MonthEnd(1)).date().isoformat(),
        "test_end": TEST_END.date().isoformat(),
        "imputed_months_checked": imputed_months,
    }
