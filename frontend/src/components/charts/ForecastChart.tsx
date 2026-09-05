import { Area, CartesianGrid, ComposedChart, Legend, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { ForecastPoint, HistoricalPoint } from '../../types/api'
import { ChartLegend } from './ChartLegend'
import { ChartTooltip } from './ChartTooltip'
import { chartColors, formatChartDate, formatPpm } from './chart-grammar'

export interface ForecastChartProps { historical: HistoricalPoint[]; forecast: ForecastPoint[]; forecastOrigin: string; intervalNominalCoverage: number }

export function ForecastChart({ forecast, forecastOrigin, historical, intervalNominalCoverage }: ForecastChartProps) {
  const recentHistory = historical.slice(-60).map((point) => ({ date: point.date, actual: point.co2 }))
  const forecastData = forecast.map((point) => ({ date: point.date, prediction: point.prediction, interval: [point.lower, point.upper] as const }))
  const data = [...recentHistory, ...forecastData]
  if (!data.length) return <p className="rounded-lg border border-dashed border-border p-6 text-sm text-muted-foreground">Forecast evidence is unavailable for this chart.</p>
  const values = [...recentHistory.map((point) => point.actual), ...forecast.flatMap((point) => [point.lower, point.upper])]
  const yMin = Math.min(...values) - 2
  const yMax = Math.max(...values) + 2
  return (
    <div className="h-[390px] min-w-0" role="img" aria-label={`Historical CO2 and fixed-origin forecast from ${forecastOrigin}`}>
      <ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 800, height: 390 }}>
        <ComposedChart accessibilityLayer data={data} margin={{ top: 12, right: 10, left: 0, bottom: 8 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 5" />
          <XAxis dataKey="date" tickFormatter={formatChartDate} minTickGap={45} tick={{ fill: chartColors.historical, fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis domain={[yMin, yMax]} width={48} tickFormatter={(value) => formatPpm(Number(value))} tick={{ fill: chartColors.historical, fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={(props) => <ChartTooltip {...props} />} />
          <Legend content={(props) => <ChartLegend {...props} />} verticalAlign="top" height={30} />
          <Area type="monotone" dataKey="interval" fill={chartColors.interval} fillOpacity={0.35} stroke="transparent" name={`${intervalNominalCoverage * 100}% prediction interval`} />
          <Line type="monotone" dataKey="actual" stroke={chartColors.historical} strokeWidth={2} dot={false} name="Historical observations" connectNulls />
          <Line type="monotone" dataKey="prediction" stroke={chartColors.forecast} strokeWidth={2.2} dot={false} name="Fixed-origin forecast" connectNulls />
          <ReferenceLine x={forecastOrigin} stroke={chartColors.forecast} strokeDasharray="4 4" label={{ value: 'Forecast origin', fill: chartColors.forecast, fontSize: 11, position: 'insideTopRight' }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
