import numpy as np
import pandas as pd
import pytest

from src.features.preprocess_timeseries import (
    FEATURE_COLUMNS,
    build_monthly_features,
    chronological_split,
)


def _weekly_frame() -> pd.DataFrame:
    index = pd.date_range("2000-01-02", periods=260, freq="W-SUN")
    values = 350 + np.linspace(0, 8, len(index)) + np.sin(np.arange(len(index)) / 8)
    return pd.DataFrame({"co2": values}, index=index.rename("date"))


def test_preprocessing_creates_required_leakage_safe_features() -> None:
    monthly, features = build_monthly_features(_weekly_frame())

    assert monthly.index.is_monotonic_increasing
    assert monthly["co2"].isna().sum() == 0
    assert set(FEATURE_COLUMNS).issubset(features.columns)
    first_feature_date = features.index[0]
    prior_month = first_feature_date - pd.offsets.MonthEnd(1)
    assert features.loc[first_feature_date, "lag_1"] == monthly.loc[prior_month, "co2"]
    assert features.loc[first_feature_date, "rolling_mean_3"] == monthly.loc[
        :prior_month, "co2"
    ].tail(3).mean()


def test_chronological_split_preserves_time_order() -> None:
    index = pd.date_range("1959-03-31", "2001-12-31", freq="ME")
    features = pd.DataFrame({"co2": np.arange(len(index))}, index=index)
    split = chronological_split(features)

    train = split[split["split"] == "train"]
    validation = split[split["split"] == "validation"]
    test = split[split["split"] == "test"]

    assert len(train) > len(validation) > 0
    assert len(test) > 0
    assert train.index.max() < validation.index.min() < test.index.min()
    assert train.index.max() == pd.Timestamp("1989-01-31")
    assert validation.index.min() == pd.Timestamp("1989-02-28")
    assert validation.index.max() == pd.Timestamp("1995-06-30")
    assert test.index.min() == pd.Timestamp("1995-07-31")
    assert test.index.max() == pd.Timestamp("2001-12-31")
    assert set(train.index).isdisjoint(validation.index)
    assert set(validation.index).isdisjoint(test.index)


def test_monthly_fill_is_causal_and_records_lineage() -> None:
    index = pd.date_range("1999-01-31", periods=24, freq="ME")
    values = np.linspace(350, 360, len(index))
    values[5] = np.nan
    original = pd.DataFrame({"co2": values}, index=index.rename("date"))
    changed_future = original.copy()
    changed_future.iloc[6, 0] = 999

    monthly, _ = build_monthly_features(original)
    changed, _ = build_monthly_features(changed_future)

    missing_month = index[5]
    assert monthly.loc[missing_month, "co2"] == monthly.iloc[4]["co2"]
    assert monthly.loc[missing_month, "co2"] == changed.loc[missing_month, "co2"]
    assert bool(monthly.loc[missing_month, "is_imputed"]) is True
    assert monthly.loc[missing_month, "observed_week_count"] == 0


def test_monthly_fill_rejects_gaps_beyond_contract() -> None:
    index = pd.date_range("1999-01-31", periods=24, freq="ME")
    values = np.linspace(350, 360, len(index))
    values[5:9] = np.nan
    frame = pd.DataFrame({"co2": values}, index=index.rename("date"))

    with pytest.raises(ValueError, match="causal fill contract"):
        build_monthly_features(frame)
