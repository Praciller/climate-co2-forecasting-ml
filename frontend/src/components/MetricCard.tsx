interface MetricCardProps {
  label: string
  value: string
  detail?: string
}

export function MetricCard({ detail, label, value }: MetricCardProps) {
  return (
    <div className="border-t border-rule pt-4">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-muted">
        {label}
      </p>
      <p className="tabular mt-2 text-2xl font-semibold tracking-tight text-ink">
        {value}
      </p>
      {detail ? <p className="mt-1 text-xs text-ink-muted">{detail}</p> : null}
    </div>
  )
}
