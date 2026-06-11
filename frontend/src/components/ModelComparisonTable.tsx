import type { ModelMetrics } from '../types/api'

interface ModelComparisonTableProps {
  bestModel?: string
  models: Record<string, ModelMetrics>
}

export function ModelComparisonTable({
  bestModel,
  models,
}: ModelComparisonTableProps) {
  const rows = Object.entries(models).sort(([, left], [, right]) => left.mae - right.mae)

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-rule text-xs uppercase tracking-[0.1em] text-ink-muted">
            <th className="px-3 py-3 font-semibold">Model</th>
            <th className="px-3 py-3 text-right font-semibold">MAE</th>
            <th className="px-3 py-3 text-right font-semibold">RMSE</th>
            <th className="px-3 py-3 text-right font-semibold">MAPE</th>
            <th className="px-3 py-3 text-right font-semibold">sMAPE</th>
            <th className="px-3 py-3 text-right font-semibold">MASE</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([name, metrics]) => (
            <tr
              key={name}
              className={`border-b border-rule/70 ${
                name === bestModel
                  ? 'bg-accent-soft/70'
                  : 'hover:bg-surface-muted/60'
              }`}
            >
              <td className="px-3 py-3 font-medium">
                {name}
                {name === bestModel ? (
                  <span className="ml-2 text-xs font-semibold text-accent">
                    Best MAE
                  </span>
                ) : null}
              </td>
              {(['mae', 'rmse', 'mape', 'smape', 'mase'] as const).map((key) => (
                <td
                  key={key}
                  className="tabular px-3 py-3 text-right text-ink-muted"
                >
                  {metrics[key].toFixed(3)}
                  {key === 'mape' || key === 'smape' ? '%' : ''}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
