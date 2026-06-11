import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { ForecastPoint, HistoricalPoint } from '../types/api'

interface ForecastChartProps {
  historical: HistoricalPoint[]
  forecast: ForecastPoint[]
}

export function ForecastChart({ forecast, historical }: ForecastChartProps) {
  const recentHistory = historical.slice(-60).map((point) => ({
    date: point.date,
    actual: point.co2,
  }))
  const forecastData = forecast.map((point) => ({
    date: point.date,
    prediction: point.prediction,
    interval: [point.lower, point.upper],
  }))
  const data = [...recentHistory, ...forecastData]
  const yMin =
    Math.min(
      ...recentHistory.map((point) => point.actual),
      ...forecast.map((point) => point.lower),
    ) - 2
  const yMax =
    Math.max(
      ...recentHistory.map((point) => point.actual),
      ...forecast.map((point) => point.upper),
    ) + 2

  return (
    <div
      className="h-[390px] min-w-0"
      role="img"
      aria-label="Historical CO2 and future forecast"
    >
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 800, height: 390 }}
      >
        <ComposedChart data={data} margin={{ top: 12, right: 10, left: 0, bottom: 8 }}>
          <CartesianGrid stroke="oklch(0.875 0.014 240)" strokeDasharray="3 5" />
          <XAxis
            dataKey="date"
            minTickGap={45}
            tick={{ fill: 'oklch(0.5 0.025 245)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[yMin, yMax]}
            width={48}
            tick={{ fill: 'oklch(0.5 0.025 245)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value, name) => [
              `${Number(value).toFixed(2)} ppm`,
              name,
            ]}
            contentStyle={{ fontSize: 12 }}
            wrapperClassName="chart-tooltip"
          />
          <Area
            type="monotone"
            dataKey="interval"
            fill="oklch(0.57 0.14 238 / 0.14)"
            stroke="transparent"
            name="95% interval"
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="oklch(0.245 0.025 245)"
            strokeWidth={2}
            dot={false}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="prediction"
            stroke="oklch(0.57 0.14 238)"
            strokeWidth={2.2}
            dot={false}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
