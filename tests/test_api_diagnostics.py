from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

import src.api.main as api_main
import src.api.service as service_module
from src.api.diagnostics import REDACTED, format_event
from src.api.main import app
from src.api.service import ForecastService


def test_structured_event_redacts_secrets_paths_and_token_values() -> None:
    raw = format_event(
        "diagnostic_test",
        authorization="Bearer top-secret-value",
        api_key="example-api-key",
        config={"password": "hidden", "safe": "visible"},
        root_path="C:" + "/Us" + "ers/example/private/repo",
        note="gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456",
    )
    payload = json.loads(raw)

    assert payload["authorization"] == REDACTED
    assert payload["api_key"] == REDACTED
    assert payload["config"] == {"password": REDACTED, "safe": "visible"}
    assert payload["root_path"] == REDACTED
    assert payload["note"] == REDACTED


def test_missing_manifest_emits_sanitized_failure_category(
    tmp_path: Path,
    monkeypatch,
) -> None:
    events: list[tuple[str, dict[str, object]]] = []

    def capture(event: str, **context: object) -> None:
        events.append((event, context))

    monkeypatch.setattr(service_module, "emit_event", capture)
    service = ForecastService(tmp_path)

    assert service.ready is False
    assert service.readiness_failure_category == "artifact_validation_error"
    failure = next(context for event, context in events if event == "governed_artifact_load_failed")
    assert failure["failure_category"] == "artifact_validation_error"
    assert failure["error_type"] == "ArtifactValidationError"
    serialized = json.dumps(failure)
    assert str(tmp_path) not in serialized
    assert "model_manifest.json" not in serialized


def test_request_completion_log_has_request_id_and_route_without_query(monkeypatch) -> None:
    class HealthyService:
        def __init__(self) -> None:
            self.ready = True
            self.readiness_code = "ready"
            self.readiness_failure_category = None
            self.forecast_artifact = {"model_name": "SARIMA"}
            self.history: list[object] = []

    events: list[tuple[str, dict[str, object]]] = []

    def capture(event: str, **context: object) -> None:
        events.append((event, context))

    monkeypatch.setattr(api_main, "ForecastService", HealthyService)
    monkeypatch.setattr(api_main, "emit_event", capture)

    with TestClient(app) as client:
        response = client.get("/health?token=must-not-appear")

    request_event = next(
        context for event, context in events if event == "api_request_completed"
    )
    assert response.status_code == 200
    assert request_event["method"] == "GET"
    assert request_event["route"] == "/health"
    assert request_event["status_code"] == 200
    assert float(request_event["duration_ms"]) >= 0
    assert response.headers["X-Request-ID"] == request_event["request_id"]
    assert "must-not-appear" not in json.dumps(request_event)


def test_failed_readiness_check_logs_category_without_changing_contract(monkeypatch) -> None:
    class UnreadyService:
        def __init__(self) -> None:
            self.ready = False
            self.readiness_code = "artifact_validation_failed"
            self.readiness_failure_category = "artifact_validation_error"
            self.forecast_artifact: dict[str, object] = {}
            self.history: list[object] = []

    events: list[tuple[str, dict[str, object]]] = []

    def capture(event: str, **context: object) -> None:
        events.append((event, context))

    monkeypatch.setattr(api_main, "ForecastService", UnreadyService)
    monkeypatch.setattr(api_main, "emit_event", capture)

    with TestClient(app) as client:
        response = client.get("/ready")

    readiness_event = next(
        context for event, context in events if event == "api_readiness_failed"
    )
    assert response.status_code == 503
    assert response.json() == {
        "ready": False,
        "code": "artifact_validation_failed",
    }
    assert readiness_event["failure_category"] == "artifact_validation_error"
    assert readiness_event["readiness_code"] == "artifact_validation_failed"
    assert readiness_event["route"] == "/ready"
