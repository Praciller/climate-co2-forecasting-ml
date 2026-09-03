import { MetricCard } from '../components/MetricCard'
import { ModelComparisonTable } from '../components/ModelComparisonTable'
import { ResidualPlotViewer } from '../components/ResidualPlotViewer'
import type { ModelInfo } from '../types/api'

interface ModelEvaluationPageProps {
  modelInfo: ModelInfo
}

export function ModelEvaluationPage({ modelInfo }: ModelEvaluationPageProps) {
  const selectedModel = modelInfo.selection.selected_model
  const models = modelInfo.metrics.final_test.models
  const finalTestWinnerEntry = Object.entries(models).sort(
    ([, left], [, right]) => left.mae - right.mae,
  )[0]
  const finalTestWinner = finalTestWinnerEntry?.[0]
  const finalTestWinnerMetrics = finalTestWinnerEntry?.[1]
  const developmentMae =
    modelInfo.metrics.rolling_origin.aggregate[selectedModel]?.mae.mean

  return (
    <div className="space-y-9">
      <header>
        <h2 className="text-2xl font-semibold tracking-tight">
          Selection and held-out evaluation
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-ink-muted">
          Development rolling-origin folds select the serving model. The
          untouched final test evaluates every candidate once afterward; its
          lowest score does not change the selection decision.
        </p>
      </header>
      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard
          label="Selected model"
          value={selectedModel}
          detail={`Selected by ${modelInfo.metrics.rolling_origin.fold_count} rolling-origin development folds`}
        />
        <MetricCard
          label="Development mean MAE"
          value={developmentMae?.toFixed(3) ?? '—'}
          detail="Selection evidence · ppm"
        />
        <MetricCard
          label="Lowest final-test MAE"
          value={finalTestWinnerMetrics?.mae.toFixed(3) ?? '—'}
          detail={`${finalTestWinner ?? 'Unavailable'} · ${modelInfo.metrics.final_test.samples} held-out months · ppm`}
        />
      </section>
      <section className="grid gap-5 border-y border-rule py-6 md:grid-cols-2">
        <div>
          <h3 className="section-heading">Development selection</h3>
          <p className="mt-2 text-sm leading-6 text-ink-muted">
            <strong className="text-ink">{selectedModel}</strong> was selected
            using {modelInfo.selection.metric}. {modelInfo.selection.rationale}
          </p>
        </div>
        <div>
          <h3 className="section-heading">Final-test evaluation</h3>
          <p className="mt-2 text-sm leading-6 text-ink-muted">
            {finalTestWinner ? (
              <>
                <strong className="text-ink">{finalTestWinner}</strong> has the
                lowest final-test MAE. This is post-selection evaluation, not a
                new model-selection decision.
              </>
            ) : (
              'Final-test metrics are unavailable.'
            )}
          </p>
        </div>
      </section>
      <section>
        <h3 className="section-heading">Final-test comparison</h3>
        <div className="mt-4">
          <ModelComparisonTable selectedModel={selectedModel} models={models} />
        </div>
        <p className="mt-3 text-xs leading-5 text-ink-muted">
          Metrics are final-test evidence for the locked period of{' '}
          {modelInfo.metrics.final_test.start} through{' '}
          {modelInfo.metrics.final_test.end}. MASE below 1 beats the seasonal
          naive scale.
        </p>
      </section>
      <section className="grid gap-6 xl:grid-cols-2">
        <div>
          <h3 className="section-heading">Residual timeline</h3>
          <div className="mt-4">
            <ResidualPlotViewer
              src="/reports/residual_plot.png"
              alt={`Residual timeline for the selected model ${selectedModel}`}
            />
          </div>
        </div>
        <div>
          <h3 className="section-heading">Error distribution</h3>
          <div className="mt-4">
            <ResidualPlotViewer
              src="/reports/error_distribution.png"
              alt={`Error distribution for the selected model ${selectedModel}`}
            />
          </div>
        </div>
      </section>
    </div>
  )
}

export default ModelEvaluationPage
