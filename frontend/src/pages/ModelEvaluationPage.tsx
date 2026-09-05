import { DataProvenance } from '../components/domain/DataProvenance'
import { ModelComparison } from '../components/domain/ModelComparison'
import { ModelSelectionSummary } from '../components/domain/ModelSelectionSummary'
import { MetricCard } from '../components/MetricCard'
import { PageHeader } from '../components/PageHeader'
import { ResidualPlotViewer } from '../components/ResidualPlotViewer'
import type { ModelInfo } from '../types/api'

interface ModelEvaluationPageProps { modelInfo: ModelInfo }

export function ModelEvaluationPage({ modelInfo }: ModelEvaluationPageProps) {
  const selectedModel = modelInfo.selection.selected_model
  const developmentMae = modelInfo.metrics.rolling_origin.aggregate[selectedModel]?.mae.mean
  const finalTestWinner = Object.entries(modelInfo.metrics.final_test.models).sort(([, left], [, right]) => left.mae - right.mae)[0]
  return (
    <div className="space-y-10">
      <PageHeader title="Model Evaluation" description="Development rolling-origin folds select the serving model. The untouched final test evaluates every candidate once afterward; its lowest score does not change the selection decision." />
      <ModelSelectionSummary selection={modelInfo.selection} developmentMae={developmentMae} foldCount={modelInfo.metrics.rolling_origin.fold_count} />
      <p className="-mt-5 text-sm text-muted-foreground"><strong className="text-foreground">{selectedModel}</strong> was selected using {modelInfo.selection.metric}; final-test ranking remains post-selection evidence.</p>
      <section className="grid gap-5 sm:grid-cols-3"><MetricCard label="Selected model" value={selectedModel} detail="Development selection evidence" /><MetricCard label="Development mean MAE" value={developmentMae?.toFixed(3) ?? '—'} detail="ppm · rolling-origin folds" /><MetricCard label="Lowest final-test MAE" value={finalTestWinner?.[1].mae.toFixed(3) ?? '—'} detail={`${finalTestWinner?.[0] ?? 'Unavailable'} · ${modelInfo.metrics.final_test.samples} held-out months · ppm`} /></section>
      <section aria-labelledby="final-test-evaluation-heading" className="rounded-lg border border-border bg-card p-5"><h2 id="final-test-evaluation-heading" className="section-heading">Final-test evaluation</h2><p className="mt-2 text-sm leading-6 text-muted-foreground">{finalTestWinner ? <><strong className="text-foreground">{finalTestWinner[0]}</strong> has the lowest final-test MAE. This is post-selection evaluation, not a new model-selection decision.</> : 'Final-test metrics are unavailable.'}</p></section>
      <section aria-labelledby="evaluation-comparison-heading"><h2 id="evaluation-comparison-heading" className="section-heading">Final-test comparison</h2><p className="mt-1 text-sm text-muted-foreground">{modelInfo.metrics.final_test.start} through {modelInfo.metrics.final_test.end}. Exponential Smoothing may rank lower on this held-out metric, but it does not replace the development-selected SARIMA.</p><div className="mt-4"><ModelComparison selectedModel={selectedModel} finalTest={modelInfo.metrics.final_test} /></div></section>
      <section className="grid gap-6 xl:grid-cols-2"><div><h2 className="section-heading">Residual timeline</h2><div className="mt-4"><ResidualPlotViewer src="/reports/residual_plot.png" alt={`Residual timeline for the selected model ${selectedModel}`} /></div></div><div><h2 className="section-heading">Error distribution</h2><div className="mt-4"><ResidualPlotViewer src="/reports/error_distribution.png" alt={`Error distribution for the selected model ${selectedModel}`} /></div></div></section>
      <DataProvenance dataset={modelInfo.dataset} preprocessing={modelInfo.preprocessing} />
    </div>
  )
}

export default ModelEvaluationPage
