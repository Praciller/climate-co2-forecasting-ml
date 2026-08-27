from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

from src.artifacts import validate_manifest
from src.utils.config import MODEL_MANIFEST_PATH, PROJECT_ROOT

FORBIDDEN_TRACKED_PARTS = {
    ".env",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    ".ipynb_checkpoints",
}
FORBIDDEN_TEXT_PATTERNS = {
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    "macOS user path": re.compile("/" + r"Users/"),
    "Linux home path": re.compile("/" + r"home/[^/\s]+/"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".ipynb",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=PROJECT_ROOT,
    )
    return [
        PROJECT_ROOT / item.decode("utf-8")
        for item in output.split(b"\0")
        if item
    ]


def validate_tracked_paths(paths: list[Path]) -> list[str]:
    issues = []
    for path in paths:
        relative = path.relative_to(PROJECT_ROOT)
        parts = set(relative.parts)
        forbidden = parts.intersection(FORBIDDEN_TRACKED_PARTS)
        if forbidden and relative.as_posix() != ".env.example":
            issues.append(f"forbidden tracked path: {relative.as_posix()}")
        if relative.suffix == ".ipynb" and relative.name.endswith(".executed.ipynb"):
            issues.append(f"executed notebook is tracked: {relative.as_posix()}")
    return issues


def validate_text(paths: list[Path]) -> list[str]:
    issues = []
    for path in paths:
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in FORBIDDEN_TEXT_PATTERNS.items():
            if pattern.search(text):
                issues.append(
                    f"{label} in {path.relative_to(PROJECT_ROOT).as_posix()}"
                )
    return issues


def validate_markdown_links(paths: list[Path]) -> list[str]:
    issues = []
    link_pattern = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
    for path in paths:
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue
            local = unquote(target.split("#", 1)[0])
            resolved = (path.parent / local).resolve()
            if not resolved.exists():
                issues.append(
                    f"broken Markdown link in "
                    f"{path.relative_to(PROJECT_ROOT).as_posix()}: {target}"
                )
    return issues


def main() -> None:
    paths = tracked_files()
    issues = [
        *validate_tracked_paths(paths),
        *validate_text(paths),
        *validate_markdown_links(paths),
    ]
    validate_manifest(
        MODEL_MANIFEST_PATH,
        required_artifacts={
            "raw_data",
            "monthly_data",
            "feature_data",
            "forecast_metrics",
            "interval_report",
            "residual_report",
            "live_forecast",
            "anomalies",
        },
    )
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"Repository guardrails passed for {len(paths)} tracked files.")


if __name__ == "__main__":
    main()
