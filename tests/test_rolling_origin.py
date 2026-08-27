import itertools

import numpy as np
import pandas as pd
import pytest

from src.evaluation.rolling_origin import (
    generate_expanding_folds,
    run_rolling_origin_backtest,
    select_robust_model,
)


def _monthly_series(periods: int = 36) -> pd.Series:
    dates = pd.date_range("2000-01-31", periods=periods, freq="ME")
    values = 300 + np.arange(periods, dtype=float) + np.sin(np.arange(periods))
    return pd.Series(values, index=dates, name="co2")


def test_expanding_folds_are_chronological_non_overlapping_and_deterministic() -> None:
    series = _monthly_series()
    folds = generate_expanding_folds(
        series.index,
        development_end=series.index[-1],
        initial_train_size=15,
        horizon=3,
        step_size=3,
    )
    repeated = generate_expanding_folds(
        series.index,
        development_end=series.index[-1],
        initial_train_size=15,
        horizon=3,
        step_size=3,
    )

    assert folds == repeated
    for previous, current in itertools.pairwise(folds):
        assert previous.validation_end < current.validation_start
        assert previous.train_end < previous.validation_start
        assert current.train_end < current.validation_start
    assert all(
        set(fold.train_dates).isdisjoint(fold.validation_dates) for fold in folds
    )
    assert all(fold.train_dates.max() < fold.validation_dates.min() for fold in folds)


def test_folds_reject_rows_after_development_boundary() -> None:
    series = _monthly_series()

    with pytest.raises(ValueError, match="development boundary"):
        generate_expanding_folds(
            series.index,
            development_end=series.index[23],
            initial_train_size=15,
            horizon=3,
        )


def test_backtest_keeps_future_rows_out_of_training_and_records_fold_metrics() -> None:
    series = _monthly_series()
    development_end = series.index[29]
    folds = generate_expanding_folds(
        series.index[:30],
        development_end=development_end,
        initial_train_size=15,
        horizon=3,
        step_size=3,
    )

    result = run_rolling_origin_backtest(
        series,
        folds,
        models=("Naive", "Seasonal Naive"),
    )

    assert len(result.folds) == len(folds)
    assert set(result.aggregate) == {"Naive", "Seasonal Naive"}
    for fold, record in zip(folds, result.folds, strict=True):
        assert record["train_end"] == fold.train_end.date().isoformat()
        assert record["validation_end"] == fold.validation_end.date().isoformat()
        assert record["horizon"] == 3
        assert set(record["models"]) == {"Naive", "Seasonal Naive"}
        assert set(record["models"]["Naive"]) >= {
            "mae",
            "rmse",
            "smape",
            "mase",
        }
        assert fold.train_dates.max() < fold.validation_dates.min()

    for frame in result.predictions.values():
        assert frame.index.max() <= development_end
        assert (frame["date"] > frame["origin_date"]).all()

    first_fold = result.predictions["Naive"].query("fold_id == 1")
    assert first_fold["prediction"].iloc[0] == pytest.approx(series.iloc[14])

    extended_series = pd.concat(
        [
            series,
            pd.Series(
                [999.0, 1000.0],
                index=pd.date_range("2003-01-31", periods=2, freq="ME"),
            ),
        ]
    )
    extended_result = run_rolling_origin_backtest(
        extended_series,
        folds,
        models=("Naive", "Seasonal Naive"),
        development_end=development_end,
    )
    for model_name in result.predictions:
        pd.testing.assert_frame_equal(
            result.predictions[model_name], extended_result.predictions[model_name]
        )


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"horizon": 0}, "horizon"),
        ({"horizon": 4, "step_size": 3}, "step_size"),
        ({"initial_train_size": 12, "horizon": 3}, "seasonal"),
    ],
)
def test_invalid_fold_configuration_fails_clearly(
    kwargs: dict[str, int],
    message: str,
) -> None:
    series = _monthly_series()
    options = {
        "development_end": series.index[-1],
        "initial_train_size": 15,
        "horizon": 3,
        "step_size": 3,
    }
    options.update(kwargs)

    with pytest.raises(ValueError, match=message):
        generate_expanding_folds(series.index, **options)


def test_robust_model_selection_uses_fold_mean_then_rmse() -> None:
    aggregate = {
        "Naive": {
            "mae": {"mean": 1.0, "median": 1.0, "std": 0.1},
            "rmse": {"mean": 1.2, "median": 1.2, "std": 0.1},
        },
        "SARIMA": {
            "mae": {"mean": 1.0, "median": 1.0, "std": 0.1},
            "rmse": {"mean": 1.1, "median": 1.1, "std": 0.1},
        },
    }

    assert select_robust_model(aggregate) == "SARIMA"
