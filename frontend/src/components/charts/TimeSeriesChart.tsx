import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { HistoricalPoint } from '../../types/api'
import { ChartLegend } from './ChartLegend'
import { ChartTooltip } from './ChartTooltip'
import { chartColors, formatChartDate, formatPpm } from './chart-grammar'

export interface TimeSeriesChartProps { data: HistoricalPoint[]; height?: number; showRollingMean?: boolean }

export function TimeSeriesChart({ data, height = 360, showRollingMean = true }: TimeSeriesChartProps) {
  if (!data.length) return <p className="rounded-lg border border-dashed border-border p-6 text-sm text-muted-foreground">Historical observations are unavailable for this chart.</p>
  return (
    <div className="min-w-0" style={{ height }} role="img" aria-label="Monthly atmospheric CO2 time series">
      <ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 800, height }}>
        <LineChart accessibilityLayer data={data} margin={{ top: 12, right: 10, bottom: 6, left: 0 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 5" />
          <XAxis dataKey="date" tickFormatter={formatChartDate} minTickGap={48} tick={{ fill: chartColors.historical, fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis domain={['dataMin - 3', 'dataMax + 3']} width={48} tickFormatter={(value) => formatPpm(Number(value))} tick={{ fill: chartColors.historical, fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={(props) => <ChartTooltip {...props} />} />
          <Legend content={(props) => <ChartLegend {...props} />} verticalAlign="top" height={30} />
          <Line type="monotone" dataKey="co2" stroke={chartColors.historical} strokeWidth={1.8} dot={false} name="Monthly observations" />
          {showRollingMean ? <Line type="monotone" dataKey="rolling_mean_12" stroke="var(--color-foreground)" strokeWidth={2.2} dot={false} name="12-month rolling mean" connectNulls /> : null}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
