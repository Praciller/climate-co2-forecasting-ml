import { Info } from 'lucide-react'
import type { ReactNode } from 'react'

export interface LimitationCalloutProps {
  title?: string
  children: ReactNode
}

export function LimitationCallout({ children, title = 'Evidence boundary' }: LimitationCalloutProps) {
  return (
    <aside role="note" className="flex gap-3 rounded-lg border border-warning/40 bg-warning/10 p-4 text-sm">
      <Info className="mt-0.5 size-4 shrink-0 text-warning" aria-hidden="true" />
      <div>
        <h2 className="font-semibold">{title}</h2>
        <div className="mt-1 leading-6 text-muted-foreground">{children}</div>
      </div>
    </aside>
  )
}
