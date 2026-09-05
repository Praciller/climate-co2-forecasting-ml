from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _dependency_name(requirement: str) -> str:
    return re.split(r"[<>=!~\[]", requirement, maxsplit=1)[0].strip().lower()


def test_vercel_project_declares_only_serving_dependencies() -> None:
    import tomllib

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = {
        _dependency_name(requirement)
        for requirement in project["project"]["dependencies"]
    }
    assert dependencies == {"fastapi", "numpy", "pandas", "statsmodels", "uvicorn"}
    assert not dependencies.intersection(
        {"torch", "jupyter", "pytest", "ruff", "scikit-learn", "matplotlib"}
    )
    assert project["project"]["requires-python"] == ">=3.12,<3.13"


def test_vercel_install_command_installs_serving_project_and_frontend_only() -> None:
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    install_steps = [step.strip() for step in config["installCommand"].split("&&")]

    assert install_steps == ["python -m pip install .", "npm --prefix frontend ci"]
    install_command = config["installCommand"].lower()
    assert "requirements.txt" not in install_command
    assert "torch" not in install_command


def test_vercel_function_configuration_excludes_nonserving_source() -> None:
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    function = config["functions"]["api/index.py"]
    excludes = function["excludeFiles"]
    for pattern in ("data/**", "reports/**", "models/**", "tests/**", "notebooks/**"):
        assert pattern in excludes
    assert "torch" not in (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_vercel_upload_does_not_include_canonical_training_requirement_files() -> None:
    ignored = (ROOT / ".vercelignore").read_text(encoding="utf-8").splitlines()
    assert "requirements.txt" in ignored
    assert "requirements-api.txt" in ignored
    assert "constraints/" in ignored
