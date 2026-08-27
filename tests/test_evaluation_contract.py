import numpy as np
import pandas as pd
import pytest

from src.evaluation.evaluate_forecasts import (
    conformal_radius,
    verify_prediction_contract,
)


def _prediction_frame() -> pd.DataFrame:
    dates = pd.date_range("2000-01-31", periods=3, freq="ME")
    return pd.DataFrame(
        {
            "origin_date": dates - pd.offsets.MonthEnd(1),
            "horizon": 1,
            "evaluation_split": "validation",
            "protocol": "rolling-origin one-step-ahead",
            "refit_at_origin": False,
            "actual": [1.0, 2.0, 3.0],
            "prediction": [1.1, 1.9, 3.2],
        },
        index=dates.rename("date"),
    )


def test_prediction_contract_checks_origin_and_target_alignment() -> None:
    frame = _prediction_frame()
    index = verify_prediction_contract(
        {"Naive": frame, "Seasonal Naive": frame.copy()},
        "validation",
    )

    assert index.equals(frame.index)
    assert (frame["origin_date"] < frame.index).all()


def test_prediction_contract_rejects_future_origin() -> None:
    frame = _prediction_frame()
    frame.loc[frame.index[0], "origin_date"] = frame.index[0]

    with pytest.raises(ValueError, match="origin alignment"):
        verify_prediction_contract({"Naive": frame}, "validation")


def test_conformal_radius_uses_finite_sample_higher_quantile() -> None:
    residuals = pd.Series(np.arange(1, 11, dtype=float))

    assert conformal_radius(residuals, 0.8) == 9.0
