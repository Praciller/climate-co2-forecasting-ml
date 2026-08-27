import numpy as np
import pandas as pd
import pytest

from src.evaluation.temporal_contract import validate_temporal_contract
from src.features.preprocess_timeseries import (
    build_monthly_features,
    chronological_split,
)


def _weekly_frame() -> pd.DataFrame:
    dates = pd.date_range("1958-03-29", periods=2284, freq="W-SAT")
    values = 315 + np.linspace(0, 70, len(dates)) + np.sin(np.arange(len(dates)))
    return pd.DataFrame({"co2": values}, index=dates.rename("date"))


def test_temporal_contract_validates_causal_features_and_split_boundaries() -> None:
    monthly, features = build_monthly_features(_weekly_frame())
    split_features = chronological_split(features)

    evidence = validate_temporal_contract(monthly, split_features)

    assert evidence["feature_information_cutoff"] == "origin_date"
    assert evidence["train_end"] == "1989-01-31"
    assert evidence["validation_start"] == "1989-02-28"
    assert evidence["test_start"] == "1995-07-31"


def test_temporal_contract_rejects_target_contaminated_rolling_feature() -> None:
    monthly, features = build_monthly_features(_weekly_frame())
    split_features = chronological_split(features)
    date = split_features.index[20]
    split_features.loc[date, "rolling_mean_3"] = monthly.loc[date, "co2"]

    with pytest.raises(ValueError, match="rolling_mean_3"):
        validate_temporal_contract(monthly, split_features)
