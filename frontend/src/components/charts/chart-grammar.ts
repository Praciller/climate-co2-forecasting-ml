export const chartColors: Readonly<Record<'historical' | 'forecast' | 'interval' | 'anomaly' | 'grid', string>> = {
  historical: 'var(--color-chart-historical)',
  forecast: 'var(--color-chart-forecast)',
  interval: 'var(--color-chart-interval)',
  anomaly: 'var(--color-chart-anomaly)',
  grid: 'var(--color-chart-grid)',
}

export function formatChartDate(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('en', { month: 'short', year: 'numeric' }).format(date)
}

export function formatPpm(value: number | null | undefined): string {
  return value === null || value === undefined || Number.isNaN(value) ? '—' : `${value.toFixed(2)} ppm`
}
