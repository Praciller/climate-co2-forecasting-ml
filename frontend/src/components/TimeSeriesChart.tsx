import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { HistoricalPoint } from '../types/api'

interface TimeSeriesChartProps {
  data: HistoricalPoint[]
  height?: number
  showRollingMean?: boolean
}

const formatDate = (value: string) =>
  new Intl.DateTimeFormat('en', { month: 'short', year: 'numeric' }).format(
    new Date(value),
  )

export function TimeSeriesChart({
  data,
  height = 360,
  showRollingMean = true,
}: TimeSeriesChartProps) {
  return (
    <div
      className="min-w-0"
      style={{ height }}
      role="img"
      aria-label="Monthly atmospheric CO2 time series"
    >
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 800, height }}
      >
        <LineChart data={data} margin={{ top: 12, right: 10, bottom: 6, left: 0 }}>
          <CartesianGrid stroke="oklch(0.875 0.014 240)" strokeDasharray="3 5" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
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
            unit=" ppm"
          />
          <Tooltip
            labelFormatter={(value) => formatDate(String(value))}
            formatter={(value, name) => [
              `${Number(value).toFixed(2)} ppm`,
              name === 'co2' ? 'Monthly CO2' : '12-month mean',
            ]}
            contentStyle={{ fontSize: 12 }}
            wrapperClassName="chart-tooltip"
          />
          <Line
            type="monotone"
            dataKey="co2"
            stroke="oklch(0.57 0.14 238)"
            strokeWidth={1.8}
            dot={false}
          />
          {showRollingMean ? (
            <Line
              type="monotone"
              dataKey="rolling_mean_12"
              stroke="oklch(0.42 0.05 245)"
              strokeWidth={2.2}
              dot={false}
              connectNulls
            />
          ) : null}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
