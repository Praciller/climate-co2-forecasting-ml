import { Skeleton } from './ui/skeleton'

export function LoadingState() {
  return (
    <div
      className="space-y-8"
      role="status"
      aria-busy="true"
      aria-label="Loading dashboard"
    >
      <Skeleton className="h-20 rounded-lg" />
      <Skeleton className="h-[360px] rounded-lg" />
      <div className="grid gap-5 md:grid-cols-3">
        <Skeleton className="h-28 rounded-lg" />
        <Skeleton className="h-28 rounded-lg" />
        <Skeleton className="h-28 rounded-lg" />
      </div>
    </div>
  )
}
