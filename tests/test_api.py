from pathlib import Path

from fastapi.testclient import TestClient

import src.api.main as api_main
from src.api.main import app
from src.api.service import ForecastService


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["ready"] is True
    assert response.json()["model_loaded"] is True


def test_readiness_endpoint_distinguishes_artifact_readiness() -> None:
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"ready": True, "code": "ready"}


def test_forecast_endpoint_rejects_invalid_horizon() -> None:
    with TestClient(app) as client:
        response = client.get("/forecast?horizon_months=0")

    assert response.status_code == 422


def test_forecast_endpoint_rejects_horizon_above_limit() -> None:
    with TestClient(app) as client:
        response = client.get("/forecast?horizon_months=61")

    assert response.status_code == 422


def test_forecast_endpoint_returns_requested_number_of_points() -> None:
    with TestClient(app) as client:
        response = client.get("/forecast?horizon_months=3")

    payload = response.json()
    assert response.status_code == 200
    assert payload["horizon_months"] == 3
    assert len(payload["forecast"]) == 3
    assert payload["model"] == "SARIMA"
    assert payload["forecast_origin"] == "2001-12-31"
    assert payload["frequency"] == "month-end"
    assert payload["interval_coverage_scope"] == "rolling one-step final test only"
    dates = [row["date"] for row in payload["forecast"]]
    assert dates == ["2002-01-31", "2002-02-28", "2002-03-31"]
    assert all(
        row["lower"] <= row["prediction"] <= row["upper"]
        for row in payload["forecast"]
    )


def test_required_read_endpoints_return_chart_ready_json() -> None:
    with TestClient(app) as client:
        model_info = client.get("/model-info")
        historical_data = client.get("/historical-data")
        anomalies = client.get("/anomalies")

    assert model_info.status_code == 200
    assert model_info.json()["active_model"] == "SARIMA"
    assert (
        model_info.json()["selection"]["evidence_split"]
        == "train/validation development folds"
    )
    assert model_info.json()["dataset"]["historical_only"] is True

    history = historical_data.json()
    assert historical_data.status_code == 200
    assert len(history) > 500
    assert {"date", "co2", "rolling_mean_12"} <= history[-1].keys()

    anomaly_rows = anomalies.json()
    assert anomalies.status_code == 200
    assert anomaly_rows
    assert {"date", "co2", "methods"} <= anomaly_rows[0].keys()


def test_missing_manifest_returns_sanitized_503(
    tmp_path: Path,
    monkeypatch,
) -> None:
    unavailable = ForecastService(tmp_path)
    monkeypatch.setattr(api_main, "ForecastService", lambda: unavailable)

    with TestClient(app) as client:
        health = client.get("/health")
        forecast = client.get("/forecast?horizon_months=1")

    assert health.status_code == 200
    assert health.json()["ready"] is False
    assert forecast.status_code == 503
    assert forecast.json() == {
        "detail": "Governed forecast artifacts are unavailable or invalid.",
        "code": "artifact_not_ready",
    }


def test_anomaly_endpoint_allows_an_empty_result(monkeypatch) -> None:
    class EmptyAnomalyService:
        def anomalies(self) -> list[dict[str, object]]:
            return []

    monkeypatch.setattr(
        api_main,
        "ForecastService",
        lambda: EmptyAnomalyService(),
    )

    with TestClient(app) as client:
        response = client.get("/anomalies")

    assert response.status_code == 200
    assert response.json() == []
