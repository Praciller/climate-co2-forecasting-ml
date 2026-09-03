# API

## Run

```bash
uvicorn src.api.main:app --reload --port 8000
```

## Lifecycle

FastAPI lifespan startup loads monthly history and the precomputed statistical forecast artifact once. Requests reuse the same in-memory service; no model fitting occurs in the API process.

## Endpoints

### `GET /health`

Returns service status, loaded-model status, and history row count.

### `GET /model-info`

Returns the governed model/evidence contract: active model and version,
historical dataset metadata, preprocessing and split boundaries, the fixed
forecasting/rolling-evaluation protocols, development selection rationale,
interval metadata, candidate names, training metadata, and nested validation
and final-test metrics. The selected model is defined by development
rolling-origin evidence; final-test metrics are post-selection evaluation.

### `GET /historical-data`

Returns monthly dates, CO2 values, and trailing 12-month means.

### `GET /forecast?horizon_months=24`

Returns 1-60 future monthly points with prediction, lower, and upper values,
plus model version, forecast origin, frequency, fixed-origin protocol, 90%
prediction-interval metadata, coverage scope, generation time, and explicit
limitations. Invalid horizons return FastAPI validation errors.

### `GET /anomalies`

Returns exploratory flagged months and method labels.

## CORS

Localhost and `127.0.0.1` origins are accepted on local development ports. Production deployments should replace the local regex with explicit frontend origins.
