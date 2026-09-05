export interface ChartLegendItem { color?: string; value?: string | number }
export interface ChartLegendProps { payload?: readonly ChartLegendItem[] }

export function ChartLegend({ payload }: ChartLegendProps) {
  if (!payload?.length) return null
  return <ul className="flex flex-wrap gap-x-4 gap-y-2 text-xs text-muted-foreground" aria-label="Chart legend">{payload.map((item, index) => <li key={`${item.value ?? 'series'}-${index}`} className="flex items-center gap-2"><span className="size-2.5 rounded-sm" style={{ backgroundColor: item.color }} aria-hidden="true" />{item.value}</li>)}</ul>
}
