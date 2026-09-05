import { DataProvenance } from '../components/domain/DataProvenance'
import { HistoricalScope } from '../components/domain/HistoricalScope'
import { LimitationCallout } from '../components/domain/LimitationCallout'
import { MetricDefinition } from '../components/domain/MetricDefinition'
import { ModelComparison } from '../components/domain/ModelComparison'
import { ModelSelectionSummary } from '../components/domain/ModelSelectionSummary'
import { PageHeader } from '../components/PageHeader'
import { TimeSeriesChart } from '../components/TimeSeriesChart'
import type { AnomalyPoint, HistoricalPoint, ModelInfo } from '../types/api'

interface OverviewPageProps { anomalies: AnomalyPoint[]; historical: HistoricalPoint[]; modelInfo: ModelInfo }

export function OverviewPage({ anomalies, historical, modelInfo }: OverviewPageProps) {
  const first = historical[0]
  const latest = historical.at(-1)
  const selectedModel = modelInfo.selection.selected_model
  const selectedMetrics = modelInfo.metrics.final_test.models[selectedModel]
  const developmentMae = modelInfo.metrics.rolling_origin.aggregate[selectedModel]?.mae.mean
  const finalTestWinnerEntry = Object.entries(modelInfo.metrics.final_test.models).sort(([, left], [, right]) => left.mae - right.mae)[0]
  const measuredCoverage = modelInfo.interval.observed_test_coverage * 100
  const measuredCoverageSamples = Math.round(modelInfo.interval.observed_test_coverage * modelInfo.interval.evaluation_samples)

  return (
    <div className="space-y-10">
      <PageHeader title="Overview" description="A reproducible workbench for the packaged Mauna Loa dataset, governed model selection, held-out evaluation, and exploratory signals." />
      <section className="grid gap-8 border-b border-border pb-9 xl:grid-cols-[1.5fr_1fr]">
        <div><h2 className="max-w-3xl text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Historical CO₂ evidence, from source to forecast.</h2><p className="mt-4 max-w-2xl text-sm leading-6 text-muted-foreground">This dashboard does not ingest current atmospheric data.</p></div>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-5 text-sm"><div><dt className="text-xs uppercase tracking-[0.12em] text-muted-foreground">Dataset</dt><dd className="mt-1 font-medium">Mauna Loa CO₂</dd></div><div><dt className="text-xs uppercase tracking-[0.12em] text-muted-foreground">Scope</dt><dd className="mt-1 font-medium">Historical only</dd></div><div><dt className="text-xs uppercase tracking-[0.12em] text-muted-foreground">Frequency</dt><dd className="mt-1 font-medium">{modelInfo.dataset.frequency}</dd></div><div><dt className="text-xs uppercase tracking-[0.12em] text-muted-foreground">Unit</dt><dd className="mt-1 font-medium">{modelInfo.dataset.unit}</dd></div></dl>
      </section>
      <HistoricalScope period={modelInfo.dataset.period} frequency={modelInfo.dataset.frequency} unit={modelInfo.dataset.unit} />
      <section aria-labelledby="overview-chart-heading"><div className="mb-4 flex flex-wrap items-end justify-between gap-3"><div><h2 id="overview-chart-heading" className="section-heading">Observed monthly concentration</h2><p className="mt-1 text-sm text-muted-foreground">{first?.date ?? '—'} to {latest?.date ?? '—'} · month-end means in ppm.</p></div><p className="tabular text-sm font-medium">Latest observation {latest ? `${latest.co2.toFixed(2)} ppm` : '—'}</p></div><TimeSeriesChart data={historical} /></section>
      <dl className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"><MetricDefinition label="Selected by development" value={selectedModel} detail={`${modelInfo.metrics.rolling_origin.fold_count} rolling-origin folds · ${developmentMae?.toFixed(3) ?? '—'} ppm MAE`} /><MetricDefinition label="Selected model · final test" value={selectedMetrics ? `${selectedMetrics.mae.toFixed(3)} ppm` : '—'} detail="Post-selection evaluation" /><MetricDefinition label="Lowest final-test MAE" value={finalTestWinnerEntry ? `${finalTestWinnerEntry[1].mae.toFixed(3)} ppm` : '—'} detail={`${finalTestWinnerEntry?.[0] ?? 'Unavailable'} · does not change selection`} /><MetricDefinition label="Measured one-step coverage" value={`${measuredCoverage.toFixed(1)}%`} detail={`${modelInfo.interval.nominal_coverage * 100}% nominal · ${measuredCoverageSamples}/${modelInfo.interval.evaluation_samples} test months`} /></dl>
      <ModelSelectionSummary selection={modelInfo.selection} developmentMae={developmentMae} foldCount={modelInfo.metrics.rolling_origin.fold_count} />
      <LimitationCallout>Prediction interval coverage is measured for rolling one-step final-test forecasts. Fixed-origin multi-step projections reuse a development-derived radius without a multi-horizon coverage claim. Anomaly outputs ({anomalies.length} flagged months) are exploratory signals, not verified events.</LimitationCallout>
      <DataProvenance dataset={modelInfo.dataset} preprocessing={modelInfo.preprocessing} />
      <section aria-labelledby="overview-comparison-heading"><h2 id="overview-comparison-heading" className="section-heading">Final-test model comparison</h2><p className="mt-1 text-sm text-muted-foreground">{modelInfo.metrics.final_test.start} to {modelInfo.metrics.final_test.end} · lower MAE is evaluation evidence, not model selection.</p><div className="mt-4"><ModelComparison selectedModel={selectedModel} finalTest={modelInfo.metrics.final_test} /></div></section>
    </div>
  )
}

export default OverviewPage
