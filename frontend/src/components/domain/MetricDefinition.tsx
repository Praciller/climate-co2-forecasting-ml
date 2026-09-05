export interface MetricDefinitionProps {
  label: string
  value: string
  detail?: string
}

export function MetricDefinition({ detail, label, value }: MetricDefinitionProps) {
  return (
    <div className="border-t border-border pt-4">
      <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</dt>
      <dd className="tabular mt-2 text-2xl font-semibold tracking-tight">{value}</dd>
      {detail ? <p className="mt-1 text-xs text-muted-foreground">{detail}</p> : null}
    </div>
  )
}
