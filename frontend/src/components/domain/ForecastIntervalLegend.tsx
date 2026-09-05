export interface ForecastIntervalLegendProps {
  nominalCoverage: number
  coverageScope: string
}

export function ForecastIntervalLegend({ coverageScope, nominalCoverage }: ForecastIntervalLegendProps) {
  return (
    <section aria-labelledby="forecast-legend-heading" className="rounded-lg border border-border bg-card p-4">
      <h2 id="forecast-legend-heading" className="section-heading">Forecast reading guide</h2>
      <ul className="mt-3 grid gap-3 text-sm sm:grid-cols-3">
        <LegendItem symbolClass="bg-chart-forecast" label="Forecast" detail="Fixed-origin projection" />
        <LegendItem symbolClass="bg-chart-interval/40" label={`${nominalCoverage * 100}% prediction interval`} detail="Soft uncertainty band" />
        <LegendItem symbolClass="border-l-2 border-dashed border-foreground" label="Forecast origin" detail="Projection begins here" />
      </ul>
      <p className="mt-4 text-xs leading-5 text-muted-foreground">Coverage is evaluated for the documented {coverageScope}; the interval is not calibrated as a general multi-horizon guarantee.</p>
    </section>
  )
}

function LegendItem({ detail, label, symbolClass }: { detail: string; label: string; symbolClass: string }) {
  return <li className="flex gap-3"><span className={`mt-1 size-3 shrink-0 rounded-sm ${symbolClass}`} aria-hidden="true" /><span><span className="font-medium">{label}</span><span className="block text-xs text-muted-foreground">{detail}</span></span></li>
}
