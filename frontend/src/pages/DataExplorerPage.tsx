import { MetricCard } from '../components/MetricCard'
import { TimeSeriesChart } from '../components/TimeSeriesChart'
import type { HistoricalPoint, ModelInfo } from '../types/api'

interface DataExplorerPageProps {
  historical: HistoricalPoint[]
  modelInfo: ModelInfo
}

export function DataExplorerPage({
  historical,
  modelInfo,
}: DataExplorerPageProps) {
  const values = historical.map((point) => point.co2)
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  const first = historical[0]
  const latest = historical.at(-1)
  const { dataset, preprocessing } = modelInfo

  return (
    <div className="space-y-10">
      <header>
        <h2 className="text-2xl font-semibold tracking-tight">
          Historical data workbench
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">
          Inspect the packaged {dataset.name} after its documented causal
          preparation. This is historical evidence, not a live atmospheric
          reading.
        </p>
      </header>
      <section className="grid gap-5 sm:grid-cols-3">
        <MetricCard
          label="Monthly rows"
          value={historical.length.toLocaleString()}
          detail={`${first?.date ?? '—'} to ${latest?.date ?? '—'}`}
        />
        <MetricCard
          label="Observed range · ppm"
          value={`${minimum.toFixed(1)}-${maximum.toFixed(1)}`}
          detail={`Source unit: ${dataset.unit}`}
        />
        <MetricCard
          label="Source observations"
          value={dataset.observed_values.toLocaleString()}
          detail={`${dataset.missing_values} missing of ${dataset.weekly_calendar_rows.toLocaleString()} calendar rows`}
        />
      </section>
      <section className="grid gap-6 border-y border-rule py-6 md:grid-cols-2">
        <div>
          <h3 className="section-heading">Dataset provenance</h3>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-[0.1em] text-ink-muted">
                Source module
              </dt>
              <dd className="mt-1 font-medium">{dataset.source_module}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.1em] text-ink-muted">
                Packaged period
              </dt>
              <dd className="mt-1 font-medium">{dataset.period}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.1em] text-ink-muted">
                Frequency
              </dt>
              <dd className="mt-1 font-medium">{dataset.frequency}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.1em] text-ink-muted">
                Historical only
              </dt>
              <dd className="mt-1 font-medium">
                {dataset.historical_only ? 'Yes' : 'No'}
              </dd>
            </div>
          </dl>
        </div>
        <div>
          <h3 className="section-heading">Preparation lineage</h3>
          <dl className="mt-4 space-y-3 text-sm leading-6">
            <div>
              <dt className="text-xs uppercase tracking-[0.1em] text-ink-muted">
                Monthly aggregation
              </dt>
              <dd className="mt-1 text-ink">{preprocessing.monthly_aggregation}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.1em] text-ink-muted">
                Missing-month strategy
              </dt>
              <dd className="mt-1 text-ink">{preprocessing.missing_month_strategy}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.1em] text-ink-muted">
                Feature contract
              </dt>
              <dd className="mt-1 text-ink">{preprocessing.feature_contract}</dd>
            </div>
          </dl>
        </div>
      </section>
      <section>
        <div className="mb-4">
          <h3 className="section-heading">Monthly concentration and rolling mean</h3>
          <p className="mt-1 text-sm text-ink-muted">
            Month-end CO₂ means and trailing 12-month mean, shown in ppm.
          </p>
        </div>
        <TimeSeriesChart data={historical} height={470} />
      </section>
    </div>
  )
}

export default DataExplorerPage
