import json
from pathlib import Path

import pytest

from src.artifacts import (
    ArtifactValidationError,
    validate_manifest,
    write_manifest,
)


def test_manifest_rejects_checksum_mismatch(tmp_path: Path) -> None:
    artifact = tmp_path / "reports" / "live_forecast.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text('{"ok": true}', encoding="utf-8")
    manifest = artifact.parent / "model_manifest.json"
    write_manifest(
        manifest,
        {"generated_at": "2026-07-23T00:00:00Z"},
        {"live_forecast": artifact},
        root=tmp_path,
    )
    artifact.write_text('{"ok": false}', encoding="utf-8")

    with pytest.raises(ArtifactValidationError, match="checksum mismatch"):
        validate_manifest(
            manifest,
            root=tmp_path,
            required_artifacts={"live_forecast"},
        )


def test_manifest_rejects_path_escape(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    manifest = reports / "model_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "2.0.0",
                "artifacts": {
                    "live_forecast": {
                        "path": "../outside.json",
                        "sha256": "invalid",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ArtifactValidationError, match="unsafe"):
        validate_manifest(
            manifest,
            root=tmp_path,
            required_artifacts={"live_forecast"},
        )
