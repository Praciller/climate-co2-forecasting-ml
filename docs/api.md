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

## Structured diagnostics

The API emits compact JSON log events to stderr for local diagnostics. Stable fields include `timestamp`, `level`, `service`, `component`, and `event`; request completion events also include a generated `request_id`, HTTP method, route template, status code, and bounded duration in milliseconds. The same request identifier is returned in the `X-Request-ID` response header.

Startup/readiness failures emit only a sanitized failure category and exception type. Raw exception messages, query strings, request bodies, credentials, arbitrary filesystem paths, and governed data payloads are not logged. Sensitive keys and common bearer/API-token shapes are redacted before serialization. Native logs are diagnostic evidence only; this repository does not claim a hosted logging, alerting, tracing, or production-SLA stack.

Example sanitized events:

```json
{"component":"request","duration_ms":3.214,"event":"api_request_completed","level":"INFO","method":"GET","request_id":"4d7d...","route":"/health","service":"co2-forecast-api","status_code":200,"timestamp":"2026-09-05T04:30:00+00:00"}
{"component":"artifact_loader","error_type":"ArtifactValidationError","event":"governed_artifact_load_failed","failure_category":"artifact_validation_error","level":"ERROR","readiness_code":"artifact_validation_failed","service":"co2-forecast-api","timestamp":"2026-09-05T04:30:01+00:00"}
```

## CORS

Localhost and `127.0.0.1` origins are accepted on local development ports. Production deployments should replace the local regex with explicit frontend origins.
