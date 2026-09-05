"""Download, verify, and safely extract a pinned CO2 serving bundle."""

from __future__ import annotations

import hashlib
import os
import shutil
import tarfile
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Callable

from src.artifacts import ArtifactValidationError, validate_manifest
from src.utils.config import PROJECT_ROOT


class BundleInstallError(ValueError):
    """Raised when a serving bundle cannot be installed safely."""


MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
MAX_EXTRACTED_BYTES = 50 * 1024 * 1024
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_MEMBER_COUNT = 128
DOWNLOAD_TIMEOUT_SECONDS = 30
CHUNK_SIZE = 1024 * 1024
SHA256_LENGTH = 64

BUNDLE_URL_ENV = "CO2_SERVING_BUNDLE_URL"
BUNDLE_SHA_ENV = "CO2_SERVING_BUNDLE_SHA256"
BUNDLE_CACHE_ROOT = Path(tempfile.gettempdir()) / "co2-serving-bundles"

_CACHE_LOCK = threading.Lock()
_RESOLVED_ROOTS: dict[tuple[str, str], Path] = {}
Urlopen = Callable[..., object]


def _validate_configuration(url: str, expected_sha256: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise BundleInstallError("Serving bundle URL must use HTTPS.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise BundleInstallError(
            "Serving bundle URL must not contain credentials or query data."
        )
    if len(expected_sha256) != SHA256_LENGTH or any(
        character not in "0123456789abcdefABCDEF" for character in expected_sha256
    ):
        raise BundleInstallError(
            "Serving bundle SHA-256 must be a 64-character hex digest."
        )


def _download(url: str, destination: Path, opener: Urlopen) -> str:
    digest = hashlib.sha256()
    total = 0
    request = urllib.request.Request(
        url, headers={"User-Agent": "co2-forecast-serving/1"}
    )
    try:
        with opener(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:  # type: ignore[union-attr]
            with destination.open("wb") as output:
                while True:
                    chunk = response.read(CHUNK_SIZE)  # type: ignore[union-attr]
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_ARCHIVE_BYTES:
                        raise BundleInstallError(
                            "Serving bundle exceeds the archive size limit."
                        )
                    digest.update(chunk)
                    output.write(chunk)
    except BundleInstallError:
        raise
    except (OSError, urllib.error.URLError) as exc:
        raise BundleInstallError("Serving bundle download failed.") from exc
    return digest.hexdigest()


def _safe_member_name(name: str) -> PurePosixPath:
    if not name or "\\" in name:
        raise BundleInstallError("Serving bundle contains an unsafe archive path.")
    path = PurePosixPath(name)
    if (
        not path.parts
        or path.is_absolute()
        or ".." in path.parts
        or path.parts[0].endswith(":")
    ):
        raise BundleInstallError("Serving bundle contains an unsafe archive path.")
    return path


def _safe_extract(archive_path: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    seen: set[str] = set()
    total_bytes = 0
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            members = archive.getmembers()
            if len(members) > MAX_MEMBER_COUNT:
                raise BundleInstallError("Serving bundle contains too many files.")
            for member in members:
                relative = _safe_member_name(member.name)
                archive_name = relative.as_posix()
                if archive_name in seen:
                    raise BundleInstallError(
                        "Serving bundle contains duplicate archive paths."
                    )
                seen.add(archive_name)
                if member.isdir():
                    member_size = 0
                elif member.isreg():
                    member_size = member.size
                    if member_size > MAX_FILE_BYTES:
                        raise BundleInstallError(
                            "Serving bundle contains an oversized file."
                        )
                    total_bytes += member_size
                    if total_bytes > MAX_EXTRACTED_BYTES:
                        raise BundleInstallError(
                            "Serving bundle exceeds the extracted size limit."
                        )
                else:
                    raise BundleInstallError(
                        "Serving bundle contains an unsafe archive member."
                    )

                target = (destination / Path(*relative.parts)).resolve()
                if (
                    target != destination_resolved
                    and destination_resolved not in target.parents
                ):
                    raise BundleInstallError(
                        "Serving bundle contains an escaping archive path."
                    )
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise BundleInstallError("Serving bundle file could not be read.")
                with source, target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=CHUNK_SIZE)
                os.chmod(target, 0o644)
    except BundleInstallError:
        raise
    except (OSError, tarfile.TarError) as exc:
        raise BundleInstallError("Serving bundle extraction failed.") from exc


def _validate_extracted_bundle(root: Path) -> None:
    try:
        validate_manifest(root / "reports" / "model_manifest.json", root=root)
    except (ArtifactValidationError, OSError) as exc:
        raise BundleInstallError("Serving bundle manifest validation failed.") from exc


def extract_and_validate_bundle(archive_path: Path, destination: Path) -> Path:
    """Safely extract an archive into a new directory and validate its manifest."""

    resolved_destination = destination.resolve()
    if resolved_destination.exists():
        raise BundleInstallError(
            "Serving bundle extraction destination already exists."
        )
    resolved_destination.mkdir(parents=True)
    try:
        _safe_extract(archive_path, resolved_destination)
        _validate_extracted_bundle(resolved_destination)
    except BundleInstallError:
        shutil.rmtree(resolved_destination, ignore_errors=True)
        raise
    return resolved_destination


def _cached_root(cache_root: Path, digest: str) -> Path:
    resolved_cache_root = cache_root.resolve()
    resolved_cache_root.mkdir(parents=True, exist_ok=True)
    cache_dir = resolved_cache_root / digest
    if cache_dir.is_symlink():
        raise BundleInstallError("Serving bundle cache path is unsafe.")
    if cache_dir.exists():
        _validate_extracted_bundle(cache_dir)
        return cache_dir
    return cache_dir


def install_serving_bundle(
    url: str,
    expected_sha256: str,
    cache_root: Path,
    *,
    opener: Urlopen | None = None,
) -> Path:
    """Install a verified bundle once and return its extracted repository root."""

    _validate_configuration(url, expected_sha256)
    digest = expected_sha256.lower()
    resolved_cache_root = cache_root.resolve()
    resolved_cache_root.mkdir(parents=True, exist_ok=True)
    cache_dir = _cached_root(resolved_cache_root, digest)
    if cache_dir.exists():
        return cache_dir

    temporary_archive: Path | None = None
    temporary_root = Path(
        tempfile.mkdtemp(prefix=f"co2-serving-{digest[:12]}-", dir=resolved_cache_root)
    )
    try:
        with tempfile.NamedTemporaryFile(
            dir=resolved_cache_root, delete=False
        ) as handle:
            temporary_archive = Path(handle.name)
        actual_digest = _download(
            url, temporary_archive, opener or urllib.request.urlopen
        )
        if actual_digest != digest:
            raise BundleInstallError("Serving bundle checksum mismatch.")
        _safe_extract(temporary_archive, temporary_root)
        _validate_extracted_bundle(temporary_root)
        os.replace(temporary_root, cache_dir)
        return cache_dir
    except BundleInstallError:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise
    except OSError as exc:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise BundleInstallError("Serving bundle cache installation failed.") from exc
    finally:
        if temporary_archive is not None:
            temporary_archive.unlink(missing_ok=True)


def resolve_serving_root() -> Path:
    """Resolve the local root or a process-cached explicitly pinned bundle."""

    url = os.getenv(BUNDLE_URL_ENV)
    expected_sha256 = os.getenv(BUNDLE_SHA_ENV)
    if not url and not expected_sha256:
        return PROJECT_ROOT
    if not url or not expected_sha256:
        raise BundleInstallError(
            f"{BUNDLE_URL_ENV} and {BUNDLE_SHA_ENV} must be configured together."
        )
    key = (url, expected_sha256.lower())
    with _CACHE_LOCK:
        cached = _RESOLVED_ROOTS.get(key)
        if cached is not None:
            _validate_extracted_bundle(cached)
            return cached
        root = install_serving_bundle(url, expected_sha256, BUNDLE_CACHE_ROOT)
        _RESOLVED_ROOTS[key] = root
        return root
