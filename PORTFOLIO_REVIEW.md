# Portfolio Review

## Leadership Summary

The project is a working local-first forecasting product, not a notebook-only
analysis. It turns a real atmospheric CO2 dataset into validated data, eight
comparable forecast approaches, anomaly signals, an inference API, and a
responsive dashboard. The strongest current result is Exponential Smoothing at
0.237 ppm MAE under rolling one-step evaluation on a held-out chronological
period.

The main presentation risk is overclaiming the deep-learning result. The generated LSTM artifact is a two-epoch pipeline check. It proves PyTorch integration, not tuned performance.

## Implemented Features

- real statsmodels CO2 ingestion
- raw and processed CSV persistence
- markdown metadata and validation reports
- monthly interpolation and chronological splits
- lag, rolling, and calendar features
- three baseline forecasts
- Exponential Smoothing and SARIMA
- Random Forest and Gradient Boosting
- configurable CPU PyTorch LSTM
- MAE, RMSE, MAPE, sMAPE, and MASE
- shared test-period enforcement
- residual analysis and comparison figures
- residual and Isolation Forest anomaly methods
- FastAPI health, metadata, history, forecast, and anomaly endpoints
- five-page React dashboard
- desktop and mobile screenshots
- pytest, frontend lint/build, Docker Compose, and GitHub Actions

## Data Science Skills Demonstrated

- real-data acquisition without synthetic fallback
- missing-value analysis and interpolation
- trend, seasonality, autocorrelation, and stationarity analysis
- honest metric interpretation
- exploratory anomaly framing
- model complexity comparison

## Time-Series Skills Demonstrated

- chronological split design
- leakage-safe lag and rolling features
- seasonal naive benchmarking
- additive seasonal modeling
- SARIMA seasonal differencing
- sliding-window sequence construction
- multi-step future forecasting
- residual diagnostics

## ML Engineering Skills Demonstrated

- modular training scripts
- common prediction artifact contract
- deterministic seed configuration
- CPU-safe debug and full-training modes
- startup-loaded API resources
- Pydantic response validation
- frontend API service boundary
- automated tests and CI
- Dockerized serving path independent from local development

## Remaining Gaps

1. Run a serious LSTM experiment and regenerate metrics.
2. Add forecast artifact versioning and checksum validation.
3. Add rolling-origin cross-validation and parameter search.
4. Calibrate forecast intervals instead of using residual scaling.
5. Add current data ingestion only after selecting a stable, documented source.
6. Add a public read-only deployment if free hosting remains reliable.

## Recruiter Review Path

1. Read the README overview and model table.
2. Open the desktop dashboard screenshot.
3. Inspect `src/features/preprocess_timeseries.py` for leakage controls.
4. Inspect `src/evaluation/evaluate_forecasts.py` for shared-period comparison.
5. Run `pytest`.
6. Run the API and dashboard locally.

## Resume Bullet

Built a local-first atmospheric CO2 forecasting platform that evaluated eight baseline, statistical, tree-based, and PyTorch models on a leakage-safe chronological test set, served forecasts through FastAPI, and visualized uncertainty, residuals, and anomaly signals in a responsive React dashboard.

## LinkedIn Version

Built an end-to-end atmospheric CO2 forecasting project using the real statsmodels time series. I compared eight forecasting approaches on one chronological holdout, added exploratory anomaly detection, served results with FastAPI, and built a responsive React dashboard. The most useful result was also the simplest: Exponential Smoothing beat the tree models and debug LSTM, reinforcing that model selection should follow evidence, not complexity.
