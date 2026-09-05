from __future__ import annotations

import hashlib
import io
import tarfile
from pathlib import Path
from typing import Self

import pytest

import scripts.install_serving_bundle as installer
from scripts.install_serving_bundle import (
    BundleInstallError,
    extract_and_validate_bundle,
    install_serving_bundle,
)
from scripts.package_serving_bundle import package_bundle
from src.utils.config import PROJECT_ROOT


class _Response(io.BytesIO):
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def _archive(tmp_path: Path) -> tuple[Path, str]:
    source = tmp_path / "source"
    reports = source / "reports"
    reports.mkdir(parents=True)
    artifact = reports / "live_forecast.json"
    artifact.write_text('{"forecast": []}\n', encoding="utf-8")
    (reports / "model_manifest.json").write_text(
        '{"schema_version":"2.0.0","artifacts":{"live_forecast":'
        '{"path":"reports/live_forecast.json","sha256":"'
        + hashlib.sha256(artifact.read_bytes()).hexdigest()
        + '"}}}',
        encoding="utf-8",
    )
    archive = tmp_path / "bundle.tar.gz"
    result = package_bundle(source, archive)
    return archive, result.sha256


def test_pinned_https_bundle_downloads_verifies_and_caches(tmp_path: Path) -> None:
    archive, digest = _archive(tmp_path)
    calls = 0

    def opener(_request, timeout: int):
        nonlocal calls
        calls += 1
        assert timeout > 0
        return _Response(archive.read_bytes())

    installed = install_serving_bundle(
        "https://example.test/releases/co2-serving-bundle.tar.gz",
        digest,
        tmp_path / "cache",
        opener=opener,
    )
    cached = install_serving_bundle(
        "https://example.test/releases/co2-serving-bundle.tar.gz",
        digest,
        tmp_path / "cache",
        opener=lambda *_args, **_kwargs: pytest.fail("cache should prevent a download"),
    )

    assert installed == cached
    assert (installed / "reports" / "model_manifest.json").is_file()
    assert calls == 1


def test_tampered_archive_fails_before_extraction(tmp_path: Path) -> None:
    archive, digest = _archive(tmp_path)
    tampered = tmp_path / "tampered.tar.gz"
    tampered.write_bytes(archive.read_bytes() + b"tampered")

    with pytest.raises(BundleInstallError, match="checksum mismatch"):
        install_serving_bundle(
            "https://example.test/releases/co2-serving-bundle.tar.gz",
            digest,
            tmp_path / "cache",
            opener=lambda *_args, **_kwargs: _Response(tampered.read_bytes()),
        )
    assert not (tmp_path / "cache" / digest).exists()


def test_rejects_non_https_and_invalid_digest(tmp_path: Path) -> None:
    for url in (
        "http://example.test/bundle.tar.gz",
        "https://user:pass@example.test/bundle.tar.gz",
        "https://example.test/bundle.tar.gz?token=secret",
    ):
        with pytest.raises(BundleInstallError, match="HTTPS|credentials"):
            install_serving_bundle(url, "a" * 64, tmp_path / "cache")

    with pytest.raises(BundleInstallError, match="SHA-256"):
        install_serving_bundle(
            "https://example.test/bundle.tar.gz",
            "not-a-sha",
            tmp_path / "cache",
        )


def test_rejects_path_traversal_and_links(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        traversal = tarfile.TarInfo("../escaped.txt")
        traversal.size = 1
        output.addfile(traversal, io.BytesIO(b"x"))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()

    with pytest.raises(BundleInstallError, match="unsafe archive path"):
        install_serving_bundle(
            "https://example.test/bundle.tar.gz",
            digest,
            tmp_path / "cache",
            opener=lambda *_args, **_kwargs: _Response(archive.read_bytes()),
        )


def test_extract_and_validate_rejects_tampered_manifest_artifact(
    tmp_path: Path,
) -> None:
    archive, _digest = _archive(tmp_path)
    tampered = tmp_path / "tampered-manifest-artifact.tar.gz"
    with (
        tarfile.open(archive, "r:gz") as source,
        tarfile.open(tampered, "w:gz") as output,
    ):
        for member in source.getmembers():
            data = source.extractfile(member).read() if member.isfile() else None
            if member.name == "reports/live_forecast.json":
                data = b'{"forecast": ["tampered"]}\n'
                member.size = len(data)
            output.addfile(member, io.BytesIO(data) if data is not None else None)

    with pytest.raises(BundleInstallError, match="manifest validation"):
        extract_and_validate_bundle(tampered, tmp_path / "tampered-extracted")


def test_default_root_is_local_project_and_explicit_root_is_used(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("CO2_SERVING_BUNDLE_URL", raising=False)
    monkeypatch.delenv("CO2_SERVING_BUNDLE_SHA256", raising=False)
    assert installer.resolve_serving_root() == PROJECT_ROOT

    explicit_root = tmp_path / "bundle"
    explicit_root.mkdir()
    monkeypatch.setenv("CO2_SERVING_BUNDLE_URL", "https://example.test/bundle.tar.gz")
    monkeypatch.setenv("CO2_SERVING_BUNDLE_SHA256", "a" * 64)
    monkeypatch.setattr(
        installer, "install_serving_bundle", lambda *_args, **_kwargs: explicit_root
    )
    assert installer.resolve_serving_root() == explicit_root


def test_invalid_deployment_root_returns_not_ready_service(
    monkeypatch,
    tmp_path: Path,
) -> None:
    import src.api.main as api_main

    monkeypatch.setattr(api_main, "resolve_serving_root", lambda: tmp_path)
    service = api_main.create_forecast_service()

    assert service.ready is False
    assert service.readiness_code == "artifact_validation_failed"
