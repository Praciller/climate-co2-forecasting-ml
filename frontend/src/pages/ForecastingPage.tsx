import { useEffect, useState } from 'react'
import { ErrorMessage } from '../components/ErrorMessage'
import { ForecastChart } from '../components/ForecastChart'
import { ForecastEvidence } from '../components/domain/ForecastEvidence'
import { ForecastIntervalLegend } from '../components/domain/ForecastIntervalLegend'
import { MetricDefinition } from '../components/domain/MetricDefinition'
import { PageHeader } from '../components/PageHeader'
import { LoadingState } from '../components/LoadingState'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { getForecast } from '../services/api'
import type { ForecastResponse, HistoricalPoint } from '../types/api'

interface ForecastingPageProps { historical: HistoricalPoint[] }
const HORIZONS = [6, 12, 24, 36, 60]

export function ForecastingPage({ historical }: ForecastingPageProps) {
  const [horizon, setHorizon] = useState(24)
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [retryKey, setRetryKey] = useState(0)
  useEffect(() => { const controller = new AbortController(); getForecast(horizon, controller.signal).then(setForecast).catch((caught: unknown) => { if (caught instanceof DOMException && caught.name === 'AbortError') return; setError(caught instanceof Error ? caught.message : 'Forecast request failed.') }).finally(() => { if (!controller.signal.aborted) setIsLoading(false) }); return () => controller.abort() }, [horizon, retryKey])
  const updateHorizon = (value: string | null) => { if (!value) return; setIsLoading(true); setError(null); setHorizon(Number(value)) }
  const retry = () => { setIsLoading(true); setError(null); setRetryKey((value) => value + 1) }
  return (
    <div className="space-y-10">
      <PageHeader title="Forecasting" description="A bounded monthly projection launched after the packaged historical record. It is not a current atmospheric forecast."><label htmlFor="forecast-horizon" className="flex items-center gap-3 text-sm font-medium">Forecast horizon<Select value={String(horizon)} onValueChange={updateHorizon}><SelectTrigger id="forecast-horizon" aria-label="Forecast horizon" className="min-h-11 min-w-32"><SelectValue /></SelectTrigger><SelectContent>{HORIZONS.map((value) => <SelectItem key={value} value={String(value)}>{value} months</SelectItem>)}</SelectContent></Select></label></PageHeader>
      {isLoading ? <LoadingState /> : null}{error ? <ErrorMessage message={error} onRetry={retry} /> : null}
      {forecast && !isLoading ? <><ForecastEvidence forecast={forecast} historical={historical} /><dl className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"><MetricDefinition label="Forecast model" value={forecast.model} detail={forecast.model_version} /><MetricDefinition label="Forecast origin" value={forecast.forecast_origin} detail="Last packaged historical month" /><MetricDefinition label="Projection horizon" value={`${forecast.horizon_months} months`} detail={forecast.frequency} /><MetricDefinition label="Prediction interval" value={`${forecast.interval_nominal_coverage * 100}% nominal`} detail={forecast.interval_method} /></dl><ForecastIntervalLegend nominalCoverage={forecast.interval_nominal_coverage} coverageScope={forecast.interval_coverage_scope} /><section aria-labelledby="forecast-chart-heading"><h2 id="forecast-chart-heading" className="section-heading">Historical record and fixed-origin projection</h2><div className="mt-4"><ForecastChart historical={historical} forecast={forecast.forecast} forecastOrigin={forecast.forecast_origin} intervalNominalCoverage={forecast.interval_nominal_coverage} /></div></section><section aria-labelledby="forecast-values-heading"><div className="flex flex-wrap items-end justify-between gap-3"><div><h2 id="forecast-values-heading" className="section-heading">Forecast values</h2><p className="mt-1 text-sm text-muted-foreground">Exact monthly values in ppm for the selected horizon.</p></div><p className="text-xs text-muted-foreground">Generated {new Date(forecast.generated_at).toLocaleString()}</p></div><div className="mt-4 max-h-[430px] overflow-auto rounded-lg border border-border"><Table className="min-w-[620px]"><caption className="sr-only">Forecast values for the selected horizon</caption><TableHeader><TableRow><TableHead>Month</TableHead><TableHead className="text-right">Prediction (ppm)</TableHead><TableHead className="text-right">Lower (ppm)</TableHead><TableHead className="text-right">Upper (ppm)</TableHead></TableRow></TableHeader><TableBody>{forecast.forecast.map((point) => <TableRow key={point.date}><TableCell className="font-medium">{point.date}</TableCell><TableCell className="tabular text-right">{point.prediction.toFixed(2)}</TableCell><TableCell className="tabular text-right text-muted-foreground">{point.lower.toFixed(2)}</TableCell><TableCell className="tabular text-right text-muted-foreground">{point.upper.toFixed(2)}</TableCell></TableRow>)}</TableBody></Table></div></section></> : null}
    </div>
  )
}

export default ForecastingPage
