import { useEffect, useState } from 'react'

import { ErrorMessage } from '../components/ErrorMessage'
import { ForecastChart } from '../components/ForecastChart'
import { LoadingState } from '../components/LoadingState'
import { MetricCard } from '../components/MetricCard'
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
  const [retryKey, setRetryKey] = useState(0)

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
  }, [horizon, retryKey])

  const updateHorizon = (value: number) => {
    setIsLoading(true)
    setError(null)
    setHorizon(value)
  }

  const retry = () => {
    setIsLoading(true)
    setError(null)
    setRetryKey((value) => value + 1)
  }

  return (
    <div className="space-y-10">
      <header className="flex flex-wrap items-end justify-between gap-5">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">
            Fixed-origin forecast
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">
            A bounded monthly projection launched after the packaged historical
            record. It is not a current atmospheric forecast.
          </p>
        </div>
        <label htmlFor="forecast-horizon" className="text-sm font-medium">
          Forecast horizon
          <select
            id="forecast-horizon"
            value={horizon}
            onChange={(event) => updateHorizon(Number(event.target.value))}
            className="ml-3 min-h-11 rounded-lg border border-rule bg-surface px-3 text-sm"
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
      {error ? <ErrorMessage message={error} onRetry={retry} /> : null}
      {forecast && !isLoading ? (
        <>
          <section aria-labelledby="forecast-evidence-heading">
            <div className="mb-5">
              <h3 id="forecast-evidence-heading" className="section-heading">
                Forecast evidence
              </h3>
              <p className="mt-1 max-w-3xl text-sm leading-6 text-ink-muted">
                {forecast.model} · {forecast.protocol} from{' '}
                {forecast.forecast_origin} · model version {forecast.model_version}.
              </p>
            </div>
            <div className="mb-6 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard
                label="Forecast model"
                value={forecast.model}
                detail={forecast.model_version}
              />
              <MetricCard
                label="Forecast origin"
                value={forecast.forecast_origin}
                detail="Last packaged historical month"
              />
              <MetricCard
                label="Projection horizon"
                value={`${forecast.horizon_months} months`}
                detail={forecast.frequency}
              />
              <MetricCard
                label="Prediction interval"
                value={`${forecast.interval_nominal_coverage * 100}% nominal`}
                detail={forecast.interval_method}
              />
            </div>
            <p className="mb-5 border-l-2 border-accent pl-4 text-sm leading-6 text-ink-muted">
              <strong className="text-ink">Coverage boundary:</strong>{' '}
              measured coverage belongs to the documented rolling one-step
              evaluation ({forecast.interval_coverage_scope}). The fixed-origin
              multi-step projection reuses that development-derived radius; it
              has no separately established multi-horizon coverage.
            </p>
            <ForecastChart
              historical={historical}
              forecast={forecast.forecast}
              forecastOrigin={forecast.forecast_origin}
              intervalNominalCoverage={forecast.interval_nominal_coverage}
            />
            <p className="mt-3 text-xs leading-5 text-ink-muted">
              Historical observations use a neutral line. The accent line is
              the fixed-origin forecast and the shaded band is the{' '}
              {forecast.interval_nominal_coverage * 100}% prediction interval.
            </p>
          </section>
          <section aria-labelledby="forecast-values-heading">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 id="forecast-values-heading" className="section-heading">
                  Forecast values
                </h3>
                <p className="mt-1 text-sm text-ink-muted">
                  Exact monthly values in ppm for the selected horizon.
                </p>
              </div>
              <p className="text-xs text-ink-muted">
                Generated {new Date(forecast.generated_at).toLocaleString()}
              </p>
            </div>
            <div className="max-h-[430px] overflow-auto border-y border-rule">
              <table className="w-full min-w-[620px] text-left text-sm">
                <thead className="sticky top-0 bg-surface text-xs uppercase tracking-[0.1em] text-ink-muted">
                  <tr>
                    <th scope="col" className="px-3 py-3">Month</th>
                    <th scope="col" className="px-3 py-3 text-right">Prediction (ppm)</th>
                    <th scope="col" className="px-3 py-3 text-right">Lower (ppm)</th>
                    <th scope="col" className="px-3 py-3 text-right">Upper (ppm)</th>
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
