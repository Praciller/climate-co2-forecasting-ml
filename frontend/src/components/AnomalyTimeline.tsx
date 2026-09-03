import {
  CartesianGrid,
  Line,
  LineChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { AnomalyPoint, HistoricalPoint } from '../types/api'

interface AnomalyTimelineProps {
  anomalies: AnomalyPoint[]
  historical: HistoricalPoint[]
}

export function AnomalyTimeline({
  anomalies,
  historical,
}: AnomalyTimelineProps) {
  const anomalyMap = new Map(anomalies.map((point) => [point.date, point]))
  const data = historical.map((point) => ({
    ...point,
    isolationForest: anomalyMap.get(point.date)?.isolation_forest_anomaly
      ? point.co2
      : null,
    residual: anomalyMap.get(point.date)?.residual_anomaly ? point.co2 : null,
  }))

  return (
    <div
      className="h-[390px] min-w-0"
      role="img"
      aria-label="CO2 timeline with Isolation Forest and residual anomaly markers"
    >
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 800, height: 390 }}
      >
        <LineChart data={data} margin={{ top: 12, right: 10, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--color-rule)" strokeDasharray="3 5" />
          <XAxis
            dataKey="date"
            minTickGap={48}
            tick={{ fill: 'var(--color-ink-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={['dataMin - 3', 'dataMax + 3']}
            width={48}
            tick={{ fill: 'var(--color-ink-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value, name) => [
              `${Number(value).toFixed(2)} ppm`,
              name === 'isolationForest'
                ? 'Isolation Forest signal'
                : name === 'residual'
                  ? 'Residual-threshold signal'
                  : 'Monthly CO2',
            ]}
            contentStyle={{ fontSize: 12 }}
            wrapperClassName="chart-tooltip"
          />
          <Legend
            verticalAlign="top"
            height={28}
            wrapperStyle={{ fontSize: 12, color: 'var(--color-ink-muted)' }}
          />
          <Line
            type="monotone"
            dataKey="co2"
            stroke="var(--color-ink-muted)"
            strokeWidth={1.6}
            dot={false}
            name="Monthly observations"
          />
          <Line
            dataKey="isolationForest"
            stroke="transparent"
            dot={{ r: 4, fill: 'var(--color-anomaly)', strokeWidth: 0 }}
            name="Isolation Forest signal"
            connectNulls={false}
          />
          <Line
            dataKey="residual"
            stroke="transparent"
            dot={{
              r: 5,
              fill: 'var(--color-surface)',
              stroke: 'var(--color-ink)',
              strokeWidth: 2,
            }}
            name="Residual-threshold signal"
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
