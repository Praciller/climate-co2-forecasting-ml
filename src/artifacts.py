from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.utils.config import ARTIFACT_SCHEMA_VERSION, PROJECT_ROOT


class ArtifactValidationError(ValueError):
    """Raised when a governed artifact is missing, unsafe, or mismatched."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_relative(path: Path, root: Path = PROJECT_ROOT) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ArtifactValidationError("Artifact path is outside the repository.")
    return resolved_path.relative_to(resolved_root).as_posix()


def artifact_entry(path: Path, root: Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.is_file():
        raise ArtifactValidationError(f"Required artifact is missing: {path.name}")
    return {
        "path": repository_relative(path, root),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def write_manifest(
    path: Path,
    metadata: dict[str, Any],
    artifact_paths: dict[str, Path],
    *,
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    payload = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        **metadata,
        "artifacts": {
            name: artifact_entry(artifact_path, root)
            for name, artifact_path in artifact_paths.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return payload


def refresh_manifest_artifact(
    manifest_path: Path,
    name: str,
    artifact_path: Path,
    *,
    root: Path = PROJECT_ROOT,
) -> None:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload.setdefault("artifacts", {})[name] = artifact_entry(artifact_path, root)
    manifest_path.write_text(
        json.dumps(payload, indent=2, default=str),
        encoding="utf-8",
    )


def validate_manifest(
    manifest_path: Path,
    *,
    root: Path = PROJECT_ROOT,
    required_artifacts: set[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Path]]:
    if not manifest_path.is_file():
        raise ArtifactValidationError("Model artifact manifest is missing.")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ArtifactValidationError("Model artifact manifest is invalid.") from exc
    if payload.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
        raise ArtifactValidationError("Model artifact manifest version is incompatible.")

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ArtifactValidationError("Model artifact manifest has no artifact map.")
    required = required_artifacts or set()
    missing = required.difference(artifacts)
    if missing:
        raise ArtifactValidationError(
            f"Model artifact manifest is incomplete: {', '.join(sorted(missing))}"
        )

    resolved_root = root.resolve()
    resolved: dict[str, Path] = {}
    for name, entry in artifacts.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ArtifactValidationError(f"Artifact entry is invalid: {name}")
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ArtifactValidationError(f"Artifact path is unsafe: {name}")
        artifact_path = (resolved_root / relative).resolve()
        if (
            artifact_path != resolved_root
            and resolved_root not in artifact_path.parents
        ):
            raise ArtifactValidationError(f"Artifact path escapes repository: {name}")
        if not artifact_path.is_file():
            raise ArtifactValidationError(f"Artifact is missing: {name}")
        if sha256_file(artifact_path) != entry.get("sha256"):
            raise ArtifactValidationError(f"Artifact checksum mismatch: {name}")
        resolved[name] = artifact_path
    return payload, resolved
