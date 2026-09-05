from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts.stage_frontend import FrontendStageError, stage_frontend


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def test_stages_built_assets_only_and_is_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "frontend" / "dist"
    source.mkdir(parents=True)
    (source / "index.html").write_text("<html>dashboard</html>\n", encoding="utf-8")
    (source / "assets").mkdir()
    (source / "assets" / "app.js").write_text("console.log('ok')\n", encoding="utf-8")
    target = tmp_path / "api" / "frontend_dist"

    result = stage_frontend(source=source, target=target)
    first_digest = _tree_digest(target)
    result_again = stage_frontend(source=source, target=target)

    assert result == target
    assert result_again == target
    assert _tree_digest(target) == first_digest
    assert sorted(path.relative_to(target).as_posix() for path in target.rglob("*")) == [
        "assets",
        "assets/app.js",
        "index.html",
    ]


@pytest.mark.parametrize("forbidden", ["node_modules", "src", "tests", "data", "reports", "models", "notebooks"])
def test_rejects_non_build_artifacts(tmp_path: Path, forbidden: str) -> None:
    source = tmp_path / "dist"
    source.mkdir()
    (source / "index.html").write_text("<html></html>\n", encoding="utf-8")
    (source / forbidden).mkdir()
    (source / forbidden / "unexpected.txt").write_text("x", encoding="utf-8")

    with pytest.raises(FrontendStageError, match="only built frontend assets"):
        stage_frontend(source=source, target=tmp_path / "staged")


def test_rejects_missing_build_output_without_touching_target(tmp_path: Path) -> None:
    target = tmp_path / "staged"
    target.mkdir()
    (target / "old.js").write_text("old", encoding="utf-8")

    with pytest.raises(FrontendStageError, match="does not exist"):
        stage_frontend(source=tmp_path / "missing", target=target)

    assert (target / "old.js").read_text(encoding="utf-8") == "old"
