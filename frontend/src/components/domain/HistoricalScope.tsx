import { CalendarRange, Ruler, Sigma } from 'lucide-react'

export interface HistoricalScopeProps {
  period: string
  frequency: string
  unit: string
}

export function HistoricalScope({ frequency, period, unit }: HistoricalScopeProps) {
  return (
    <section aria-labelledby="historical-scope-heading" className="border-y border-border py-5">
      <h2 id="historical-scope-heading" className="section-heading">Historical scope</h2>
      <dl className="mt-4 grid gap-4 sm:grid-cols-3">
        <ScopeItem icon={CalendarRange} label="Period" value={period} />
        <ScopeItem icon={Sigma} label="Frequency" value={frequency} />
        <ScopeItem icon={Ruler} label="Unit" value={unit} />
      </dl>
    </section>
  )
}

function ScopeItem({ icon: Icon, label, value }: { icon: typeof CalendarRange; label: string; value: string }) {
  return (
    <div className="flex gap-3">
      <Icon className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
      <div>
        <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</dt>
        <dd className="mt-1 text-sm font-medium">{value}</dd>
      </div>
    </div>
  )
}
