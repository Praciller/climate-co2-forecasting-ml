import type { ModelMetrics } from '../types/api'

interface ModelComparisonTableProps {
  selectedModel: string
  models: Record<string, ModelMetrics>
}

export function ModelComparisonTable({
  models,
  selectedModel,
}: ModelComparisonTableProps) {
  const rows = Object.entries(models).sort(([, left], [, right]) => left.mae - right.mae)
  const lowestFinalTestModel = rows[0]?.[0]

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-rule text-xs uppercase tracking-[0.1em] text-ink-muted">
            <th scope="col" className="px-3 py-3 font-semibold">Model</th>
            <th scope="col" className="px-3 py-3 font-semibold">Development status</th>
            <th scope="col" className="px-3 py-3 text-right font-semibold">Final-test MAE</th>
            <th scope="col" className="px-3 py-3 text-right font-semibold">RMSE</th>
            <th scope="col" className="px-3 py-3 text-right font-semibold">MAPE</th>
            <th scope="col" className="px-3 py-3 text-right font-semibold">sMAPE</th>
            <th scope="col" className="px-3 py-3 text-right font-semibold">MASE</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([name, metrics]) => (
            <tr
              key={name}
              className={`border-b border-rule/70 ${
                name === selectedModel
                  ? 'bg-accent-soft/70'
                  : 'hover:bg-surface-muted/60'
              }`}
            >
              <td className="px-3 py-3 font-medium">
                {name}
              </td>
              <td className="px-3 py-3 text-xs text-ink-muted">
                <div className="flex flex-wrap gap-1.5">
                  {name === selectedModel ? (
                    <span className="rounded border border-accent px-1.5 py-0.5 font-semibold text-accent">
                      Selected by development
                    </span>
                  ) : null}
                  {name === lowestFinalTestModel ? (
                    <span className="rounded border border-rule px-1.5 py-0.5 font-semibold text-ink">
                      Lowest final-test MAE
                    </span>
                  ) : null}
                </div>
              </td>
              <td className="tabular px-3 py-3 text-right text-ink-muted">
                {formatMetric(metrics.mae)}
              </td>
              <td className="tabular px-3 py-3 text-right text-ink-muted">
                {formatMetric(metrics.rmse)}
              </td>
              <td className="tabular px-3 py-3 text-right text-ink-muted">
                {formatMetric(metrics.mape, '%')}
              </td>
              <td className="tabular px-3 py-3 text-right text-ink-muted">
                {formatMetric(metrics.smape, '%')}
              </td>
              <td className="tabular px-3 py-3 text-right text-ink-muted">
                {formatMetric(metrics.mase)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function formatMetric(value: number | null, suffix = ''): string {
  return value === null ? '—' : `${value.toFixed(3)}${suffix}`
}
