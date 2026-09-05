"""Compare regenerated reviewer evidence with the committed HEAD baseline."""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VERIFICATION_DOC = REPOSITORY_ROOT / "docs" / "verification.md"
TRACKED_MARKER = "TRACKED_GENERATED_REVIEWER_EVIDENCE"
RUNTIME_MARKER = "RUNTIME_ONLY_GENERATED"
VOLATILE_PATH = "reports/live_forecast.json"
VOLATILE_FIELD = "generated_at"


class EvidencePolicyError(ValueError):
    """Raised when the documented generated-evidence policy is malformed."""


@dataclass(frozen=True)
class ArtifactPolicy:
    tracked_patterns: tuple[str, ...]
    runtime_patterns: tuple[str, ...]


def _patterns_between(markdown: str, start: str, end: str) -> tuple[str, ...]:
    lines = markdown.splitlines()
    start_marker = f"`{start}`:"
    end_marker = f"`{end}`:"
    try:
        start_index = lines.index(start_marker)
        end_index = lines.index(end_marker)
    except ValueError as exc:
        raise EvidencePolicyError(
            f"Generated-evidence policy markers are incomplete: {start}, {end}"
        ) from exc
    patterns = []
    for line in lines[start_index + 1 : end_index]:
        match = re.fullmatch(r"- `([^`]+)`(?:.*)", line.strip())
        if match:
            patterns.append(match.group(1))
    if not patterns:
        raise EvidencePolicyError(f"No patterns documented under {start}.")
    return tuple(patterns)


def parse_artifact_policy(markdown: str) -> ArtifactPolicy:
    """Read the two generated-artifact lists from docs/verification.md."""

    return ArtifactPolicy(
        tracked_patterns=_patterns_between(markdown, TRACKED_MARKER, RUNTIME_MARKER),
        runtime_patterns=_patterns_between(markdown, RUNTIME_MARKER, "MANIFEST_POLICY"),
    )


def _expand_braces(pattern: str) -> tuple[str, ...]:
    match = re.search(r"\{([^{}]+)\}", pattern)
    if not match:
        return (pattern,)
    prefix, suffix = pattern[: match.start()], pattern[match.end() :]
    return tuple(
        expanded
        for option in match.group(1).split(",")
        for expanded in _expand_braces(prefix + option + suffix)
    )


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern) or PurePosixPath(path).match(pattern)


def select_policy_paths(
    tracked_paths: list[str], policy: ArtifactPolicy
) -> list[str]:
    """Select only tracked files covered by the documented reviewer policy."""

    expanded = tuple(
        expanded_pattern
        for pattern in policy.tracked_patterns
        for expanded_pattern in _expand_braces(pattern)
    )
    runtime = tuple(
        expanded_pattern
        for pattern in policy.runtime_patterns
        for expanded_pattern in _expand_braces(pattern)
    )
    return sorted(
        path
        for path in tracked_paths
        if any(_matches(path, pattern) for pattern in expanded)
        and not any(_matches(path, pattern) for pattern in runtime)
    )


def _normalized_live_forecast(raw: bytes, relative_path: str) -> object:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidencePolicyError(f"{relative_path} is not valid UTF-8 JSON.") from exc
    if not isinstance(payload, dict) or VOLATILE_FIELD not in payload:
        raise EvidencePolicyError(
            f"{relative_path} must contain the documented {VOLATILE_FIELD} field."
        )
    payload.pop(VOLATILE_FIELD)
    return payload


def compare_content(relative_path: str, current: bytes, expected: bytes) -> bool:
    """Compare one policy-defined artifact, normalizing one known field only."""

    if relative_path == VOLATILE_PATH:
        return _normalized_live_forecast(
            current, relative_path
        ) == _normalized_live_forecast(expected, relative_path)
    return current == expected


def _git_output(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=REPOSITORY_ROOT)


def _head_content(relative_path: str) -> bytes:
    # Apply the repository's checkout filters so Windows CRLF worktrees compare
    # against the same checked-out baseline as Linux LF worktrees.
    return _git_output("cat-file", "--filters", f"HEAD:{relative_path}")


def verify_generated_evidence() -> list[str]:
    """Return readable drift diagnostics, or an empty list when evidence is clean."""

    policy = parse_artifact_policy(VERIFICATION_DOC.read_text(encoding="utf-8"))
    tracked_paths = [
        item.decode("utf-8")
        for item in _git_output("ls-files", "-z", "--cached").split(b"\0")
        if item
    ]
    policy_paths = select_policy_paths(tracked_paths, policy)
    diagnostics = []
    for relative_path in policy_paths:
        current_path = REPOSITORY_ROOT / Path(*PurePosixPath(relative_path).parts)
        if not current_path.is_file():
            diagnostics.append(f"{relative_path}: regenerated file is missing")
            continue
        try:
            expected = _head_content(relative_path)
            matches = compare_content(relative_path, current_path.read_bytes(), expected)
        except (EvidencePolicyError, subprocess.CalledProcessError) as exc:
            diagnostics.append(f"{relative_path}: {exc}")
            continue
        if not matches:
            if relative_path == VOLATILE_PATH:
                reason = (
                    "substantive JSON differs after normalizing only "
                    f"{VOLATILE_FIELD}"
                )
            else:
                reason = "content differs from committed HEAD"
            diagnostics.append(f"{relative_path}: {reason}")
    return diagnostics


def main() -> int:
    diagnostics = verify_generated_evidence()
    if diagnostics:
        print("Governed evidence drift detected:")
        print("\n".join(f"- {diagnostic}" for diagnostic in diagnostics))
        return 1
    print("Governed tracked evidence matches committed HEAD (volatile metadata normalized).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
