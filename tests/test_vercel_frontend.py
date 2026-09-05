from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import src.api.main as api_main
from api.index import create_app
from tests.test_deployment_api import _runtime_fixture


def test_frontend_root_and_assets_are_served_after_api_mount(
    monkeypatch,
    tmp_path: Path,
) -> None:
    frontend = tmp_path / "frontend_dist"
    (frontend / "assets").mkdir(parents=True)
    (frontend / "index.html").write_text(
        '<!doctype html><html><body>CO2 dashboard</body></html>\n',
        encoding="utf-8",
    )
    (frontend / "assets" / "app.js").write_text("console.log('dashboard')\n", encoding="utf-8")
    monkeypatch.setattr(
        api_main, "resolve_serving_root", lambda: _runtime_fixture(tmp_path)
    )

    app = create_app(frontend_directory=frontend)
    with TestClient(app) as client:
        root = client.get("/", headers={"accept": "text/html"})
        asset = client.get("/assets/app.js")
        deep_link = client.get("/model-evaluation", headers={"accept": "text/html"})
        api_health = client.get("/api/health")
        api_missing = client.get("/api/not-a-route")

    assert root.status_code == 200
    assert "text/html" in root.headers["content-type"]
    assert "CO2 dashboard" in root.text
    assert asset.status_code == 200
    assert "console.log" in asset.text
    assert deep_link.status_code == 200
    assert "CO2 dashboard" in deep_link.text
    assert api_health.status_code == 200
    assert api_health.json()["status"] == "ok"
    assert api_missing.status_code == 404
    assert api_missing.json() == {"detail": "Not Found"}
