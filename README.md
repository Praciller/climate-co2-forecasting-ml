# Climate CO2 Forecasting System

A reproducible atmospheric CO2 forecasting system that compares statistical,
machine-learning, and neural approaches through chronological rolling
evaluation, governs forecast intervals and model artifacts, and serves bounded
exploratory analysis through FastAPI and React.

- **Governed evidence:** 359 training, 77 validation, and 78 final-test feature
  rows with fixed, non-overlapping date boundaries.
- **Selection without test leakage:** SARIMA is selected across 11 development
  folds on mean MAE (`0.239 ppm`); its final-test MAE is `0.243 ppm`.
- **Measured prediction intervals:** a 90% development-fold residual-quantile
  one-step interval achieves `91.0%` coverage across 78 final-test forecasts
  with `1.011 ppm` average width.
- **Verifiable serving:** a repository-relative manifest checks eight data,
  evaluation, forecast, and anomaly artifacts before the API becomes ready.

![CO2 Forecast Lab dashboard](reports/screenshots/dashboard-overview.png)

## Review in under 10 minutes

```powershell
uv venv .venv --python 3.11
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.\.venv\Scripts\python.exe -m src.pipeline
.\.venv\Scripts\python.exe -m pytest -q
```

Then start the API and dashboard in separate terminals:

```powershell
.\.venv\Scripts\uvicorn.exe src.api.main:app --port 8000
```

```powershell
Set-Location frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. The pipeline is deterministic on CPU, needs no
provider key or external data download, and keeps the two-epoch LSTM run
explicitly outside candidate ranking.

## Dataset and frequency contract

The source is the historical **Mauna Loa Weekly Atmospheric CO2 Data** packaged
with `statsmodels.datasets.co2`. The installed package provides 2,284 weekly
`W-SAT` calendar rows from 1958-03-29 through 2001-12-29: 2,225 observed values
and 59 missing values, measured in ppmv. It is public-domain source data
obtained upstream in 2014, not a current NOAA feed.

The repository fingerprint for the package-loaded CSV is:

```text
SHA-256 6d5ee9e8d32c1f8fa5f24f30a33ada05615ab19b3c4f6699fd2efc7d29b73085
```

Weekly observations become 526 month-end means. Five months have no observed
weekly value (`1958-06`, `1958-10`, and `1964-02` through `1964-04`); they use a
causal forward fill bounded to three consecutive months. The output records
`observed_week_count` and `is_imputed` lineage. It never uses a later value to
fill an earlier month and fails if a gap exceeds the configured bound.

Authoritative details:
[data source](docs/data_source.md) and
[generated validation report](reports/data_validation_report.md).

## Forecasting protocol

One governed split contract is shared by every candidate:

| Role | Feature rows | Period | Permitted use |
|---|---:|---|---|
| Train | 359 | 1959-03-31 to 1989-01-31 | Fit candidates and preprocessors |
| Validation | 77 | 1989-02-28 to 1995-06-30 | Development folds, selection, calibration |
| Final test | 78 | 1995-07-31 to 2001-12-31 | One post-selection evaluation |

Candidate evidence uses **rolling-origin one-step-ahead** forecasts with an
expanding observed history. The target month is never in its own lag or rolling
feature, and the previous actual observation is available at each new origin.
Every saved row records target date, origin date, horizon, split, protocol, and
refit behavior.

One split is insufficient because a single contiguous holdout can be unusually
easy or difficult for one historical regime. The governed backtest therefore
uses 11 deterministic expanding folds: 359 initial training feature rows, then
eleven non-overlapping seven-month validation blocks through 1995-06-30. The
final-test period starts at 1995-07-31 and is never used for fold construction,
model selection, or interval calibration. See the [rolling-origin report](reports/rolling_origin_evaluation.md)
for per-fold and aggregate MAE, RMSE, sMAPE, and MASE.

This differs from the API output: the served artifact is a **fixed-origin
multi-step** projection beginning after 2001-12-31. Tree models use observed
one-step features for evaluation and are not presented as long-horizon
extrapolators.

See [modeling approach](docs/modeling_approach.md) and
[evaluation protocol](docs/evaluation.md).

## Model comparison

The selected model is the candidate with the lowest mean development-fold MAE.
Ties use mean fold RMSE and then an explicit simplicity order. Final-test
results do not change the selected model.

| Candidate | Validation MAE | Final-test MAE | Final-test RMSE | Final-test MASE |
|---|---:|---:|---:|---:|
| **SARIMA (selected)** | **0.238** | 0.243 | 0.298 | 0.197 |
| Exponential Smoothing | 0.270 | **0.237** | **0.295** | **0.191** |
| Naive | 1.126 | 1.136 | 1.276 | 0.918 |
| Seasonal Naive | 1.278 | 1.693 | 1.849 | 1.368 |
| Moving Average | 2.100 | 1.988 | 2.290 | 1.607 |
| Random Forest | 3.290 | 3.966 | 4.984 | 3.205 |
| Gradient Boosting | 4.471 | 5.840 | 6.850 | 4.719 |

The result is specific to this smooth, historical, univariate series and this
one-step protocol. The tree models flatten because they cannot naturally
extrapolate the rising level beyond their fitted target range; this is a model
and feature limitation, not a library failure.

The two-epoch PyTorch LSTM restores its best validation checkpoint and proves
sequence construction, train-only scaling, validation monitoring, and CPU
execution. It is labeled `pipeline_smoke`, excluded from selection, and absent
from the candidate comparison plot.

Raw evidence: [model comparison](reports/model_comparison.md) and
[`forecast_metrics.json`](reports/forecast_metrics.json).

## Forecast intervals

The selected model's 77 out-of-sample development-fold residuals define a
finite-sample absolute-residual quantile radius of `0.506 ppm` at 90% nominal
coverage. Applying that radius to the final one-step test predictions produces:

- observed coverage: **91.0%** (`71/78`)
- average width: **1.011 ppm**
- calibration samples: **77**
- evaluation samples: **78**

This is a measured **90% prediction interval**, not a 95% confidence interval or
general probabilistic-calibration claim. The API shows the same development-
derived radius around each fixed-origin multi-step projection, but coverage
beyond one month has not been established.

See [`forecast_interval_evaluation.json`](reports/forecast_interval_evaluation.json)
and [`interval_report.json`](reports/interval_report.json).

## Residual and anomaly analysis

Residual diagnostics use the selected SARIMA's out-of-sample final-test
forecasts: mean residual `0.022 ppm`, standard deviation `0.297 ppm`, and lag-1
autocorrelation `0.051` across 78 ordered errors.

Anomaly output is limited to the final-test period and preserves method
disagreement:

- residual threshold: 99% validation-residual radius, applied only to test
- Isolation Forest: fit on train plus validation only
- features: one- and twelve-month changes, deviation from prior rolling mean,
  prior rolling scale, and cyclical month; no absolute year or raw level
- contamination assumption: 3% of development scores
- current result: 8 Isolation Forest signals, 0 residual signals, 0 agreements

These are exploratory statistical signals under selected assumptions. They are
not verified climate events, sensor failures, or causal discoveries.

See [residual evidence](reports/residual_report.json),
[anomaly report](reports/anomaly_report.md), and
[method documentation](docs/anomaly_detection.md).

## Artifact and model governance

[`reports/model_manifest.json`](reports/model_manifest.json) records:

- source fingerprint and package version
- preprocessing and feature contracts
- exact split boundaries and forecasting protocol
- selected-model rationale
- interval method and measured coverage
- runtime versions and Git identifier
- repository-relative artifact paths, byte sizes, and SHA-256 checksums

FastAPI validates the manifest schema, path containment, file existence,
checksums, monthly ordering, forecast continuity, and interval ordering before
readiness. The serving path loads governed JSON/CSV only. Ignored joblib and
PyTorch files are local training outputs and must be treated as trusted
repository-created artifacts; arbitrary user paths are never accepted.

## API and dashboard

| Endpoint | Contract |
|---|---|
| `GET /health` | Liveness plus readiness state |
| `GET /ready` | `200` only when governed artifacts validate |
| `GET /model-info` | Dataset, split, selection, interval, and metric provenance |
| `GET /historical-data` | Ordered monthly history and trailing 12-month mean |
| `GET /forecast?horizon_months=24` | Bounded 1–60 month fixed-origin projection |
| `GET /anomalies` | Bounded exploratory final-test signal rows |

Forecast responses disclose model/version, historical origin, horizon,
frequency, protocol, interval method and coverage scope, artifact timestamp,
and limitations.

The React dashboard provides Overview, Data Explorer, Forecasting, Anomaly
Detection, and Model Evaluation pages with loading, empty, API-unavailable,
keyboard-focus, responsive-table, and non-color-only label support.

See [API](docs/api.md) and [frontend](docs/frontend.md).

## Local quickstart

Run the complete governed pipeline:

```bash
python -m src.pipeline
```

Individual debugging stages:

```bash
python -m src.data.load_co2
python -m src.data.validate_data
python -m src.features.preprocess_timeseries
python -m src.eda.generate_eda
python -m src.models.train_baselines
python -m src.models.train_statistical
python -m src.models.train_ml_regressors
python -m src.models.train_lstm --debug
python -m src.evaluation.rolling_origin_evaluation
python -m src.evaluation.evaluate_forecasts
python -m src.anomaly.detect_anomalies
```

Docker remains optional:

```bash
docker compose up --build
```

No hosted deployment is claimed.

## Testing and CI

```powershell
ruff check src tests
.\.venv\Scripts\python.exe -m compileall -q src
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\jupyter.exe nbconvert --to notebook --execute notebooks/01_eda.ipynb --output executed.ipynb --output-dir $env:TEMP
Set-Location frontend
npm ci
npm run lint
npm run build
npm audit
```

CI repeats deterministic backend tests, compilation, Ruff, notebook execution,
manifest verification, frontend lint/typecheck/build, dependency audit, Docker
Compose validation, and repository guardrails. See
[verification](docs/verification.md).

## Scope and limitations

- The packaged record ends in December 2001; the system does not ingest current
  atmospheric measurements.
- This is an educational forecasting system, not a climate-policy model,
  causal climate model, monitoring service, alerting platform, or scientific
  anomaly detector.
- One-step interval coverage does not establish multi-horizon calibration.
- The test period is one historical regime and is not representative of every
  forecasting problem.
- The LSTM result is pipeline smoke, not a tuned neural benchmark.
- Local tests and container checks are reproducibility evidence, not a
  production SLA, security certification, or scalability claim.

## Documentation links

- [Data source and transformation](docs/data_source.md)
- [Modeling approach](docs/modeling_approach.md)
- [Evaluation and metrics](docs/evaluation.md)
- [Anomaly methods](docs/anomaly_detection.md)
- [API contract](docs/api.md)
- [Frontend reviewer path](docs/frontend.md)
- [Local and Docker deployment](docs/deployment.md)
- [Verification record](docs/verification.md)
- [Portfolio review](PORTFOLIO_REVIEW.md)
