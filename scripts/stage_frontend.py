"""Stage only the built Vite frontend for the Vercel Python function."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "frontend" / "dist"
DEFAULT_TARGET = ROOT / "api" / "frontend_dist"
FORBIDDEN_PARTS = frozenset(
    {"node_modules", "src", "tests", "data", "models", "notebooks"}
)


class FrontendStageError(RuntimeError):
    """Raised when the frontend build output is missing or unsafe to stage."""


def _validate_source(source: Path) -> list[Path]:
    if not source.exists():
        raise FrontendStageError(f"Frontend build output does not exist: {source}")
    if not source.is_dir() or source.is_symlink():
        raise FrontendStageError("Frontend build output is not a directory.")
    if not (source / "index.html").is_file():
        raise FrontendStageError("Frontend build output must contain index.html.")

    entries = sorted(source.rglob("*"))
    for entry in entries:
        relative = entry.relative_to(source)
        if entry.is_symlink() or any(part in FORBIDDEN_PARTS for part in relative.parts):
            raise FrontendStageError(
                "Staging accepts only built frontend assets; found a forbidden path: "
                f"{relative.as_posix()}"
            )
        if not entry.is_file() and not entry.is_dir():
            raise FrontendStageError(f"Unsupported frontend build entry: {relative}")
    return entries


def _paths_overlap(source: Path, target: Path) -> bool:
    return source == target or source.is_relative_to(target) or target.is_relative_to(source)


def stage_frontend(
    source: Path = DEFAULT_SOURCE,
    target: Path = DEFAULT_TARGET,
) -> Path:
    """Copy validated build output into the function-visible staging directory."""

    source = source.resolve()
    target = target.resolve()
    entries = _validate_source(source)
    if _paths_overlap(source, target):
        raise FrontendStageError("Frontend source and staging directories must not overlap.")
    if target.exists() and (target.is_symlink() or not target.is_dir()):
        raise FrontendStageError("Frontend staging target must be a directory.")

    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for entry in entries:
        relative = entry.relative_to(source)
        destination = target / relative
        if entry.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(entry, destination)
    return target


if __name__ == "__main__":
    staged = stage_frontend()
    print(f"Staged frontend assets at {staged}")
