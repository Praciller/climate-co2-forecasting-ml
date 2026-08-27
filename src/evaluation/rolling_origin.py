"""Deterministic, leakage-safe expanding-window backtesting."""

from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.evaluation.metrics import calculate_metrics
from src.models.train_baselines import walk_forward_baselines
from src.models.train_statistical import (
    rolling_exponential_smoothing,
    rolling_sarima,
)
from src.utils.config import SEASONAL_PERIOD

DEFAULT_BACKTEST_MODELS = (
    "Naive",
    "Seasonal Naive",
    "Exponential Smoothing",
    "SARIMA",
)
METRIC_NAMES = ("mae", "rmse", "smape", "mase")
COMPLEXITY_ORDER = {
    "Naive": 0,
    "Seasonal Naive": 1,
    "Moving Average": 2,
    "Exponential Smoothing": 3,
    "SARIMA": 4,
}


@dataclass(frozen=True, eq=False)
class RollingOriginFold:
    """One expanding training window and a non-overlapping validation block."""

    fold_id: int
    train_dates: pd.DatetimeIndex
    validation_dates: pd.DatetimeIndex
    horizon: int

    @property
    def train_start(self) -> pd.Timestamp:
        return self.train_dates[0]

    @property
    def train_end(self) -> pd.Timestamp:
        return self.train_dates[-1]

    @property
    def validation_start(self) -> pd.Timestamp:
        return self.validation_dates[0]

    @property
    def validation_end(self) -> pd.Timestamp:
        return self.validation_dates[-1]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RollingOriginFold):
            return NotImplemented
        return (
            self.fold_id == other.fold_id
            and self.horizon == other.horizon
            and self.train_dates.equals(other.train_dates)
            and self.validation_dates.equals(other.validation_dates)
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "fold_id": self.fold_id,
            "train_start": self.train_start.date().isoformat(),
            "train_end": self.train_end.date().isoformat(),
            "validation_start": self.validation_start.date().isoformat(),
            "validation_end": self.validation_end.date().isoformat(),
            "train_samples": len(self.train_dates),
            "validation_samples": len(self.validation_dates),
            "horizon": self.horizon,
        }


def _validate_datetime_index(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    dates = pd.DatetimeIndex(index)
    if dates.empty:
        raise ValueError("At least one development timestamp is required.")
    if dates.has_duplicates or not dates.is_monotonic_increasing:
        raise ValueError("Development timestamps must be unique and increasing.")
    return dates


def generate_expanding_folds(
    dates: pd.DatetimeIndex,
    *,
    development_end: pd.Timestamp,
    initial_train_size: int,
    horizon: int,
    step_size: int | None = None,
) -> list[RollingOriginFold]:
    """Generate deterministic non-overlapping validation blocks.

    ``dates`` must already be the rows eligible for development evaluation.
    Passing a final-test row is rejected instead of silently truncating it.
    ``step_size`` defaults to ``horizon`` so validation blocks do not overlap.
    """
    development_dates = _validate_datetime_index(dates)
    boundary = pd.Timestamp(development_end)
    if development_dates[-1] > boundary:
        raise ValueError("Development timestamps exceed the development boundary.")
    if initial_train_size <= SEASONAL_PERIOD:
        raise ValueError("initial_train_size must exceed the seasonal MASE period.")
    if horizon < 1:
        raise ValueError("horizon must be at least 1.")
    resolved_step = horizon if step_size is None else step_size
    if resolved_step < horizon:
        raise ValueError(
            "step_size must be at least horizon to avoid overlapping validation windows."
        )
    if resolved_step < 1:
        raise ValueError("step_size must be at least 1.")
    if initial_train_size + horizon > len(development_dates):
        raise ValueError("Fold configuration does not fit the development period.")

    folds = []
    fold_number = 1
    train_stop = initial_train_size
    while train_stop + horizon <= len(development_dates):
        train_dates = development_dates[:train_stop]
        validation_dates = development_dates[train_stop : train_stop + horizon]
        folds.append(
            RollingOriginFold(
                fold_id=fold_number,
                train_dates=train_dates,
                validation_dates=validation_dates,
                horizon=horizon,
            )
        )
        train_stop += resolved_step
        fold_number += 1
    if not folds:
        raise ValueError("No complete rolling-origin folds fit the development period.")
    return folds


def _validate_series(series: pd.Series) -> pd.Series:
    if not isinstance(series, pd.Series):
        raise TypeError("Backtest input must be a pandas Series.")
    values = series.sort_index()
    if not isinstance(values.index, pd.DatetimeIndex):
        raise TypeError("Backtest input must use a DatetimeIndex.")
    if values.index.has_duplicates or not values.index.is_monotonic_increasing:
        raise ValueError("Backtest input timestamps must be unique and increasing.")
    if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError("Backtest input values must be finite and non-null.")
    return values.astype(float)


def _forecast_model(
    model_name: str,
    history: pd.Series,
    target: pd.Series,
) -> np.ndarray:
    if model_name in {"Naive", "Moving Average", "Seasonal Naive"}:
        return walk_forward_baselines(history, target)[model_name]
    if model_name == "Exponential Smoothing":
        return rolling_exponential_smoothing(history, target)
    if model_name == "SARIMA":
        return rolling_sarima(history, target)
    raise ValueError(f"Unsupported rolling-origin model: {model_name}.")


@dataclass(frozen=True)
class RollingOriginBacktest:
    """Fold metrics plus per-target predictions for development calibration."""

    folds: list[dict[str, Any]]
    aggregate: dict[str, dict[str, dict[str, float | int]]]
    predictions: dict[str, pd.DataFrame]
    models: tuple[str, ...]
    development_end: pd.Timestamp

    def as_dict(self) -> dict[str, Any]:
        return {
            "protocol": "expanding-window rolling-origin one-step-ahead",
            "development_end": self.development_end.date().isoformat(),
            "fold_count": len(self.folds),
            "models": list(self.models),
            "folds": self.folds,
            "aggregate": self.aggregate,
        }

    def residuals_for(self, model_name: str) -> pd.Series:
        if model_name not in self.predictions:
            raise KeyError(f"No predictions recorded for model: {model_name}.")
        frame = self.predictions[model_name]
        return pd.Series(
            frame["residual"].to_numpy(dtype=float),
            index=pd.DatetimeIndex(frame["date"]),
            name="residual",
        )


def run_rolling_origin_backtest(
    series: pd.Series,
    folds: Sequence[RollingOriginFold],
    *,
    models: Sequence[str] = DEFAULT_BACKTEST_MODELS,
    development_end: pd.Timestamp | None = None,
) -> RollingOriginBacktest:
    """Fit each candidate only through each fold origin and score its block."""
    values = _validate_series(series)
    selected_models = tuple(models)
    if not selected_models:
        raise ValueError("At least one rolling-origin model is required.")
    if len(set(selected_models)) != len(selected_models):
        raise ValueError("Rolling-origin model names must be unique.")
    resolved_end = pd.Timestamp(
        development_end
        if development_end is not None
        else max(fold.validation_end for fold in folds)
    )
    if values.index.max() < resolved_end:
        raise ValueError("Backtest series does not cover the development boundary.")
    if not folds:
        raise ValueError("At least one rolling-origin fold is required.")

    all_predictions: dict[str, list[dict[str, Any]]] = {
        model_name: [] for model_name in selected_models
    }
    fold_records: list[dict[str, Any]] = []
    previous_validation_end: pd.Timestamp | None = None

    for fold in folds:
        if fold.validation_end > resolved_end:
            raise ValueError("Fold validation exceeds the development boundary.")
        if fold.train_end >= fold.validation_start:
            raise ValueError("Fold training must end before validation starts.")
        if (
            previous_validation_end is not None
            and fold.validation_start <= previous_validation_end
        ):
            raise ValueError("Rolling-origin validation blocks must not overlap.")
        previous_validation_end = fold.validation_end
        if not set(fold.train_dates).issubset(values.index) or not set(
            fold.validation_dates
        ).issubset(values.index):
            raise ValueError("Fold timestamps are missing from the backtest series.")

        history = values.loc[: fold.train_end]
        target = values.loc[fold.validation_dates]
        record: dict[str, Any] = {
            **fold.as_dict(),
            "models": {},
        }
        for model_name in selected_models:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                prediction = _forecast_model(model_name, history, target)
            metrics = calculate_metrics(
                target.to_numpy(),
                prediction,
                history.to_numpy(),
            )
            record["models"][model_name] = {
                metric: metrics[metric] for metric in METRIC_NAMES
            }
            for date, actual, predicted in zip(
                target.index,
                target.to_numpy(),
                prediction,
                strict=True,
            ):
                all_predictions[model_name].append(
                    {
                        "fold_id": fold.fold_id,
                        "date": date,
                        "origin_date": date - pd.offsets.MonthEnd(1),
                        "horizon": 1,
                        "actual": float(actual),
                        "prediction": float(predicted),
                        "residual": float(actual - predicted),
                    }
                )
        fold_records.append(record)

    aggregate: dict[str, dict[str, dict[str, float | int]]] = {}
    prediction_frames: dict[str, pd.DataFrame] = {}
    for model_name, rows in all_predictions.items():
        frame = pd.DataFrame(rows).sort_values("date")
        frame.index = pd.DatetimeIndex(frame["date"], name="date")
        prediction_frames[model_name] = frame
        aggregate[model_name] = {}
        for metric in METRIC_NAMES:
            metric_values = np.asarray(
                [record["models"][model_name][metric] for record in fold_records],
                dtype=float,
            )
            aggregate[model_name][metric] = {
                "mean": float(np.mean(metric_values)),
                "median": float(np.median(metric_values)),
                "std": float(np.std(metric_values, ddof=0)),
            }
        aggregate[model_name]["folds"] = {"count": len(fold_records)}

    return RollingOriginBacktest(
        folds=fold_records,
        aggregate=aggregate,
        predictions=prediction_frames,
        models=selected_models,
        development_end=resolved_end,
    )


def select_robust_model(
    aggregate: Mapping[str, Mapping[str, Mapping[str, float | int]]],
) -> str:
    """Select by mean fold MAE, then mean RMSE, then model simplicity."""
    if not aggregate:
        raise ValueError("At least one aggregate model result is required.")
    unknown = set(aggregate) - set(COMPLEXITY_ORDER)
    if unknown:
        raise ValueError(f"No simplicity order is defined for: {sorted(unknown)}.")
    return min(
        aggregate,
        key=lambda name: (
            float(aggregate[name]["mae"]["mean"]),
            float(aggregate[name]["rmse"]["mean"]),
            COMPLEXITY_ORDER[name],
        ),
    )
