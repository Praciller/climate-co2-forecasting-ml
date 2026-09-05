from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path

import pytest

from scripts.package_serving_bundle import BundlePackagingError, package_bundle
from src.artifacts import ArtifactValidationError, sha256_file, write_manifest

ARTIFACTS = {
    "raw_data": "data/raw/co2_raw.csv",
    "monthly_data": "data/processed/co2_monthly.csv",
    "feature_data": "data/processed/co2_features.csv",
    "forecast_metrics": "reports/forecast_metrics.json",
    "interval_report": "reports/interval_report.json",
    "residual_report": "reports/residual_report.json",
    "live_forecast": "reports/live_forecast.json",
    "anomalies": "reports/anomalies.csv",
}


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    for relative_path in ARTIFACTS.values():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture:{relative_path}\n", encoding="utf-8")
    write_manifest(
        root / "reports" / "model_manifest.json",
        {
            "generated_at": "2026-09-05T00:00:00+00:00",
            "code_commit": "abc123",
            "runtime": {"python": "3.11.16"},
        },
        {name: root / path for name, path in ARTIFACTS.items()},
        root=root,
    )
    return root


def test_valid_manifest_packages_all_artifacts_with_repository_paths(
    tmp_path: Path,
) -> None:
    root = _fixture_root(tmp_path)
    result = package_bundle(
        root,
        tmp_path / "co2-serving-bundle.tar.gz",
        metadata_path=tmp_path / "co2-serving-bundle.metadata.json",
        source_commit="abc123",
        environment_label="test-fixture",
    )

    assert result.archive_path.is_file()
    assert result.sha256 == sha256_file(result.archive_path)
    assert set(result.member_names) == {
        "reports/model_manifest.json",
        *ARTIFACTS.values(),
    }
    with tarfile.open(result.archive_path, "r:gz") as archive:
        assert archive.getnames() == sorted(result.member_names)
        assert all(
            member.uid == 0 and member.gid == 0 for member in archive.getmembers()
        )
        assert all(member.mtime == 0 for member in archive.getmembers())

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata == {
        "schema_version": "1.0.0",
        "source_commit": "abc123",
        "manifest_sha256": hashlib.sha256(
            (root / "reports" / "model_manifest.json").read_bytes()
        ).hexdigest(),
        "artifact_count": len(ARTIFACTS),
        "generation_environment": "test-fixture",
    }
    assert len(result.metadata_path.read_bytes()) < 1024


def test_extracted_bundle_can_revalidate_against_manifest(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    result = package_bundle(root, tmp_path / "bundle.tar.gz")
    extracted = tmp_path / "extracted"
    extracted.mkdir()

    with tarfile.open(result.archive_path, "r:gz") as archive:
        archive.extractall(extracted)

    from src.artifacts import validate_manifest

    _manifest, resolved = validate_manifest(
        extracted / "reports" / "model_manifest.json",
        root=extracted,
    )
    assert set(resolved) == set(ARTIFACTS)


def test_unreferenced_model_binaries_are_not_added(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    models = root / "models"
    models.mkdir()
    (models / "not-referenced.joblib").write_bytes(b"not part of the manifest")
    (models / "not-referenced.pt").write_bytes(b"not part of the manifest")

    result = package_bundle(root, tmp_path / "bundle.tar.gz")

    assert not any(name.startswith("models/") for name in result.member_names)


def test_missing_manifest_artifact_is_rejected(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    (root / ARTIFACTS["anomalies"]).unlink()

    with pytest.raises(ArtifactValidationError, match="Artifact is missing: anomalies"):
        package_bundle(root, tmp_path / "bundle.tar.gz")


def test_unsafe_manifest_path_is_rejected(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    manifest = root / "reports" / "model_manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["artifacts"]["raw_data"]["path"] = "../outside.csv"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ArtifactValidationError, match="unsafe"):
        package_bundle(root, tmp_path / "bundle.tar.gz")


def test_archive_order_and_bytes_are_deterministic(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    first = package_bundle(root, tmp_path / "first.tar.gz")
    second = package_bundle(root, tmp_path / "second.tar.gz")

    assert first.member_names == second.member_names
    assert first.archive_path.read_bytes() == second.archive_path.read_bytes()
    assert first.sha256 == second.sha256


def test_output_path_inside_repository_is_rejected(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)

    with pytest.raises(BundlePackagingError, match="outside the repository"):
        package_bundle(root, root / "bundle.tar.gz")
