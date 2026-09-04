from __future__ import annotations

import json

import pytest

from scripts.verify_generated_evidence import (
    EvidencePolicyError,
    compare_content,
    parse_artifact_policy,
    select_policy_paths,
)

POLICY = """\
`TRACKED_GENERATED_REVIEWER_EVIDENCE`:

- `reports/forecast_metrics.json`
- `reports/live_forecast.json`
- `reports/predictions/{sarima,naive}.csv`

`RUNTIME_ONLY_GENERATED`:

- `reports/model_manifest.json`
- `reports/predictions/validation/*.csv`

`MANIFEST_POLICY`:

Generated manifests are runtime-only.
"""


def _live_forecast(**overrides: object) -> bytes:
    payload = {
        "schema_version": "2.0.0",
        "generated_at": "2026-09-05T00:00:00+00:00",
        "model_name": "SARIMA",
        "forecast": [{"date": "2002-01-31", "prediction": 1.0}],
        **overrides,
    }
    return json.dumps(payload, indent=2).encode("utf-8")


def test_clean_deterministic_evidence_passes() -> None:
    assert compare_content("reports/forecast_metrics.json", b"same", b"same")


def test_substantive_tracked_mutation_fails() -> None:
    assert not compare_content("reports/forecast_metrics.json", b"new", b"old")


def test_only_live_forecast_generated_at_difference_passes() -> None:
    expected = _live_forecast()
    current = _live_forecast(generated_at="2026-09-05T01:00:00+00:00")
    assert compare_content("reports/live_forecast.json", current, expected)


def test_other_live_forecast_field_difference_fails() -> None:
    expected = _live_forecast()
    current = _live_forecast(model_name="Exponential Smoothing")
    assert not compare_content("reports/live_forecast.json", current, expected)


def test_runtime_only_paths_are_not_selected() -> None:
    policy = parse_artifact_policy(POLICY)
    paths = select_policy_paths(
        [
            "reports/forecast_metrics.json",
            "reports/live_forecast.json",
            "reports/model_manifest.json",
            "reports/predictions/validation/sarima.csv",
            "reports/predictions/naive.csv",
            "reports/predictions/sarima.csv",
        ],
        policy,
    )
    assert paths == [
        "reports/forecast_metrics.json",
        "reports/live_forecast.json",
        "reports/predictions/naive.csv",
        "reports/predictions/sarima.csv",
    ]


def test_volatile_field_is_required_for_live_forecast() -> None:
    with pytest.raises(EvidencePolicyError, match="generated_at"):
        compare_content(
            "reports/live_forecast.json",
            b'{"model_name": "SARIMA"}',
            _live_forecast(),
        )
