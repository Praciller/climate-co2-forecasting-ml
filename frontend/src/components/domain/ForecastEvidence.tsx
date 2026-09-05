import type { ForecastResponse, HistoricalPoint } from '../../types/api'

export interface ForecastEvidenceProps {
  forecast: ForecastResponse
  historical: HistoricalPoint[]
}

export function ForecastEvidence({ forecast, historical }: ForecastEvidenceProps) {
  const latestObserved = historical.at(-1)?.date ?? 'Unavailable'
  return (
    <section aria-labelledby="forecast-evidence-heading" className="rounded-lg border border-border bg-card p-5">
      <h2 id="forecast-evidence-heading" className="section-heading">Forecast evidence</h2>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">A fixed-origin multi-step forecast from the governed historical model artifact.</p>
      <dl className="mt-5 grid gap-x-6 gap-y-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
        <div><dt className="text-xs text-muted-foreground">Model</dt><dd className="mt-1 font-medium">{forecast.model} · {forecast.model_version}</dd></div>
        <div><dt className="text-xs text-muted-foreground">Forecast origin</dt><dd className="mt-1 font-medium">{forecast.forecast_origin}</dd></div>
        <div><dt className="text-xs text-muted-foreground">Latest observed</dt><dd className="mt-1 font-medium">{latestObserved}</dd></div>
        <div><dt className="text-xs text-muted-foreground">Horizon</dt><dd className="mt-1 font-medium">{forecast.horizon_months} months · {forecast.frequency}</dd></div>
      </dl>
      <p className="mt-5 border-t border-border pt-4 text-sm leading-6">The shaded range is a {forecast.interval_nominal_coverage * 100}% prediction interval. It is served for a fixed-origin multi-step projection and does not make a multi-horizon coverage claim.</p>
    </section>
  )
}
