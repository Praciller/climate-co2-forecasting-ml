import { AnomalyTimeline } from '../components/AnomalyTimeline'
import { MetricCard } from '../components/MetricCard'
import type { AnomalyPoint, HistoricalPoint } from '../types/api'

interface AnomalyDetectionPageProps {
  anomalies: AnomalyPoint[]
  historical: HistoricalPoint[]
}

export function AnomalyDetectionPage({
  anomalies,
  historical,
}: AnomalyDetectionPageProps) {
  const residualCount = anomalies.filter((point) => point.residual_anomaly).length
  const isolationCount = anomalies.filter(
    (point) => point.isolation_forest_anomaly,
  ).length
  const agreementCount = anomalies.filter(
    (point) => point.residual_anomaly && point.isolation_forest_anomaly,
  ).length
  const residualOnlyCount = residualCount - agreementCount
  const isolationOnlyCount = isolationCount - agreementCount

  return (
    <div className="space-y-10">
      <header>
        <h2 className="text-2xl font-semibold tracking-tight">
          Exploratory anomaly signals
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-ink-muted">
          Compare two statistical signals over the packaged historical record.
          They are not verified climate events, sensor failures, or causal
          attributions.
        </p>
      </header>
      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Unique months" value={String(anomalies.length)} />
        <MetricCard
          label="Residual-threshold signal"
          value={String(residualCount)}
          detail="Mean absolute residual + 3 sigma"
        />
        <MetricCard
          label="Isolation Forest"
          value={String(isolationCount)}
          detail="3% contamination assumption"
        />
        <MetricCard
          label="Agreement"
          value={String(agreementCount)}
          detail={`${residualOnlyCount} residual only · ${isolationOnlyCount} Isolation Forest only`}
        />
      </section>
      <section>
        <h3 className="section-heading">Timeline</h3>
        <p className="mt-1 text-sm text-ink-muted">
          Filled amber circles mark Isolation Forest signals. Outlined circles
          mark residual-threshold signals; overlapping markers indicate
          agreement.
        </p>
        <div className="mt-4">
          <AnomalyTimeline anomalies={anomalies} historical={historical} />
        </div>
      </section>
      <section>
        <h3 className="section-heading">Flagged months</h3>
        <p className="mt-1 text-sm text-ink-muted">
          Method labels are derived from the API flags and are independent of
          marker color.
        </p>
        <div className="mt-4 overflow-x-auto border-y border-rule">
          <table className="w-full min-w-[660px] text-left text-sm">
            <thead className="text-xs uppercase tracking-[0.1em] text-ink-muted">
              <tr>
                <th scope="col" className="px-3 py-3">Date</th>
                <th scope="col" className="px-3 py-3 text-right">CO2 ppm</th>
                <th scope="col" className="px-3 py-3">Method</th>
                <th scope="col" className="px-3 py-3">Signal details</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((point) => (
                <tr key={point.date} className="border-t border-rule/70">
                  <td className="px-3 py-3 font-medium">{point.date}</td>
                  <td className="tabular px-3 py-3 text-right">
                    {point.co2.toFixed(2)}
                  </td>
                  <td className="px-3 py-3 text-ink-muted">
                    {point.methods.join(', ')}
                  </td>
                  <td className="px-3 py-3 text-xs text-ink-muted">
                    {point.residual_anomaly && point.isolation_forest_anomaly
                      ? 'Agreement'
                      : point.residual_anomaly
                        ? 'Residual threshold only'
                        : 'Isolation Forest only'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default AnomalyDetectionPage
