"""Build a deterministic, manifest-complete archive for API serving."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

from src.artifacts import validate_manifest


class BundlePackagingError(ValueError):
    """Raised when a serving bundle cannot be created safely."""


MAX_METADATA_STRING = 128
METADATA_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class BundleResult:
    archive_path: Path
    sha256: str
    member_names: tuple[str, ...]
    metadata_path: Path | None = None
    sha_path: Path | None = None


def _ensure_output_outside_root(output: Path, root: Path) -> Path:
    resolved = output.resolve()
    if resolved == root or root in resolved.parents:
        raise BundlePackagingError("Bundle output must be outside the repository.")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def _bounded_string(value: str, field: str) -> str:
    if len(value) > MAX_METADATA_STRING:
        raise BundlePackagingError(f"Bundle metadata field is too long: {field}")
    return value


def _relative_archive_name(path: Path, root: Path) -> str:
    try:
        relative = path.resolve().relative_to(root)
    except ValueError as exc:
        raise BundlePackagingError(
            "Manifest artifact is outside the repository."
        ) from exc
    name = PurePosixPath(relative.as_posix())
    if name.is_absolute() or ".." in name.parts or not name.parts:
        raise BundlePackagingError("Manifest artifact path is unsafe.")
    return name.as_posix()


def _archive_members(
    root: Path, resolved_paths: dict[str, Path], manifest: Path
) -> list[tuple[str, Path]]:
    members = {_relative_archive_name(manifest, root): manifest}
    for path in resolved_paths.values():
        name = _relative_archive_name(path, root)
        members[name] = path
    return sorted(members.items())


def _write_member(archive: tarfile.TarFile, name: str, path: Path) -> None:
    data = path.read_bytes()
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, fileobj=_BytesReader(data))


class _BytesReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._offset = 0

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self._data) - self._offset
        start = self._offset
        self._offset = min(len(self._data), self._offset + size)
        return self._data[start : self._offset]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
    os.replace(temporary, path)


def package_bundle(
    root: Path,
    output_archive: Path,
    *,
    metadata_path: Path | None = None,
    sha_path: Path | None = None,
    source_commit: str | None = None,
    environment_label: str = "unknown",
) -> BundleResult:
    """Package every artifact referenced by the complete model manifest."""

    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        raise BundlePackagingError("Repository root does not exist.")
    manifest_path = resolved_root / "reports" / "model_manifest.json"
    manifest_bytes = manifest_path.read_bytes() if manifest_path.is_file() else b""
    manifest, resolved_paths = validate_manifest(manifest_path, root=resolved_root)
    if not manifest_bytes:
        raise BundlePackagingError("Model manifest is empty.")

    archive_path = _ensure_output_outside_root(output_archive, resolved_root)
    metadata_resolved = (
        None
        if metadata_path is None
        else _ensure_output_outside_root(metadata_path, resolved_root)
    )
    sha_resolved = (
        None
        if sha_path is None
        else _ensure_output_outside_root(sha_path, resolved_root)
    )
    members = _archive_members(resolved_root, resolved_paths, manifest_path)

    with tempfile.NamedTemporaryFile(dir=archive_path.parent, delete=False) as handle:
        temporary_archive = Path(handle.name)
    try:
        with temporary_archive.open("wb") as raw_handle:
            with gzip.GzipFile(
                filename="",
                fileobj=raw_handle,
                mode="wb",
                mtime=0,
            ) as gzip_handle:
                with tarfile.open(
                    fileobj=gzip_handle,
                    mode="w",
                    format=tarfile.USTAR_FORMAT,
                ) as archive:
                    for name, path in members:
                        _write_member(archive, name, path)
        os.replace(temporary_archive, archive_path)
    except BaseException:
        temporary_archive.unlink(missing_ok=True)
        raise

    archive_sha256 = _sha256(archive_path)
    if sha_resolved is not None:
        _atomic_write(
            sha_resolved,
            f"{archive_sha256}  {archive_path.name}\n".encode("ascii"),
        )

    if metadata_resolved is not None:
        metadata = {
            "schema_version": METADATA_SCHEMA_VERSION,
            "source_commit": _bounded_string(
                source_commit or "unknown", "source_commit"
            ),
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "artifact_count": len(resolved_paths),
            "generation_environment": _bounded_string(
                environment_label,
                "generation_environment",
            ),
        }
        _atomic_write(
            metadata_resolved,
            (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )

    return BundleResult(
        archive_path=archive_path,
        sha256=archive_sha256,
        member_names=tuple(name for name, _path in members),
        metadata_path=metadata_resolved,
        sha_path=sha_resolved,
    )


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--sha-file", type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--environment-label", default="canonical-linux-py311")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    result = package_bundle(
        args.root,
        args.output,
        metadata_path=args.metadata,
        sha_path=args.sha_file,
        source_commit=args.source_commit,
        environment_label=args.environment_label,
    )
    print(
        json.dumps(
            {
                "archive": str(result.archive_path),
                "sha256": result.sha256,
                "artifact_count": len(result.member_names) - 1,
                "members": list(result.member_names),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
