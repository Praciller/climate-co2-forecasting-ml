import numpy as np
import pandas as pd
import pytest

from src.evaluation.intervals import (
    calibrate_residual_radius,
    coverage_rate,
    evaluate_prediction_interval,
    symmetric_prediction_interval,
)
from src.evaluation.rolling_origin import RollingOriginBacktest
from src.evaluation.rolling_origin_evaluation import evaluate_final_test_interval


def test_calibration_rejects_governed_test_residuals() -> None:
    dates = pd.date_range("2000-01-31", periods=4, freq="ME")
    residuals = pd.Series([0.1, 0.2, 0.3, 0.4], index=dates)

    with pytest.raises(ValueError, match="calibration boundary"):
        calibrate_residual_radius(
            residuals,
            nominal_coverage=0.9,
            development_end=dates[2],
        )


def test_interval_ordering_width_and_coverage_are_measured() -> None:
    predictions = np.array([10.0, 20.0, 30.0])
    lower, upper = symmetric_prediction_interval(predictions, radius=1.5)
    actual = np.array([12.0, 19.5, 32.0])

    assert np.all(lower <= predictions)
    assert np.all(predictions <= upper)
    assert np.all((upper - lower) >= 0)
    assert coverage_rate(actual, lower, upper) == pytest.approx(1 / 3)

    evidence = evaluate_prediction_interval(
        actual,
        predictions,
        lower,
        upper,
        nominal_coverage=0.9,
    )
    assert evidence["nominal_coverage"] == 0.9
    assert evidence["empirical_coverage"] == pytest.approx(1 / 3)
    assert evidence["average_width"] == pytest.approx(3.0)


def test_interval_inputs_require_finite_ordered_bounds() -> None:
    with pytest.raises(ValueError, match="finite"):
        coverage_rate(
            np.array([1.0]),
            np.array([np.nan]),
            np.array([2.0]),
        )

    with pytest.raises(ValueError, match="(?i)lower"):
        coverage_rate(
            np.array([1.0]),
            np.array([2.0]),
            np.array([1.0]),
        )


def test_final_test_interval_requires_targets_after_development_boundary() -> None:
    development_dates = pd.date_range("2000-01-31", periods=3, freq="ME")
    residual_frame = pd.DataFrame(
        {
            "date": development_dates,
            "residual": [0.1, 0.2, 0.3],
        },
        index=development_dates,
    )
    result = RollingOriginBacktest(
        folds=[],
        aggregate={},
        predictions={"Naive": residual_frame},
        models=("Naive",),
        development_end=development_dates[-1],
    )
    final_test = pd.DataFrame(
        {"actual": [10.0], "prediction": [10.1]},
        index=pd.date_range("2000-04-30", periods=1, freq="ME"),
    )

    report, radius = evaluate_final_test_interval(
        result,
        final_test,
        "Naive",
        nominal_coverage=0.9,
    )

    assert radius == pytest.approx(0.3)
    assert report["calibration_end"] == "2000-03-31"
    assert report["evaluation_split"] == "final_test"

    with pytest.raises(ValueError, match="after the development boundary"):
        evaluate_final_test_interval(
            result,
            pd.DataFrame(
                {"actual": [10.0], "prediction": [10.1]},
                index=development_dates[-1:],
            ),
            "Naive",
            nominal_coverage=0.9,
        )
