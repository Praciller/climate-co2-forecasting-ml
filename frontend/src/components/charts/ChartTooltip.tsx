import { formatChartDate, formatPpm } from './chart-grammar'

export interface ChartTooltipItem { color?: string; name?: string | number; value?: unknown }
export interface ChartTooltipProps { active?: boolean; label?: unknown; payload?: readonly ChartTooltipItem[] }

export function ChartTooltip({ active, label, payload }: ChartTooltipProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip rounded-md border border-border bg-popover px-3 py-2 text-xs text-popover-foreground shadow-md">
      <p className="font-semibold">{formatChartDate(String(label ?? ''))}</p>
      <dl className="mt-1 space-y-1">
        {payload.map((item, index) => {
          const value = Array.isArray(item.value)
            ? item.value.map((part) => typeof part === 'number' ? formatPpm(part) : String(part)).join('–')
            : typeof item.value === 'number' ? formatPpm(item.value) : item.value == null ? '—' : String(item.value)
          return <div key={`${item.name ?? 'series'}-${index}`} className="flex gap-4"><dt className="text-muted-foreground">{item.name}</dt><dd className="tabular font-medium">{value}</dd></div>
        })}
      </dl>
    </div>
  )
}
