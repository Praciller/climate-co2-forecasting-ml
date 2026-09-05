from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_serving_bundle_workflow_is_manual_read_only_and_main_only() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "serving-bundle.yml"
    source = workflow_path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(source)
    trigger = workflow.get("on", workflow.get(True))
    assert list(trigger) == ["workflow_dispatch"]
    assert workflow["permissions"] == {"contents": "read"}
    job = next(iter(workflow["jobs"].values()))
    assert job["runs-on"] == "ubuntu-24.04"
    steps_text = "\n".join(step.get("run", "") for step in job["steps"])
    assert "github.ref" in steps_text
    assert "refs/heads/main" in steps_text
    for command in (
        "python -m src.pipeline",
        "python scripts/verify_generated_evidence.py",
        "python -m src.verify_repository",
        "python -m scripts.package_serving_bundle",
        "ForecastService",
        "actions/upload-artifact@v4",
    ):
        assert command in source
    assert "python scripts/package_serving_bundle.py" not in source
    assert "contents: write" not in source
    assert "vercel" not in source.lower()
    assert "release" not in source.lower()
