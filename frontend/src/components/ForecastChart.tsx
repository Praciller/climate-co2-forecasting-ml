import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { ForecastPoint, HistoricalPoint } from '../types/api'

interface ForecastChartProps {
  historical: HistoricalPoint[]
  forecast: ForecastPoint[]
  forecastOrigin: string
  intervalNominalCoverage: number
}

export function ForecastChart({
  forecast,
  forecastOrigin,
  historical,
  intervalNominalCoverage,
}: ForecastChartProps) {
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
      aria-label={`Historical CO2 and fixed-origin forecast from ${forecastOrigin}`}
    >
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 800, height: 390 }}
      >
        <ComposedChart data={data} margin={{ top: 12, right: 10, left: 0, bottom: 8 }}>
          <CartesianGrid stroke="var(--color-rule)" strokeDasharray="3 5" />
          <XAxis
            dataKey="date"
            minTickGap={45}
            tick={{ fill: 'var(--color-ink-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[yMin, yMax]}
            width={48}
            tickFormatter={(value) => Number(value).toFixed(1)}
            tick={{ fill: 'var(--color-ink-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value, name) => {
              if (Array.isArray(value)) {
                return [
                  `${Number(value[0]).toFixed(2)}–${Number(value[1]).toFixed(2)} ppm`,
                  `${intervalNominalCoverage * 100}% prediction interval`,
                ]
              }
              return [`${Number(value).toFixed(2)} ppm`, name]
            }}
            contentStyle={{ fontSize: 12 }}
            wrapperClassName="chart-tooltip"
          />
          <Legend
            verticalAlign="top"
            height={28}
            wrapperStyle={{ fontSize: 12, color: 'var(--color-ink-muted)' }}
          />
          <Area
            type="monotone"
            dataKey="interval"
            fill="var(--color-accent-soft)"
            fillOpacity={0.8}
            stroke="transparent"
            name={`${intervalNominalCoverage * 100}% prediction interval`}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="var(--color-ink-muted)"
            strokeWidth={2}
            dot={false}
            name="Historical observations"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="prediction"
            stroke="var(--color-accent)"
            strokeWidth={2.2}
            dot={false}
            name="Fixed-origin forecast"
            connectNulls
          />
          <ReferenceLine
            x={forecastOrigin}
            stroke="var(--color-accent)"
            strokeDasharray="4 4"
            label={{
              value: 'Forecast origin',
              fill: 'var(--color-accent)',
              fontSize: 11,
              position: 'insideTopRight',
            }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
