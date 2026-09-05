import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AnomalyPoint, HistoricalPoint } from '../../types/api'
import { ChartLegend } from './ChartLegend'
import { ChartTooltip } from './ChartTooltip'
import { chartColors, formatChartDate, formatPpm } from './chart-grammar'

export interface AnomalyTimelineProps { anomalies: AnomalyPoint[]; historical: HistoricalPoint[] }

export function AnomalyTimeline({ anomalies, historical }: AnomalyTimelineProps) {
  if (!historical.length) return <p className="rounded-lg border border-dashed border-border p-6 text-sm text-muted-foreground">Historical observations are unavailable for this timeline.</p>
  const anomalyMap = new Map(anomalies.map((point) => [point.date, point]))
  const data = historical.map((point) => ({ ...point, isolationForest: anomalyMap.get(point.date)?.isolation_forest_anomaly ? point.co2 : null, residual: anomalyMap.get(point.date)?.residual_anomaly ? point.co2 : null }))
  return (
    <div className="h-[390px] min-w-0" role="img" aria-label="CO2 timeline with Isolation Forest and residual anomaly markers">
      <ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 800, height: 390 }}>
        <LineChart accessibilityLayer data={data} margin={{ top: 12, right: 10, bottom: 8, left: 0 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 5" />
          <XAxis dataKey="date" tickFormatter={formatChartDate} minTickGap={48} tick={{ fill: chartColors.historical, fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis domain={['dataMin - 3', 'dataMax + 3']} width={48} tickFormatter={(value) => formatPpm(Number(value))} tick={{ fill: chartColors.historical, fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={(props) => <ChartTooltip {...props} />} />
          <Legend content={(props) => <ChartLegend {...props} />} verticalAlign="top" height={30} />
          <Line type="monotone" dataKey="co2" stroke={chartColors.historical} strokeWidth={1.6} dot={false} name="Monthly observations" />
          <Line dataKey="isolationForest" stroke="transparent" dot={{ r: 4, fill: chartColors.anomaly, strokeWidth: 0 }} name="Isolation Forest signal" connectNulls={false} />
          <Line dataKey="residual" stroke="transparent" dot={{ r: 5, fill: 'var(--color-background)', stroke: chartColors.anomaly, strokeWidth: 2 }} name="Residual-threshold signal" connectNulls={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
