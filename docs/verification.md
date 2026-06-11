# Verification

Fresh verification completed on June 12, 2026.

## Reproducibility

| Gate | Result |
|---|---|
| Python dependency install | Passed; `pip check` reported no broken requirements |
| Data loading | Passed; 2,284 weekly rows saved |
| Validation | Passed; markdown report regenerated |
| Preprocessing | Passed; 526 monthly rows and chronological features regenerated |
| Baseline models | Passed |
| Statistical models | Passed; Exponential Smoothing selected |
| ML regressors | Passed |
| PyTorch LSTM debug run | Passed; two CPU epochs |
| Shared evaluation | Passed; best MAE 0.237 ppm |
| Anomaly detection | Passed; 16 exploratory rows |
| EDA generation | Passed; four required figures regenerated |

## Automated Checks

```text
python -m pytest
11 passed

python -m compileall -q src
exit 0

jupyter nbconvert --execute notebooks/01_eda.ipynb
11 cells, 5 code cells, 0 execution errors

npm ci
0 vulnerabilities

npm run lint
exit 0

npm run build
exit 0
```

CI repeats backend tests, bytecode compilation, notebook execution, frontend
lint, and frontend production build on pushes and pull requests.

## Docker Compose

Both images built and started through Docker Compose using alternate host ports:

- frontend: HTTP 200
- `/health`: HTTP 200
- `/model-info`: HTTP 200
- `/historical-data`: HTTP 200
- `/forecast?horizon_months=24`: HTTP 200
- `/anomalies`: HTTP 200
- `/docs`: HTTP 200
- 10-request forecast benchmark: 4.37 ms mean, 21.57 ms maximum

The benchmark is local evidence, not a production latency guarantee.

## Browser Smoke

Verified against the Docker frontend and API:

- dashboard title and API-connected state
- overview metrics and model comparison
- navigation to Forecasting, Anomaly Detection, and Model Evaluation
- forecast horizon change from 24 to 6 months produced six table rows
- anomaly page produced 16 flagged rows and retained the exploratory caveat
- evaluation page produced eight model rows
- residual and error images loaded with non-zero natural dimensions
- 390-by-844 mobile viewport had no page-level horizontal overflow
- mobile navigation remained independently horizontally scrollable

## Residual Risk

- LSTM evidence is a debug pipeline run, not tuned model performance.
- Forecast intervals are residual-scaled approximations.
- Browser automation retained one historical Recharts warning from an older
  asset; the current build sets explicit initial chart dimensions and produced
  no new warning entry during the rerun.
