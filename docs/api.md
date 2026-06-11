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

Returns active forecast method, training range, available model names, and generated evaluation metrics.

### `GET /historical-data`

Returns monthly dates, CO2 values, and trailing 12-month means.

### `GET /forecast?horizon_months=24`

Returns 1-60 future monthly points with prediction, lower, and upper values. Invalid horizons return FastAPI validation errors.

### `GET /anomalies`

Returns exploratory flagged months and method labels.

## CORS

Localhost and `127.0.0.1` origins are accepted on local development ports. Production deployments should replace the local regex with explicit frontend origins.
