import { MetricCard } from '../components/MetricCard'
import { ModelComparisonTable } from '../components/ModelComparisonTable'
import { ResidualPlotViewer } from '../components/ResidualPlotViewer'
import type { ModelInfo } from '../types/api'

interface ModelEvaluationPageProps {
  modelInfo: ModelInfo
}

export function ModelEvaluationPage({ modelInfo }: ModelEvaluationPageProps) {
  const models = modelInfo.metrics.models ?? {}
  const bestModel = modelInfo.metrics.best_model
  const bestMetrics = bestModel ? models[bestModel] : undefined

  return (
    <div className="space-y-9">
      <header>
        <h2 className="text-2xl font-semibold tracking-tight">
          Held-out model evaluation
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-ink-muted">
          Baseline, statistical, tree-based, and deep-learning forecasts use
          the same chronological test months. MASE below 1 beats the seasonal
          naive scale.
        </p>
      </header>
      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard label="Best model" value={bestModel ?? 'Pending'} />
        <MetricCard label="MAE" value={bestMetrics?.mae.toFixed(3) ?? 'Pending'} />
        <MetricCard
          label="RMSE"
          value={bestMetrics?.rmse.toFixed(3) ?? 'Pending'}
        />
        <MetricCard
          label="sMAPE"
          value={bestMetrics ? `${bestMetrics.smape.toFixed(3)}%` : 'Pending'}
        />
        <MetricCard
          label="MASE"
          value={bestMetrics?.mase.toFixed(3) ?? 'Pending'}
        />
      </section>
      <section>
        <h3 className="section-heading">Comparison table</h3>
        <div className="mt-4">
          <ModelComparisonTable bestModel={bestModel} models={models} />
        </div>
      </section>
      <section className="grid gap-6 xl:grid-cols-2">
        <div>
          <h3 className="section-heading">Residual timeline</h3>
          <div className="mt-4">
            <ResidualPlotViewer
              src="/reports/residual_plot.png"
              alt={`Residual timeline for ${bestModel ?? 'the best model'}`}
            />
          </div>
        </div>
        <div>
          <h3 className="section-heading">Error distribution</h3>
          <div className="mt-4">
            <ResidualPlotViewer
              src="/reports/error_distribution.png"
              alt={`Error distribution for ${bestModel ?? 'the best model'}`}
            />
          </div>
        </div>
      </section>
    </div>
  )
}

export default ModelEvaluationPage
