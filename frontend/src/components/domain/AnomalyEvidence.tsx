import { Circle, CircleDot } from 'lucide-react'
import type { AnomalyPoint } from '../../types/api'

export interface AnomalyEvidenceProps {
  anomalies: AnomalyPoint[]
}

export function AnomalyEvidence({ anomalies }: AnomalyEvidenceProps) {
  const isolationCount = anomalies.filter((point) => point.isolation_forest_anomaly).length
  const residualCount = anomalies.filter((point) => point.residual_anomaly).length
  return (
    <section aria-labelledby="anomaly-evidence-heading" className="rounded-lg border border-border bg-card p-5">
      <h2 id="anomaly-evidence-heading" className="section-heading">Exploratory anomaly evidence</h2>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">These statistical signals are exploratory and are not verified climate events or causal claims.</p>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <Signal label="Isolation Forest" count={isolationCount} filled />
        <Signal label="Residual method" count={residualCount} />
      </div>
      <div className="mt-5 border-t border-border pt-4 text-sm text-muted-foreground">The dashboard keeps method signals separate: {isolationCount} Isolation Forest flagged months and {residualCount} residual flagged months.</div>
    </section>
  )
}

function Signal({ count, filled = false, label }: { count: number; filled?: boolean; label: string }) {
  const Icon = filled ? CircleDot : Circle
  return <div className="flex items-center gap-3"><Icon className={`size-5 ${filled ? 'fill-anomaly text-anomaly' : 'text-anomaly'}`} aria-hidden="true" /><div><p className="text-xs font-semibold uppercase tracking-[0.1em] text-muted-foreground">{label}</p><p className="tabular mt-1 text-xl font-semibold">{count} flagged months</p></div></div>
}
