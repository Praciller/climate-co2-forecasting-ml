export interface MetricCardProps {
  label: string
  value: string
  detail?: string
}

export function MetricCard({ detail, label, value }: MetricCardProps) {
  return (
    <div className="border-t border-border pt-4">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        {label}
      </p>
      <p className="tabular mt-2 text-2xl font-semibold tracking-tight">
        {value}
      </p>
      {detail ? <p className="mt-1 text-xs text-muted-foreground">{detail}</p> : null}
    </div>
  )
}
