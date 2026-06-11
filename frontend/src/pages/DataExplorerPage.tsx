import { MetricCard } from '../components/MetricCard'
import { TimeSeriesChart } from '../components/TimeSeriesChart'
import type { HistoricalPoint } from '../types/api'

interface DataExplorerPageProps {
  historical: HistoricalPoint[]
}

export function DataExplorerPage({ historical }: DataExplorerPageProps) {
  const values = historical.map((point) => point.co2)
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)

  return (
    <div className="space-y-9">
      <header>
        <h2 className="text-2xl font-semibold tracking-tight">Observed data</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">
          Weekly observations are resampled to month-end means and interpolated
          before leakage-safe lag and rolling features are created.
        </p>
      </header>
      <section className="grid gap-5 sm:grid-cols-3">
        <MetricCard
          label="Monthly rows"
          value={historical.length.toLocaleString()}
        />
        <MetricCard
          label="Observed range"
          value={`${minimum.toFixed(1)}-${maximum.toFixed(1)}`}
          detail="ppm"
        />
        <MetricCard label="Rolling signal" value="12 months" detail="Trailing mean" />
      </section>
      <section>
        <div className="mb-4">
          <h3 className="section-heading">Trend and rolling mean</h3>
          <p className="mt-1 text-sm text-ink-muted">
            The long-term rise coexists with a stable seasonal cycle.
          </p>
        </div>
        <TimeSeriesChart data={historical} height={470} />
      </section>
      <section className="border-y border-rule py-6">
        <h3 className="section-heading">Feature engineering</h3>
        <div className="mt-4 grid gap-5 text-sm leading-6 text-ink-muted md:grid-cols-3">
          <p>
            <strong className="text-ink">Lags:</strong> 1, 3, 6, and 12 months
            capture recent and annual history.
          </p>
          <p>
            <strong className="text-ink">Rolling:</strong> means and standard
            deviations use only prior observations.
          </p>
          <p>
            <strong className="text-ink">Calendar:</strong> month, quarter, and
            year preserve seasonal and trend context.
          </p>
        </div>
      </section>
    </div>
  )
}

export default DataExplorerPage
