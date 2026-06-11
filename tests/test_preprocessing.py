import numpy as np
import pandas as pd

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
    _, features = build_monthly_features(_weekly_frame())
    split = chronological_split(features)

    train = split[split["split"] == "train"]
    validation = split[split["split"] == "validation"]
    test = split[split["split"] == "test"]

    assert len(train) > len(validation) > 0
    assert len(test) > 0
    assert train.index.max() < validation.index.min() < test.index.min()
