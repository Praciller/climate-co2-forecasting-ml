from __future__ import annotations

import numpy as np
import pandas as pd

from src.evaluation.metrics import calculate_metrics
from src.models.common import (
    load_modeling_data,
    save_forecast_plot,
    save_metrics,
    save_prediction_artifact,
)
from src.utils.config import FIGURES_DIR, REPORTS_DIR


def walk_forward_baselines(
    history: pd.Series,
    test: pd.Series,
) -> dict[str, np.ndarray]:
    observed = history.tolist()
    predictions = {
        "Naive": [],
        "Moving Average": [],
        "Seasonal Naive": [],
    }

    for actual in test:
        predictions["Naive"].append(observed[-1])
        predictions["Moving Average"].append(float(np.mean(observed[-12:])))
        predictions["Seasonal Naive"].append(observed[-12])
        observed.append(float(actual))

    return {name: np.asarray(values) for name, values in predictions.items()}


def main() -> None:
    monthly, features = load_modeling_data()
    test_dates = features.index[features["split"] == "test"]
    test = monthly.loc[test_dates, "co2"]
    history = monthly.loc[monthly.index < test_dates.min(), "co2"]
    predictions = walk_forward_baselines(history, test)
    metrics = {}
    plotted = {}

    for model_name, values in predictions.items():
        metrics[model_name] = calculate_metrics(
            test.to_numpy(),
            values,
            history.to_numpy(),
        )
        save_prediction_artifact(model_name, test.index, test, values)
        plotted[model_name] = pd.Series(values, index=test.index)

    save_metrics(REPORTS_DIR / "baseline_metrics.json", metrics)
    save_forecast_plot(
        FIGURES_DIR / "baseline_forecast.png",
        "Baseline forecasts on the held-out test period",
        test,
        plotted,
    )
    print("Trained and evaluated three baseline models.")


if __name__ == "__main__":
    main()
