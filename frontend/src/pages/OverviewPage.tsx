import { MetricCard } from '../components/MetricCard'
import { ModelComparisonTable } from '../components/ModelComparisonTable'
import { TimeSeriesChart } from '../components/TimeSeriesChart'
import type { AnomalyPoint, HistoricalPoint, ModelInfo } from '../types/api'

interface OverviewPageProps {
  anomalies: AnomalyPoint[]
  historical: HistoricalPoint[]
  modelInfo: ModelInfo
}

export function OverviewPage({
  anomalies,
  historical,
  modelInfo,
}: OverviewPageProps) {
  const first = historical[0]
  const latest = historical.at(-1)
  const models = modelInfo.metrics.models ?? {}
  const bestMetrics = modelInfo.metrics.best_model
    ? models[modelInfo.metrics.best_model]
    : undefined

  return (
    <div className="space-y-10">
      <section className="grid gap-8 border-b border-rule pb-9 xl:grid-cols-[1.6fr_1fr]">
        <div>
          <h2 className="max-w-3xl text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">
            Forecast atmospheric CO2 with evidence at every step.
          </h2>
          <p className="mt-4 max-w-2xl text-sm leading-6 text-ink-muted">
            Real weekly observations from statsmodels become monthly forecasts,
            comparable model metrics, and exploratory anomaly signals.
          </p>
        </div>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-5 text-sm">
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">
              Source
            </dt>
            <dd className="mt-1 font-medium">statsmodels CO2</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">
              Range
            </dt>
            <dd className="mt-1 font-medium">
              {first?.date.slice(0, 4)} to {latest?.date.slice(0, 4)}
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">
              Live model
            </dt>
            <dd className="mt-1 font-medium">{modelInfo.active_model}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">
              Split
            </dt>
            <dd className="mt-1 font-medium">Chronological 70/15/15</dd>
          </div>
        </dl>
      </section>

      <section>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="section-heading">Observed monthly concentration</h2>
            <p className="mt-1 text-sm text-ink-muted">
              Monthly mean and trailing 12-month mean, parts per million.
            </p>
          </div>
          <p className="tabular text-sm font-medium">
            Latest {latest?.co2.toFixed(2)} ppm
          </p>
        </div>
        <TimeSeriesChart data={historical} />
      </section>

      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Best test model"
          value={modelInfo.metrics.best_model ?? 'Pending'}
          detail="Selected by lowest MAE"
        />
        <MetricCard
          label="Test MAE"
          value={bestMetrics ? `${bestMetrics.mae.toFixed(3)} ppm` : 'Pending'}
          detail="Lower is better"
        />
        <MetricCard
          label="Models compared"
          value={String(Object.keys(models).length)}
          detail="Baseline through deep learning"
        />
        <MetricCard
          label="Anomaly signals"
          value={String(anomalies.length)}
          detail="Exploratory, not ground truth"
        />
      </section>

      <section>
        <div className="mb-4">
          <h2 className="section-heading">Model comparison</h2>
          <p className="mt-1 text-sm text-ink-muted">
            Shared held-out test period, ordered by mean absolute error.
          </p>
        </div>
        <ModelComparisonTable
          bestModel={modelInfo.metrics.best_model}
          models={models}
        />
      </section>
    </div>
  )
}

export default OverviewPage
