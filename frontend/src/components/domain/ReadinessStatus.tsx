import { CheckCircle2, CircleDashed, CircleOff } from 'lucide-react'

export interface ReadinessStatusProps {
  status: 'connected' | 'connecting' | 'unavailable'
  detail?: string
}

export function ReadinessStatus({ detail, status }: ReadinessStatusProps) {
  const copy = status === 'connected'
    ? { label: 'Ready', detail: detail ?? 'Governed artifacts validated', icon: CheckCircle2, className: 'text-status-ready' }
    : status === 'connecting'
      ? { label: 'Loading', detail: detail ?? 'Checking governed artifacts', icon: CircleDashed, className: 'text-warning' }
      : { label: 'Unavailable', detail: detail ?? 'Required artifacts could not be read', icon: CircleOff, className: 'text-status-unavailable' }
  const Icon = copy.icon

  return (
    <div role="status" aria-live="polite" className="flex items-start gap-3 rounded-lg border border-border bg-card px-4 py-3">
      <Icon className={`mt-0.5 size-4 shrink-0 ${copy.className}`} aria-hidden="true" />
      <div>
        <p className="text-sm font-semibold">{copy.label}</p>
        <p className="mt-0.5 text-xs text-muted-foreground">{copy.detail}</p>
      </div>
    </div>
  )
}
