import { DataProvenance } from '../components/domain/DataProvenance'
import { HistoricalScope } from '../components/domain/HistoricalScope'
import { MetricDefinition } from '../components/domain/MetricDefinition'
import { PageHeader } from '../components/PageHeader'
import { TimeSeriesChart } from '../components/TimeSeriesChart'
import type { HistoricalPoint, ModelInfo } from '../types/api'

interface DataExplorerPageProps { historical: HistoricalPoint[]; modelInfo: ModelInfo }

export function DataExplorerPage({ historical, modelInfo }: DataExplorerPageProps) {
  const values = historical.map((point) => point.co2)
  const first = historical[0]
  const latest = historical.at(-1)
  const { dataset, preprocessing } = modelInfo
  const range = values.length ? `${Math.min(...values).toFixed(1)}–${Math.max(...values).toFixed(1)}` : '—'
  return (
    <div className="space-y-10">
      <PageHeader title="Data Explorer" description={`Inspect the packaged ${dataset.name} after its documented causal preparation. This is historical evidence, not a live atmospheric reading.`} />
      <HistoricalScope period={dataset.period} frequency={dataset.frequency} unit={dataset.unit} />
      <dl className="grid gap-5 sm:grid-cols-3"><MetricDefinition label="Monthly rows" value={historical.length.toLocaleString()} detail={`${first?.date ?? '—'} to ${latest?.date ?? '—'}`} /><MetricDefinition label="Observed range · ppm" value={range} detail={`Source unit: ${dataset.unit}`} /><MetricDefinition label="Source observations" value={dataset.observed_values.toLocaleString()} detail={`${dataset.missing_values} missing of ${dataset.weekly_calendar_rows.toLocaleString()} calendar rows`} /></dl>
      <DataProvenance dataset={dataset} preprocessing={preprocessing} />
      <section aria-labelledby="data-chart-heading"><h2 id="data-chart-heading" className="section-heading">Monthly concentration and rolling mean</h2><p className="mt-1 text-sm text-muted-foreground">Month-end CO₂ means and trailing 12-month mean, shown in ppm.</p><div className="mt-4"><TimeSeriesChart data={historical} height={470} /></div></section>
    </div>
  )
}

export default DataExplorerPage
