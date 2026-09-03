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
  const selectedModel = modelInfo.selection.selected_model
  const models = modelInfo.metrics.final_test.models
  const selectedMetrics = models[selectedModel]
  const finalTestWinnerEntry = Object.entries(models).sort(
    ([, left], [, right]) => left.mae - right.mae,
  )[0]
  const finalTestWinner = finalTestWinnerEntry?.[0] ?? 'Unavailable'
  const finalTestWinnerMetrics = finalTestWinnerEntry?.[1]
  const developmentMae =
    modelInfo.metrics.rolling_origin.aggregate[selectedModel]?.mae.mean
  const measuredCoverage = modelInfo.interval.observed_test_coverage * 100
  const measuredCoverageSamples = Math.round(
    modelInfo.interval.observed_test_coverage *
      modelInfo.interval.evaluation_samples,
  )

  return (
    <div className="space-y-10">
      <section className="grid gap-8 border-b border-rule pb-9 xl:grid-cols-[1.5fr_1fr]">
        <div>
          <h2 className="max-w-3xl text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">
            Historical CO₂ evidence, from source to forecast.
          </h2>
          <p className="mt-4 max-w-2xl text-sm leading-6 text-ink-muted">
            A reproducible workbench for the packaged Mauna Loa dataset,
            governed model selection, held-out evaluation, and exploratory
            signals. This dashboard does not ingest current atmospheric data.
          </p>
        </div>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-5 text-sm">
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">
              Dataset
            </dt>
            <dd className="mt-1 font-medium">Mauna Loa CO₂</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">Scope</dt>
            <dd className="mt-1 font-medium">
              {datasetScope(modelInfo.dataset.period)}
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">Frequency</dt>
            <dd className="mt-1 font-medium">{modelInfo.dataset.frequency}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.12em] text-ink-muted">Unit</dt>
            <dd className="mt-1 font-medium">{modelInfo.dataset.unit}</dd>
          </div>
        </dl>
      </section>

      <section>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="section-heading">Observed monthly concentration</h2>
            <p className="mt-1 text-sm text-ink-muted">
              {first?.date} to {latest?.date} · month-end means in ppm.
            </p>
          </div>
          <p className="tabular text-sm font-medium">
            Latest observation {latest?.co2.toFixed(2)} ppm
          </p>
        </div>
        <TimeSeriesChart data={historical} />
      </section>

      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Selected by development"
          value={selectedModel}
          detail={`${modelInfo.metrics.rolling_origin.fold_count} rolling-origin folds · ${developmentMae?.toFixed(3) ?? '—'} ppm MAE`}
        />
        <MetricCard
          label="Selected model · final test"
          value={selectedMetrics ? `${selectedMetrics.mae.toFixed(3)} ppm` : '—'}
          detail="Post-selection evaluation"
        />
        <MetricCard
          label="Lowest final-test MAE"
          value={finalTestWinnerMetrics ? `${finalTestWinnerMetrics.mae.toFixed(3)} ppm` : '—'}
          detail={`${finalTestWinner} · does not change selection`}
        />
        <MetricCard
          label="Measured one-step coverage"
          value={`${measuredCoverage.toFixed(1)}%`}
          detail={`${modelInfo.interval.nominal_coverage * 100}% nominal · ${measuredCoverageSamples}/${modelInfo.interval.evaluation_samples} test months`}
        />
      </section>

      <section className="grid gap-6 border-y border-rule py-6 md:grid-cols-2">
        <div>
          <h2 className="section-heading">Why {selectedModel} is selected</h2>
          <p className="mt-1 text-sm text-ink-muted">
            {modelInfo.selection.rationale} The decision uses{' '}
            {modelInfo.selection.evidence_split}; final-test metrics are not
            used to retune or replace it.
          </p>
        </div>
        <div>
          <h2 className="section-heading">Evidence boundaries</h2>
          <p className="mt-1 text-sm leading-6 text-ink-muted">
            The {modelInfo.interval.nominal_coverage * 100}% prediction interval
            coverage is measured for rolling one-step final-test forecasts. The
            fixed-origin multi-step serving projection reuses its development-
            derived radius without a multi-horizon coverage claim. Anomaly
            outputs ({anomalies.length} flagged months) are exploratory signals,
            not verified events.
          </p>
        </div>
      </section>

      <section>
        <div className="mb-4">
          <h2 className="section-heading">Final-test model comparison</h2>
          <p className="mt-1 text-sm text-ink-muted">
            {modelInfo.metrics.final_test.start} to{' '}
            {modelInfo.metrics.final_test.end} · lower MAE is shown for
            evaluation, not model selection.
          </p>
        </div>
        <ModelComparisonTable selectedModel={selectedModel} models={models} />
      </section>
    </div>
  )
}

function datasetScope(period: string): string {
  return period.replace(/\d{2}:\d{2}$/, '').replace(' to ', '–')
}

export default OverviewPage
