export function LoadingState() {
  return (
    <div className="space-y-8" aria-busy="true" aria-label="Loading dashboard">
      <div className="h-20 animate-pulse rounded-lg bg-surface-muted" />
      <div className="h-[360px] animate-pulse rounded-lg bg-surface-muted" />
      <div className="grid gap-5 md:grid-cols-3">
        <div className="h-28 animate-pulse rounded-lg bg-surface-muted" />
        <div className="h-28 animate-pulse rounded-lg bg-surface-muted" />
        <div className="h-28 animate-pulse rounded-lg bg-surface-muted" />
      </div>
    </div>
  )
}
