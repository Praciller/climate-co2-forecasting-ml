# Verification

Fresh local verification completed on August 27, 2026. This evidence applies to
the repository working tree on `feat/rolling-origin-interval-eval`.

## Governed pipeline

| Gate | Result |
|---|---|
| Raw source integrity | Passed; SHA-256 `6d5ee9e8d32c1f8fa5f24f30a33ada05615ab19b3c4f6699fd2efc7d29b73085` |
| Causal preprocessing | Passed; 526 monthly rows, 5 imputed months, maximum causal fill 3 months |
| Explicit split | Train through 1989-01-31; validation through 1995-06-30; locked test through 2001-12-31 |
| Temporal contract | Passed; causal lags/rolling statistics, causal fill, train-only scaling, and fixed boundaries |
| Rolling-origin backtest | Passed; 11 non-overlapping seven-month development folds, SARIMA mean MAE `0.2394` ppm |
| Candidate selection | SARIMA selected on mean development-fold MAE `0.2394` ppm |
| Locked final test | SARIMA MAE `0.2433` ppm; evaluated only after selection |
| 90% prediction interval | Development-fold residual quantile; 91.03% observed one-step test coverage; 1.011 ppm average width; 78 test months |
| Residual diagnostic | Mean `0.0216`; standard deviation `0.2973`; lag-1 correlation `0.0511` |
| Anomaly boundary | 8 Isolation Forest flags; 0 residual flags; development-calibrated thresholds |
| Artifact manifest | Passed; eight governed artifacts validated by path, schema, and SHA-256 |
| Repository guardrails | Passed; 149 tracked and intended files scanned |

The LSTM is a validation-only pipeline smoke test. It is excluded from model
ranking and is not evidence of competitive forecasting performance.

## Automated checks

```text
python -m pytest -q
36 passed

ruff check src tests
All checks passed

python -m compileall -q src
exit 0

python -m src.verify_repository
Repository guardrails passed for 149 tracked and intended files.

jupyter nbconvert --execute notebooks/01_eda.ipynb
11 cells, 5 code cells, 0 execution errors

npm ci
0 vulnerabilities

npm run lint
exit 0

npm run build
exit 0
```

## Docker and API

`docker compose config` passed. Both images built and ran as unprivileged users;
the API and frontend health checks became healthy.

- `/health`: HTTP 200, liveness `ok`, readiness `true`
- `/ready`: HTTP 200
- `/model-info`: HTTP 200, development-fold-selected SARIMA
- `/historical-data`: HTTP 200, 526 rows
- `/forecast?horizon_months=60`: HTTP 200, 60 contiguous month-end rows with ordered intervals
- `/anomalies`: HTTP 200, 8 rows
- `/docs`: HTTP 200

The service fails readiness closed when the manifest is missing or a governed
artifact checksum does not match. Error responses are sanitized.

## Browser acceptance

Playwright acceptance was run against the Docker frontend and API at desktop and
390-by-844 mobile viewports. The final run covered navigation, API connection,
validation/test labels, the six-month horizon interaction, anomaly caveats,
model comparison, keyboard focus, console errors, and page-level overflow.
Updated screenshots are stored in `reports/screenshots/`.

## Residual risk and scope

- The live forecast is a fixed-origin historical extension from 2001-12-31, not
  a current atmospheric forecast.
- Interval coverage is measured for rolling one-step predictions on the locked
  historical test only; the 90% interval is not a guarantee for 60-step
  recursive horizons or a 95% confidence interval.
- Anomaly flags are exploratory statistical signals, not confirmed measurement
  errors or climate events.
- No production deployment, external monitoring, or current-data ingestion was
  verified.

## Issue #5 frontend quality foundation

The `feat/frontend-quality-foundation` branch adds a clean-install frontend
quality gate for representative shared components. It uses Vitest, jsdom,
Testing Library, Storybook, the official Vitest addon, and the official a11y
addon. The browser check is limited to isolated Storybook stories; full
application E2E and visual regression remain later issue scope.

Run from `frontend/`:

```text
npm ci
npm run lint
npm run test
npm run build
npm run build-storybook
npx playwright install --with-deps chromium
npm run test:storybook
npm audit --audit-level=high
```

The CI frontend job runs the same checks. The unit suite covers MetricCard,
LoadingState, ErrorMessage, ModelComparisonTable, and AppShell. Storybook
stories cover those components and enforce configured accessibility checks.

Backend checks were also run without regenerating evidence: `ruff check src
tests` and `python -m compileall -q src` passed. `python -m pytest -q` remains
PARTIAL with 4 API/readiness failures because `reports/model_manifest.json` is
absent in this clean feature worktree, and `python -m src.verify_repository`
fails closed for the same missing governed manifest. No model, data, or report
artifact was changed for Issue #5.

## Issue #6 dashboard design refactor

The dashboard was reviewed against `DESIGN.md` with the real local API and Vite
frontend on September 4, 2026. The browser pass covered all five pages at
1440-by-900 desktop and 390-by-844 mobile viewports. Each page loaded API-backed
historical/model/anomaly/forecast data, exposed exactly one active navigation
item, kept document and body width within the viewport, and produced no
page-error or console-error output. Mobile comparison and forecast tables use
bounded horizontal scrolling rather than overflowing the page.

The review also checked keyboard navigation from the document body, visible
focus rings, method-specific anomaly labels/markers, the fixed-origin forecast
origin, the 90% nominal interval boundary, and the development-selection versus
final-test distinction. Screenshots were captured outside the repository for
review; no screenshot or generated pipeline artifact is committed by Issue #6.

The frontend contract now mirrors the nested `/model-info` response and the
metadata-bearing `/forecast` response. The UI does not claim current-data
monitoring, multi-horizon interval coverage, or final-test-driven model
selection.

## Issue #15 governed evidence ownership

The canonical regeneration command is:

```text
python -m src.pipeline
```

Generated metrics and reports are pipeline-owned and must never be hand-edited.
After regeneration, tracked evidence is compared byte-for-byte; only the
documented volatile metadata below may be normalized.

`TRACKED_GENERATED_REVIEWER_EVIDENCE`:

- `data/processed/*.csv`
- `reports/anomalies.csv`
- `reports/anomaly_report.md`
- `reports/baseline_metrics.json`
- `reports/data_validation_report.md`
- `reports/dataset_metadata.md`
- `reports/eda_summary.md`
- `reports/figures/*.png` (excluding manually captured `reports/screenshots/`)
- `reports/forecast_interval_evaluation.json`
- `reports/forecast_metrics.json`
- `reports/live_forecast.json`
- `reports/lstm_metrics.json`
- `reports/ml_regressor_metrics.json`
- `reports/model_comparison.md`
- `reports/predictions/{exponential_smoothing,gradient_boosting,moving_average,naive,random_forest,sarima,seasonal_naive}.csv`
- `reports/rolling_origin_evaluation.{json,md}`
- `reports/statistical_metrics.json`

`RUNTIME_ONLY_GENERATED`:

- `reports/model_manifest.json`
- `reports/interval_report.json`
- `reports/residual_report.json`
- `reports/predictions/validation/*.csv`
- `models/*.joblib`
- `models/*.pt`

`reports/model_manifest.json` is generated by the pipeline and must exist before
API serving. A fresh checkout therefore runs `python -m src.pipeline` before
starting Uvicorn; readiness validates the generated manifest and its governed
artifact checksums. The manifest remains runtime-only because it contains
runtime metadata and checksums for other runtime artifacts.

`reports/live_forecast.json` remains tracked reviewer evidence. Its forecast
values, interval values, model, origin, protocol, and limitations are
deterministic; only `generated_at` varies between runs. A future drift check may
normalize only that field. The manifest's `generated_at` and its derived
`artifacts.live_forecast.sha256` are runtime-only and are not tracked-evidence
comparison inputs.
