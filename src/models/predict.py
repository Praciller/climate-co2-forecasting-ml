from __future__ import annotations

import joblib
import numpy as np

from src.utils.config import MODELS_DIR


def forecast_future(horizon_months: int) -> tuple[str, np.ndarray]:
    if horizon_months < 1:
        raise ValueError("horizon_months must be positive.")

    artifact_path = MODELS_DIR / "statistical_model.joblib"
    if not artifact_path.exists():
        raise FileNotFoundError(
            "Statistical model is missing. Run "
            "`python -m src.models.train_statistical` first."
        )

    artifact = joblib.load(artifact_path)
    return artifact["model_name"], np.asarray(
        artifact["model"].forecast(horizon_months),
        dtype=float,
    )
