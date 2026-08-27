# Modeling Approach

## Governed split

Split dates live in `src.utils.config` and are consumed by every trainer:

- train: 1959-03-31 through 1989-01-31 (359 feature rows)
- validation: 1989-02-28 through 1995-06-30 (77 rows)
- final test: 1995-07-31 through 2001-12-31 (78 rows)

There is no temporal shuffle, validation-block overlap, boundary inference
inside individual trainers, or test use during candidate selection. The LSTM
loader also preserves sequence order (`shuffle=False`).

## Forecast-time features

- lags: 1, 3, 6, and 12 months
- prior rolling means: 3, 6, and 12 months
- prior rolling standard deviations: 3, 6, and 12 months
- calendar: month, quarter, and year

Rolling calculations start from `co2.shift(1)`. The target month cannot enter
its own predictors. Tabular candidate evaluation is one-step-ahead and may use
the actual observation from the preceding origin; it is not presented as a
recursive multi-step tree forecast.

## Ranking-eligible candidates

- naive previous observation
- trailing 12-month mean
- seasonal naive at lag 12
- additive Exponential Smoothing with 12-month seasonality
- SARIMA `(1,1,1)(1,1,1,12)`
- Random Forest
- Gradient Boosting

Validation and final-test prediction rows share a contract: `date`,
`origin_date`, `horizon`, `evaluation_split`, `protocol`, `refit_at_origin`,
`actual`, and `prediction`.

Exponential Smoothing is refit at every origin. SARIMA parameters are fitted at
the split start and its state is updated with each observed value without
parameter refitting. Baselines update observed history. Tree models fit once on
the permitted pre-split rows.

## Neural pipeline smoke

The PyTorch LSTM uses a 24-month sequence, a StandardScaler fitted on training
only, seeded deterministic CPU operations, validation monitoring, best-state
restoration, and optional early stopping. The committed two-epoch run is
`pipeline_smoke` evidence and `ranking_eligible: false`.

It is not included in candidate selection, the final-test ranking, or the
candidate comparison plot.

## Fixed-origin serving

After development-fold selection and final-test evaluation, the selected
SARIMA is fit on all 526 monthly values to create a bounded 60-month fixed-origin
projection from 2001-12-31. This serving protocol is deliberately separate from
the rolling one-step comparison. The selected model and interval are not tuned
against final-test labels.
