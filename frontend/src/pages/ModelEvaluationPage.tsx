import { DataProvenance } from '../components/domain/DataProvenance'
import { ModelComparison } from '../components/domain/ModelComparison'
import { ModelSelectionSummary } from '../components/domain/ModelSelectionSummary'
import { PageHeader } from '../components/PageHeader'
import { ResidualPlotViewer } from '../components/ResidualPlotViewer'
import type { ModelInfo } from '../types/api'

interface ModelEvaluationPageProps { modelInfo: ModelInfo }

export function ModelEvaluationPage({ modelInfo }: ModelEvaluationPageProps) {
  const selectedModel = modelInfo.selection.selected_model
  const developmentMae = modelInfo.metrics.rolling_origin.aggregate[selectedModel]?.mae.mean
  const finalTestWinnerEntry = Object.entries(modelInfo.metrics.final_test.models).sort(([, left], [, right]) => left.mae - right.mae)[0]
  const finalTestWinner = finalTestWinnerEntry ? { model: finalTestWinnerEntry[0], mae: finalTestWinnerEntry[1].mae, samples: modelInfo.metrics.final_test.samples } : undefined
  return (
    <div className="space-y-10">
      <PageHeader title="Model Evaluation" description="Development rolling-origin folds select the serving model. The untouched final test evaluates every candidate once afterward; its lowest score does not change the selection decision." />
      <ModelSelectionSummary selection={modelInfo.selection} developmentMae={developmentMae} finalTestWinner={finalTestWinner} foldCount={modelInfo.metrics.rolling_origin.fold_count} />
      <section aria-labelledby="evaluation-comparison-heading"><h2 id="evaluation-comparison-heading" className="section-heading">Final-test comparison</h2><p className="mt-1 text-sm text-muted-foreground">{modelInfo.metrics.final_test.start} through {modelInfo.metrics.final_test.end}. Lower MAE is post-selection evaluation evidence; it does not replace the development-selected serving model.</p><div className="mt-4"><ModelComparison selectedModel={selectedModel} finalTest={modelInfo.metrics.final_test} /></div></section>
      <section className="grid gap-6 xl:grid-cols-2"><div><h2 className="section-heading">Residual timeline</h2><div className="mt-4"><ResidualPlotViewer src="/reports/residual_plot.png" alt={`Residual timeline for the selected model ${selectedModel}`} /></div></div><div><h2 className="section-heading">Error distribution</h2><div className="mt-4"><ResidualPlotViewer src="/reports/error_distribution.png" alt={`Error distribution for the selected model ${selectedModel}`} /></div></div></section>
      <DataProvenance dataset={modelInfo.dataset} preprocessing={modelInfo.preprocessing} />
    </div>
  )
}

export default ModelEvaluationPage
