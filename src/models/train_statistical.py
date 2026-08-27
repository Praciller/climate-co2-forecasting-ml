from __future__ import annotations

import warnings

import joblib
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.evaluation.metrics import calculate_metrics
from src.models.common import (
    load_modeling_data,
    save_forecast_plot,
    save_metrics,
    save_prediction_artifact,
)
from src.utils.config import (
    FIGURES_DIR,
    MODELS_DIR,
    REPORTS_DIR,
)


def fit_exponential_smoothing(series: pd.Series):
    return ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)


def fit_sarima(series: pd.Series):
    with warnings.catch_warnings():
        warnings.simplefilter("default")
        return SARIMAX(
            series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False, maxiter=100)


def rolling_exponential_smoothing(
    history: pd.Series,
    test: pd.Series,
) -> np.ndarray:
    observed = history.copy()
    predictions = []
    for forecast_date, actual in test.items():
        model = fit_exponential_smoothing(observed)
        predictions.append(float(model.forecast(1).iloc[0]))
        observed = pd.concat(
            [observed, pd.Series([actual], index=pd.DatetimeIndex([forecast_date]))]
        )
        observed.index = pd.DatetimeIndex(observed.index, freq="ME", name="date")
    return np.asarray(predictions)


def rolling_sarima(history: pd.Series, test: pd.Series) -> np.ndarray:
    model = fit_sarima(history)
    predictions = []
    for forecast_date, actual in test.items():
        predictions.append(float(model.forecast(1).iloc[0]))
        observation = pd.DataFrame(
            {"co2": [actual]},
            index=pd.DatetimeIndex([forecast_date], freq="ME", name="date"),
        )
        model = model.append(observation, refit=False)
    return np.asarray(predictions)


def main() -> None:
    monthly, features = load_modeling_data()
    metrics = {}
    predictions = {}

    for split_name in ("validation", "test"):
        target_dates = features.index[features["split"] == split_name]
        history = monthly.loc[monthly.index < target_dates.min(), "co2"]
        target = monthly.loc[target_dates, "co2"]
        prediction_values = {
            "Exponential Smoothing": rolling_exponential_smoothing(
                history,
                target,
            ),
            "SARIMA": rolling_sarima(history, target),
        }
        split_metrics = {}
        for model_name, values in prediction_values.items():
            split_metrics[model_name] = calculate_metrics(
                target.to_numpy(),
                values,
                history.to_numpy(),
            )
            save_prediction_artifact(
                model_name,
                target.index,
                target,
                values,
                evaluation_split=split_name,
                refit_at_each_origin=model_name == "Exponential Smoothing",
            )
            if split_name == "test":
                predictions[model_name] = pd.Series(values, index=target.index)
        metrics[split_name] = split_metrics

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for model_name, model in (
        ("Exponential Smoothing", fit_exponential_smoothing(monthly["co2"])),
        ("SARIMA", fit_sarima(monthly["co2"])),
    ):
        joblib.dump(
            {"model_name": model_name, "model": model},
            MODELS_DIR / f"{model_name.lower().replace(' ', '_')}.joblib",
        )
    save_metrics(REPORTS_DIR / "statistical_metrics.json", metrics)
    save_forecast_plot(
        FIGURES_DIR / "statistical_forecast.png",
        "Statistical rolling one-step forecasts on the final test period",
        target,
        predictions,
    )
    print("Generated validation and final-test evidence for statistical models.")


if __name__ == "__main__":
    main()
