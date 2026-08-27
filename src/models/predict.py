from __future__ import annotations

import json

import numpy as np

from src.artifacts import validate_manifest
from src.utils.config import MAX_FORECAST_HORIZON, MODEL_MANIFEST_PATH


def forecast_future(horizon_months: int) -> tuple[str, np.ndarray]:
    if not 1 <= horizon_months <= MAX_FORECAST_HORIZON:
        raise ValueError(
            f"horizon_months must be between 1 and {MAX_FORECAST_HORIZON}."
        )
    _manifest, paths = validate_manifest(
        MODEL_MANIFEST_PATH,
        required_artifacts={"live_forecast"},
    )
    artifact = json.loads(paths["live_forecast"].read_text(encoding="utf-8"))
    predictions = [
        float(row["prediction"])
        for row in artifact["forecast"][:horizon_months]
    ]
    return str(artifact["model_name"]), np.asarray(predictions, dtype=float)
