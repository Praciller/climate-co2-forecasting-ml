import {
  Activity,
  BarChart3,
  ChartNoAxesCombined,
  Database,
  FlaskConical,
} from 'lucide-react'
import type { PropsWithChildren } from 'react'

import type { PageId } from '../types/api'

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: ChartNoAxesCombined },
  { id: 'data', label: 'Data Explorer', icon: Database },
  { id: 'forecasting', label: 'Forecasting', icon: Activity },
  { id: 'anomalies', label: 'Anomaly Detection', icon: FlaskConical },
  { id: 'evaluation', label: 'Model Evaluation', icon: BarChart3 },
] satisfies Array<{
  id: PageId
  label: string
  icon: typeof Activity
}>

interface AppShellProps extends PropsWithChildren {
  activePage: PageId
  apiStatus: 'connected' | 'connecting' | 'unavailable'
  pageTitle: string
  onNavigate: (page: PageId) => void
}

export function AppShell({
  activePage,
  apiStatus,
  children,
  pageTitle,
  onNavigate,
}: AppShellProps) {
  return (
    <div className="min-h-screen bg-canvas text-ink lg:grid lg:grid-cols-[248px_1fr]">
      <aside className="hidden min-h-screen border-r border-rule bg-surface lg:flex lg:flex-col">
        <div className="border-b border-rule px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-lg bg-accent text-sm font-bold text-white">
              CO2
            </div>
            <div>
              <p className="font-semibold tracking-tight">CO2 Forecast Lab</p>
              <p className="mt-0.5 text-xs text-ink-muted">
                Evidence-led forecasting
              </p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-5" aria-label="Primary navigation">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => onNavigate(id)}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium transition-colors ${
                activePage === id
                  ? 'bg-accent-soft text-accent'
                  : 'text-ink-muted hover:bg-surface-muted hover:text-ink'
              }`}
              aria-current={activePage === id ? 'page' : undefined}
            >
              <Icon size={18} strokeWidth={1.8} aria-hidden="true" />
              {label}
            </button>
          ))}
        </nav>
        <div className="border-t border-rule px-6 py-5 text-xs leading-5 text-ink-muted">
          Real statsmodels data
          <br />
          Local-first ML system
        </div>
      </aside>

      <div className="min-w-0">
        <header className="sticky top-0 z-10 border-b border-rule bg-surface/95 backdrop-blur">
          <div className="flex min-h-16 items-center justify-between px-5 sm:px-8 lg:px-10">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ink-muted">
                CO2 Forecast Lab
              </p>
              <h1 className="text-lg font-semibold tracking-tight">{pageTitle}</h1>
            </div>
            <div className="flex items-center gap-2 text-xs font-medium text-ink-muted">
              <span
                className={`size-2 rounded-full ${
                  apiStatus === 'connected'
                    ? 'bg-success'
                    : apiStatus === 'connecting'
                      ? 'bg-anomaly'
                      : 'bg-danger'
                }`}
                aria-hidden="true"
              />
              API {apiStatus}
            </div>
          </div>
          <nav
            className="flex gap-1 overflow-x-auto border-t border-rule px-3 py-2 lg:hidden"
            aria-label="Mobile navigation"
          >
            {NAV_ITEMS.map(({ id, label }) => (
              <button
                key={id}
                type="button"
                onClick={() => onNavigate(id)}
                className={`shrink-0 rounded-md px-3 py-2 text-xs font-semibold ${
                  activePage === id
                    ? 'bg-accent-soft text-accent'
                    : 'text-ink-muted'
                }`}
                aria-current={activePage === id ? 'page' : undefined}
              >
                {label}
              </button>
            ))}
          </nav>
        </header>
        <main className="mx-auto w-full max-w-[1500px] px-5 py-7 sm:px-8 lg:px-10 lg:py-10">
          {children}
        </main>
      </div>
    </div>
  )
}
