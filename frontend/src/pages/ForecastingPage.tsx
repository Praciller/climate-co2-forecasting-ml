import { useEffect, useState } from 'react'

import { ErrorMessage } from '../components/ErrorMessage'
import { ForecastChart } from '../components/ForecastChart'
import { LoadingState } from '../components/LoadingState'
import { getForecast } from '../services/api'
import type { ForecastResponse, HistoricalPoint } from '../types/api'

interface ForecastingPageProps {
  historical: HistoricalPoint[]
}

const HORIZONS = [6, 12, 24, 36, 60]

export function ForecastingPage({ historical }: ForecastingPageProps) {
  const [horizon, setHorizon] = useState(24)
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    getForecast(horizon, controller.signal)
      .then(setForecast)
      .catch((caught: unknown) => {
        if (caught instanceof DOMException && caught.name === 'AbortError') return
        setError(
          caught instanceof Error ? caught.message : 'Forecast request failed.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })
    return () => controller.abort()
  }, [horizon])

  const updateHorizon = (value: number) => {
    setIsLoading(true)
    setError(null)
    setHorizon(value)
  }

  return (
    <div className="space-y-8">
      <header className="flex flex-wrap items-end justify-between gap-5">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">
            Future monthly CO2
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">
            Multi-step Exponential Smoothing forecast with an approximate
            residual-based 95% interval.
          </p>
        </div>
        <label className="text-sm font-medium">
          Forecast horizon
          <select
            value={horizon}
            onChange={(event) => updateHorizon(Number(event.target.value))}
            className="ml-3 min-h-10 rounded-lg border border-rule bg-surface px-3 text-sm"
          >
            {HORIZONS.map((value) => (
              <option key={value} value={value}>
                {value} months
              </option>
            ))}
          </select>
        </label>
      </header>

      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorMessage message={error} /> : null}
      {forecast && !isLoading ? (
        <>
          <section>
            <div className="mb-3 flex items-center justify-between gap-3">
              <h3 className="section-heading">{forecast.model}</h3>
              <p className="text-xs text-ink-muted">
                Generated {new Date(forecast.generated_at).toLocaleString()}
              </p>
            </div>
            <ForecastChart historical={historical} forecast={forecast.forecast} />
          </section>
          <section>
            <h3 className="section-heading">Forecast values</h3>
            <div className="mt-4 max-h-[430px] overflow-auto border-y border-rule">
              <table className="w-full min-w-[620px] text-left text-sm">
                <thead className="sticky top-0 bg-surface text-xs uppercase tracking-[0.1em] text-ink-muted">
                  <tr>
                    <th className="px-3 py-3">Month</th>
                    <th className="px-3 py-3 text-right">Prediction</th>
                    <th className="px-3 py-3 text-right">Lower</th>
                    <th className="px-3 py-3 text-right">Upper</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.forecast.map((point) => (
                    <tr key={point.date} className="border-t border-rule/70">
                      <td className="px-3 py-3 font-medium">{point.date}</td>
                      <td className="tabular px-3 py-3 text-right">
                        {point.prediction.toFixed(2)}
                      </td>
                      <td className="tabular px-3 py-3 text-right text-ink-muted">
                        {point.lower.toFixed(2)}
                      </td>
                      <td className="tabular px-3 py-3 text-right text-ink-muted">
                        {point.upper.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : null}
    </div>
  )
}

export default ForecastingPage
