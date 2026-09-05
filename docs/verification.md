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

The CI frontend job runs the same checks. The unit suite covers MetricDefinition,
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

`MANIFEST_POLICY`:

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

## Issue #21 canonical Linux evidence environment

The governed tracked-evidence baseline is generated on GitHub Actions, not on
native Windows. The canonical environment is:

```text
CANONICAL_EVIDENCE_PLATFORM=Ubuntu 24.04 (ubuntu-24.04), x86_64
CANONICAL_PYTHON=3.11.16 (CPython)
CANONICAL_CONSTRAINTS=constraints/evidence-linux-py311.txt
CANONICAL_PIP=26.2.1
CANONICAL_BOOTSTRAP_RUN=33910956540
DETERMINISM_RUN_1=33911880057 (attempt 1)
DETERMINISM_RUN_2=33911880057 (attempt 2)
TRACKED_EVIDENCE_FILE_COUNT=37
CONSTRAINTS_SHA256=d8d992b83969cd955c430284b7caed70b728f475c772684e34529156c86b10cc
```

The constraints file is the exact 161-package `pip freeze` captured from the
canonical bootstrap run `33910956540`; it is not intended for native Windows
installation. Both CI jobs that run Python application code (`backend` and
`browser-e2e`) use the exact Python version, constraints file, and deterministic
runtime settings (`PYTHONHASHSEED=0`, single-threaded numeric libraries,
`MPLBACKEND=Agg`, `TZ=UTC`, and `C.UTF-8` locale). The frontend-only job is not
part of this Python environment contract.

The migrated tracked evidence was regenerated by that Linux environment. The
prior committed baseline was Windows-generated and is not a byte-identical
canonical baseline. Windows remains supported for semantic development and
local checks, but Linux is the release evidence origin. Future evidence
refreshes must run `python -m src.pipeline` on the canonical GitHub Actions
environment with the committed constraints, then review and commit only the
policy-defined tracked evidence. A short-lived branch-only artifact capture may
be used to transfer generated reviewer evidence from the runner; remove that
capture before the final PR. Do not commit manifests, validation predictions,
model binaries, or other runtime-only outputs.

## Issue #30 hosted-runner dispatch determinism

Package constraints and thread limits alone did not fully define the hosted
numeric runtime. The temporary Ubuntu 24.04 probe captured CPU models,
`numpy.show_runtime()`, `threadpoolctl`, PyTorch dispatch information, and
SHA-256 hashes for every policy-defined evidence file. Its replicas showed
that heterogeneous CPU dispatch can change the pipeline-owned LSTM smoke
metric while the statistical forecasts and anomaly outputs remain numerically
unchanged. The original failing runner's CPU was not captured, so the exact
historical CPU pair is not asserted here.

The one-control-at-a-time probe evidence was:

```text
BASELINE_RUN=33965450224: 3/3 stable on AMD EPYC 9V74 and AMD EPYC 7763
OPENBLAS_ONLY_RUN=33965685116: 3/3 passed, but LSTM hashes varied by 3.9633218307244533e-07
NUMPY_ONLY_RUN=33966547573: 3/3 passed, but one Intel replica diverged in governed reports
OPENBLAS_NUMPY_RUN=33965920150: 3/3 stable in the probe, but an independent PR runner still drifted
PYTORCH_DEFAULT_RUN=33966180658: 3/3 passed, but LSTM hashes varied again
DNNL_WITH_ATEN_RUN=33967207450: 3/3 byte-identical substantive evidence across AMD and Intel
DNNL_MINIMIZED_RUN=33967405894 (attempts 1-3): 3/3 byte-identical per attempt across AMD EPYC 9V74 and EPYC 7763
```

The permanent hosted contract therefore pins the smallest control set proven
stable across the observed CPU mix:

```text
OPENBLAS_CORETYPE=Haswell
NPY_DISABLE_CPU_FEATURES=X86_V3,X86_V4
DNNL_MAX_CPU_ISA=AVX2
ATEN_CPU_CAPABILITY=<unset>
```

The existing hash comparison remains strict: every policy-defined file is
compared byte-for-byte, including PNG figures; only
`reports/live_forecast.json.generated_at` is normalized. The probe's numerical
contract remained unchanged: SARIMA was selected by development rolling-origin
MAE, Exponential Smoothing retained the lower final-test MAE, interval
coverage remained 0.9102564102564102, Isolation Forest produced 8 signals,
and residual anomalies remained 0. These results do not promote the LSTM,
change final-test semantics, or turn exploratory anomalies into verified
climate events.

The controls are applied identically to the `backend`, `browser-e2e`, and
manual `serving-bundle` workflows. Windows remains a semantic-development
environment; governed evidence refreshes originate from the pinned Linux
workflow. The diagnostic workflow used for this investigation is temporary
and is removed before the repair PR.

The two-run determinism proof for this migration compares SHA-256 hashes for
every tracked evidence file, including PNG figures, across two runs of the same
commit. The only normalized field is
`reports/live_forecast.json.generated_at`; no tolerance or other normalization
is permitted. This baseline change does not modify model or anomaly logic:
SARIMA remains development-selected, final-test evaluation remains
post-selection, and the documented Exponential Smoothing final-test result and
Isolation Forest/residual anomaly counts remain governed invariants. The strict
drift guard introduced by PR #20 remains in that PR and is not copied or
weakened by Issue #21.

## Issue #7 browser verification

From `frontend/`, run:

```text
npm ci
npm run test:e2e
npm run test:e2e:report
```

Playwright starts the real local environment through `e2e/start-backend.mjs`:
it runs `python -m src.pipeline`, starts FastAPI, waits on `/ready`, and starts
Vite at `http://127.0.0.1:4173`. The suite uses only the packaged historical
dataset and no current or internet data. The desktop project is Chromium at
1440x900; the mobile project is Chromium at 390x844. Retries are disabled and
CI uses one worker.

The browser suite covers all five navigation destinations, reviewer-critical
model/forecast/anomaly semantics, keyboard focus and `aria-current`, mobile
page-level overflow, and deterministic API-unavailable/retry recovery. The
positive path is real API-backed application behavior; only the failure path
uses Playwright request routing to abort one API request.

Four focused visual regions are committed under `frontend/e2e/snapshots/`:
desktop Overview evidence, desktop Model Evaluation development-vs-final-test
evidence, desktop Forecast evidence, and the mobile Overview shell. Snapshots
are canonical Linux/Chromium baselines generated in the same environment as the
CI `browser-e2e` job. Windows reference images are not committed. Animations are
disabled, caret rendering is hidden, and `generated_at` is outside every visual
region. Use `npm run test:e2e:update-snapshots` only in that canonical Linux
environment after reviewing the resulting diff.

CI uploads `playwright-report/` and `test-results/` on failure. The scoped
`test:e2e:verify-baselines` step fails if the snapshot directory is missing or
becomes modified/untracked; it does not apply a blanket repository dirty-tree
policy. Runtime-only manifests, interval/residual reports, validation
predictions, and model binaries remain untracked under the Issue #15 policy.

## Issue #25 design system v2 verification

Issue #25 implements the approved design specification from PR #27
(`f9463bcdafeea94e30d66640decf8ce7724e79bd`) on the isolated
`feat/design-system-v2` branch. The frontend verification route is:

```text
npm ci
npm run lint
npm run test
npm run build
npm run build-storybook
npm run test:storybook
npm run test:e2e
npm run test:e2e:verify-baselines
npm audit --audit-level=high
```

The unit suite covers theme persistence/system resolution, the shell, domain
evidence modules, and chart grammar. Browser checks cover all five pages,
selection/evaluation semantics, fixed-origin forecast language, anomaly method
counts, keyboard focus, mobile navigation/reflow, and deterministic API
recovery. Storybook's browser project covers the shared component catalog and
fails on configured accessibility violations.

The theme contract is light/dark/system with localStorage key
`co2-forecast-lab-theme`; visual checks force light mode through an init script
so snapshot output is deterministic. The four focused visual regions remain
Linux/Chromium release evidence: Overview desktop, Model Evaluation desktop,
Forecast desktop, and Overview mobile shell. Windows-created `*-win32.png`
files are not release evidence and must not be committed.

## Issue #8 CI governance

The canonical generated-evidence regeneration command is:

```text
python -m src.pipeline
```

The policy-aware drift check runs immediately afterward:

```text
python scripts/verify_generated_evidence.py
```

It reads the `TRACKED_GENERATED_REVIEWER_EVIDENCE` and `RUNTIME_ONLY_GENERATED`
lists above, selects only the documented tracked paths from `git ls-files`, and
compares each regenerated path with the committed `HEAD` checkout content. It
normalizes only `reports/live_forecast.json.generated_at`; all model, forecast,
interval, anomaly, split, prediction, and report content remains comparison-
sensitive. Runtime-only manifests, interval/residual reports, validation
predictions, and model binaries do not participate in the comparison.

The focused tests in `tests/test_generated_evidence.py` cover a clean baseline,
substantive tracked drift, generated-at-only variance, other live-forecast
changes, runtime-only paths, and readable missing-field failures. A controlled
working-copy demonstration passed on the clean regenerated evidence, failed on
a changed `reports/forecast_metrics.json` with that exact path, and passed when
only `generated_at` differed.

The stable required CI checks are `backend`, `frontend`, and `browser-e2e`.
The backend job regenerates evidence and runs the drift check before pytest;
all three jobs have explicit 15-minute limits where applicable and retain pip
or npm dependency caching. Workflow-default permissions are `contents: read`.
The backend, frontend, and browser jobs receive no write permissions.

CodeQL is configured as a separate `codeql` security-analysis workflow for
Python and JavaScript/TypeScript source under `src`, `scripts`, and
`frontend/src`. It uses the official `github/codeql-action` v4 actions and
scopes `security-events: write` to that job only. CodeQL is visible security
analysis, not yet a required branch-protection check: its purpose here is to
surface actionable alerts without making a new alert policy or noisy scanner
an implicit merge gate. `npm audit --audit-level=high` remains the frontend
dependency gate. No additional Python dependency scanner is added because the
repository has no pinned lockfile or distinct Python audit policy, and adding
one would duplicate supply-chain signal without an agreed remediation policy.

All workflow actions are official first-party actions: checkout/setup-python/
setup-node/upload-artifact and github/codeql-action. Major action tags are used
to receive maintained fixes; no third-party action or secret-dependent service
is required. The CodeQL schedule is weekly and can also be dispatched manually.

Required local verification is the backend gate set (`ruff`, `compileall`,
pytest, pipeline, drift check, repository verification, Docker Compose,
notebook, and API import) followed by the complete frontend gate set (`npm
ci`, lint, unit tests, build, Storybook build, Storybook/a11y, Playwright E2E,
committed baseline verification, and high-severity npm audit). Generated
metrics and reports remain pipeline-owned and must never be hand-edited.

Main protection is intentionally deferred until the implementing PR is merged
and post-merge main CI is green. The planned required checks are `backend`,
`frontend`, and `browser-e2e`; `codeql` remains informational unless a later
review establishes a reliable blocking alert policy. The final ruleset should
require pull requests and these checks, block accidental direct pushes, avoid
an impractical multi-reviewer requirement for the solo maintainer, and preserve
an owner/admin recovery path.
