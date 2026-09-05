import { AnomalyEvidence } from '../components/domain/AnomalyEvidence'
import { PageHeader } from '../components/PageHeader'
import { AnomalyTimeline } from '../components/AnomalyTimeline'
import { MetricCard } from '../components/MetricCard'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import type { AnomalyPoint, HistoricalPoint } from '../types/api'

interface AnomalyDetectionPageProps { anomalies: AnomalyPoint[]; historical: HistoricalPoint[] }

export function AnomalyDetectionPage({ anomalies, historical }: AnomalyDetectionPageProps) {
  const residualCount = anomalies.filter((point) => point.residual_anomaly).length
  const isolationCount = anomalies.filter((point) => point.isolation_forest_anomaly).length
  const agreementCount = anomalies.filter((point) => point.residual_anomaly && point.isolation_forest_anomaly).length
  return (
    <div className="space-y-10">
      <PageHeader title="Anomaly Detection" description="Compare two statistical signals over the packaged historical record. Review method-level markers with caution." />
      <AnomalyEvidence anomalies={anomalies} />
      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="Unique months" value={String(anomalies.length)} /><MetricCard label="Residual-threshold signal" value={String(residualCount)} detail="Mean absolute residual + 3 sigma" /><MetricCard label="Isolation Forest" value={String(isolationCount)} detail="3% contamination assumption" /><MetricCard label="Agreement" value={String(agreementCount)} detail={`${residualCount - agreementCount} residual only · ${isolationCount - agreementCount} Isolation Forest only`} /></section>
      <section aria-labelledby="anomaly-timeline-heading"><h2 id="anomaly-timeline-heading" className="section-heading">Timeline</h2><p className="mt-1 text-sm text-muted-foreground">Filled amber circles mark Isolation Forest signals. Outlined amber circles mark residual-threshold signals; overlapping markers indicate agreement.</p><div className="mt-4"><AnomalyTimeline anomalies={anomalies} historical={historical} /></div></section>
      <section aria-labelledby="anomaly-table-heading"><h2 id="anomaly-table-heading" className="section-heading">Flagged months</h2><p className="mt-1 text-sm text-muted-foreground">Method labels are derived from API flags and are independent of marker color.</p><div className="mt-4 overflow-x-auto rounded-lg border border-border"><Table className="min-w-[660px]"><caption className="sr-only">Exploratory flagged historical months</caption><TableHeader><TableRow><TableHead>Date</TableHead><TableHead className="text-right">CO2 ppm</TableHead><TableHead>Method</TableHead><TableHead>Signal details</TableHead></TableRow></TableHeader><TableBody>{anomalies.map((point) => <TableRow key={point.date}><TableCell className="font-medium">{point.date}</TableCell><TableCell className="tabular text-right">{point.co2.toFixed(2)}</TableCell><TableCell className="text-muted-foreground">{point.methods.join(', ')}</TableCell><TableCell className="text-xs text-muted-foreground">{point.residual_anomaly && point.isolation_forest_anomaly ? 'Agreement' : point.residual_anomaly ? 'Residual threshold only' : 'Isolation Forest only'}</TableCell></TableRow>)}</TableBody></Table></div></section>
    </div>
  )
}

export default AnomalyDetectionPage
