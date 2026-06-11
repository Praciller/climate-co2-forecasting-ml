import {
  CartesianGrid,
  Line,
  LineChart,
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
  const anomalyMap = new Map(anomalies.map((point) => [point.date, point.co2]))
  const data = historical.map((point) => ({
    ...point,
    anomaly: anomalyMap.get(point.date) ?? null,
  }))

  return (
    <div
      className="h-[390px] min-w-0"
      role="img"
      aria-label="CO2 timeline with anomaly markers"
    >
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 800, height: 390 }}
      >
        <LineChart data={data} margin={{ top: 12, right: 10, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="oklch(0.875 0.014 240)" strokeDasharray="3 5" />
          <XAxis
            dataKey="date"
            minTickGap={48}
            tick={{ fill: 'oklch(0.5 0.025 245)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={['dataMin - 3', 'dataMax + 3']}
            width={48}
            tick={{ fill: 'oklch(0.5 0.025 245)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value, name) => [
              `${Number(value).toFixed(2)} ppm`,
              name === 'anomaly' ? 'Exploratory anomaly' : 'Monthly CO2',
            ]}
            contentStyle={{ fontSize: 12 }}
            wrapperClassName="chart-tooltip"
          />
          <Line
            type="monotone"
            dataKey="co2"
            stroke="oklch(0.57 0.14 238)"
            strokeWidth={1.6}
            dot={false}
          />
          <Line
            dataKey="anomaly"
            stroke="transparent"
            dot={{ r: 4, fill: 'oklch(0.68 0.15 65)', strokeWidth: 0 }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
