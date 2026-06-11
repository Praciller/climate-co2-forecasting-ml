from fastapi.testclient import TestClient

from src.api.main import app


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_loaded"] is True


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
    assert payload["model"] == "Exponential Smoothing"


def test_required_read_endpoints_return_chart_ready_json() -> None:
    with TestClient(app) as client:
        model_info = client.get("/model-info")
        historical_data = client.get("/historical-data")
        anomalies = client.get("/anomalies")

    assert model_info.status_code == 200
    assert model_info.json()["active_model"] == "Exponential Smoothing"

    history = historical_data.json()
    assert historical_data.status_code == 200
    assert len(history) > 500
    assert {"date", "co2", "rolling_mean_12"} <= history[-1].keys()

    anomaly_rows = anomalies.json()
    assert anomalies.status_code == 200
    assert anomaly_rows
    assert {"date", "co2", "methods"} <= anomaly_rows[0].keys()
