# Project Context

## Purpose

`climate-co2-forecasting-ml` is a reproducible portfolio system for demonstrating disciplined time-series forecasting and ML engineering on a **historical packaged Mauna Loa CO₂ dataset**. It compares statistical, machine-learning, and neural approaches, selects models without test leakage, measures a documented prediction interval, exposes governed artifacts through FastAPI, and presents the evidence in a React dashboard.

The primary success criterion is **trustworthy evidence a reviewer can reproduce**, not the largest model or most complex UI.

## Ubiquitous language

- **Source observation** — weekly historical CO₂ value from the packaged dataset.
- **Monthly observation** — month-end mean derived from source observations under the documented causal missing-data rule.
- **Feature row** — one monthly target with lag/rolling/cyclical predictors that were available before the target timestamp.
- **Train** — earliest governed feature period used to fit candidates/preprocessors.
- **Validation / development period** — post-train period used for deterministic rolling-origin folds, candidate selection, and interval calibration.
- **Development fold** — one expanding-history, non-overlapping rolling-origin validation block.
- **Final test** — untouched post-development period used once for post-selection evaluation.
- **Candidate** — model eligible for governed comparison under the documented protocol.
- **Selected model** — candidate chosen by development-fold rules, not final-test performance.
- **One-step forecast** — forecast for the next observation when prior actual observations are available at each origin.
- **Fixed-origin projection** — API projection launched after the historical record ends; it is not equivalent to rolling one-step evaluation.
- **Prediction interval** — the documented residual-quantile interval calibrated from development residuals; its measured coverage scope must remain explicit.
- **Anomaly signal** — exploratory statistical flag under a method/threshold assumption. It is not a verified event or cause.
- **Governed artifact** — repository data/report/forecast/anomaly artifact whose path, size, checksum, schema/order constraints, and provenance are validated before serving.
- **Ready** — the API can validate and safely serve all required governed artifacts. This is stricter than process liveness.

## Non-negotiable invariants

1. **No temporal leakage.** Future observations must never influence earlier feature rows, fills, scaling, selection, or calibration.
2. **No final-test tuning.** The final test cannot choose features, models, hyperparameters, thresholds, or interval calibration.
3. **Selection and evaluation stay separate.** Development-fold evidence selects; final-test evidence evaluates.
4. **Protocol labels stay explicit.** One-step rolling evaluation and fixed-origin multi-step serving must never be presented as the same validation result.
5. **Interval claims stay bounded.** Measured one-step coverage does not become a blanket long-horizon uncertainty guarantee.
6. **Anomaly claims stay exploratory.** Never imply detected rows are proven climate events, sensor faults, or causal effects.
7. **Evidence is reproducible.** If a result changes, the pipeline and generated evidence should explain why.
8. **Serving is artifact-governed.** No user-controlled arbitrary filesystem loading.
9. **Portfolio claims match evidence.** Do not describe this repository as a current feed, production SLA, deployed monitoring platform, or climate-policy model unless that capability is actually implemented and verified later.

## Current architecture

```text
historical source
  -> causal monthly preparation
  -> leakage-safe features
  -> candidate training/evaluation
  -> rolling-origin development selection
  -> one-time final-test evaluation
  -> interval + residual/anomaly evidence
  -> manifest/checksum governance
  -> FastAPI serving
  -> React/Vite dashboard
```

Primary references:

- `README.md`
- `docs/data_source.md`
- `docs/modeling_approach.md`
- `docs/evaluation.md`
- `docs/anomaly_detection.md`
- `docs/api.md`
- `docs/frontend.md`
- `docs/verification.md`
- `reports/model_manifest.json`

## Frontend product intent

The UI should feel like a **scientific/data-workbench dashboard** rather than a marketing SaaS page. A reviewer should be able to answer quickly:

1. What historical data is this?
2. What model was selected and why?
3. How did candidates perform under the governed protocol?
4. What does the forecast show, with what uncertainty boundary?
5. What anomaly methods disagree or agree?
6. What are the limitations and provenance of the evidence?

The visual system is defined in `DESIGN.md`.

## Decision ownership

Record durable architecture/model/evaluation/design decisions in `docs/adr/`. One ADR should capture one decision with context, options, decision, consequences, and status. If a decision changes, supersede the old ADR rather than erasing the history.
