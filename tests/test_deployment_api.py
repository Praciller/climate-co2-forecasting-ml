from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from api.index import app
from scripts.install_serving_bundle import extract_and_validate_bundle
from scripts.package_serving_bundle import package_bundle
import src.api.main as api_main
from src.api.service import ForecastService


RUNTIME_PATHS = (
    "data/raw/co2_raw.csv",
    "data/processed/co2_monthly.csv",
    "data/processed/co2_features.csv",
    "reports/forecast_metrics.json",
    "reports/interval_report.json",
    "reports/residual_report.json",
    "reports/live_forecast.json",
    "reports/anomalies.csv",
)


def _runtime_fixture(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[1]
    fixture_root = tmp_path / "serving-root"
    for relative in RUNTIME_PATHS:
        source = source_root / relative
        destination = fixture_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    manifest = fixture_root / "reports" / "model_manifest.json"
    payload = json.loads(
        (source_root / "reports" / "model_manifest.json").read_text(encoding="utf-8")
    )
    for entry in payload["artifacts"].values():
        path = fixture_root / entry["path"]
        entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        entry["bytes"] = path.stat().st_size
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    return fixture_root


def test_vercel_api_prefix_preserves_core_response_semantics(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        api_main, "resolve_serving_root", lambda: _runtime_fixture(tmp_path)
    )
    with TestClient(app) as client:
        health = client.get("/api/health")
        ready = client.get("/api/ready")
        model_info = client.get("/api/model-info")
        historical = client.get("/api/historical-data")
        forecast = client.get("/api/forecast?horizon_months=24")
        anomalies = client.get("/api/anomalies")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert ready.status_code == 200
    assert ready.json() == {"ready": True, "code": "ready"}
    assert model_info.status_code == 200
    assert model_info.json()["active_model"] == "SARIMA"
    assert historical.status_code == 200
    assert len(historical.json()) == 526
    assert forecast.status_code == 200
    assert forecast.json()["horizon_months"] == 24
    assert len(forecast.json()["forecast"]) == 24
    assert anomalies.status_code == 200
    assert len(anomalies.json()) == 8


def test_vercel_api_prefix_does_not_remove_local_core_routes() -> None:
    from src.api.main import app as core_app

    with TestClient(core_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_actual_runtime_artifacts_survive_bundle_roundtrip(tmp_path: Path) -> None:
    source_root = _runtime_fixture(tmp_path)
    archive = tmp_path / "co2-serving-bundle.tar.gz"
    package_bundle(source_root, archive)
    extracted_root = extract_and_validate_bundle(archive, tmp_path / "extracted")

    service = ForecastService(root=extracted_root)

    assert service.ready is True
    assert len(service.historical_records()) == 526
    assert len(service.forecast(horizon_months=24).forecast) == 24
    assert len(service.anomalies()) == 8
