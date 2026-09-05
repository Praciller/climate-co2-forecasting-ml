import {
  Activity,
  BarChart3,
  ChartNoAxesCombined,
  Database,
  FlaskConical,
  Menu,
  SunMoon,
} from 'lucide-react'
import { useState } from 'react'
import type { PropsWithChildren } from 'react'

import { useTheme, type Theme } from '../theme/ThemeProvider'
import type { PageId } from '../types/api'
import { Button } from './ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from './ui/sheet'

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

export interface AppShellProps extends PropsWithChildren {
  activePage: PageId
  apiStatus: 'connected' | 'connecting' | 'unavailable'
  onNavigate: (page: PageId) => void
}

function themeLabel(theme: Theme): string {
  return theme[0].toUpperCase() + theme.slice(1)
}

function NavigationItems({
  activePage,
  onNavigate,
  onSelection,
}: {
  activePage: PageId
  onNavigate: (page: PageId) => void
  onSelection?: () => void
}) {
  return (
    <>
      {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
        const isActive = activePage === id
        return (
          <Button
            key={id}
            type="button"
            variant="ghost"
            className={`min-h-11 w-full justify-start gap-3 rounded-md border-l-2 px-3 text-left text-sm font-medium hover:bg-muted hover:text-foreground ${
              isActive
                ? 'border-primary bg-primary-muted font-semibold text-primary'
                : 'border-transparent text-muted-foreground'
            }`}
            aria-current={isActive ? 'page' : undefined}
            onClick={() => {
              onNavigate(id)
              onSelection?.()
            }}
          >
            <Icon size={18} strokeWidth={1.8} aria-hidden="true" />
            {label}
          </Button>
        )
      })}
    </>
  )
}

export function AppShell({
  activePage,
  apiStatus,
  children,
  onNavigate,
}: AppShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { setTheme, theme } = useTheme()
  const activeLabel = NAV_ITEMS.find(({ id }) => id === activePage)?.label

  const navigateFromShell = (page: PageId) => {
    setMobileOpen(false)
    onNavigate(page)
    window.setTimeout(() => {
      document.getElementById('page-heading')?.focus()
    }, 0)
  }

  const statusLabel = apiStatus === 'connected'
    ? 'connected'
    : apiStatus === 'connecting'
      ? 'connecting'
      : 'unavailable'
  const statusColor = apiStatus === 'connected'
    ? 'bg-status-ready'
    : apiStatus === 'connecting'
      ? 'bg-warning'
      : 'bg-status-unavailable'

  return (
    <div className="min-h-screen max-w-full bg-background text-foreground lg:grid lg:grid-cols-[220px_minmax(0,1fr)]">
      <aside className="hidden min-h-screen border-r border-border bg-card lg:flex lg:flex-col">
        <div className="border-b border-border px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="grid size-9 place-items-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
              CO2
            </div>
            <div>
              <p className="font-semibold tracking-tight">CO2 Forecast Lab</p>
              <p className="mt-0.5 text-xs text-muted-foreground">Evidence-led forecasting</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-5" aria-label="Primary navigation">
          <NavigationItems activePage={activePage} onNavigate={navigateFromShell} />
        </nav>
        <div className="border-t border-border px-5 py-5 text-xs leading-5 text-muted-foreground">
          Historical statsmodels data
          <br />
          Local-first ML system
        </div>
      </aside>

      <div className="min-w-0">
        <header className="sticky top-0 z-10 border-b border-border bg-background/95">
          <div className="flex min-h-16 items-center justify-between gap-3 px-4 sm:px-8 lg:px-10">
            <div className="flex min-w-0 items-center gap-3">
              <div className="lg:hidden">
                <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
                  <SheetTrigger
                    render={
                      <Button
                        variant="outline"
                        size="icon"
                        className="min-h-11 min-w-11"
                        aria-label="Open navigation"
                      />
                    }
                  >
                    <Menu aria-hidden="true" />
                  </SheetTrigger>
                  <SheetContent side="left" className="w-[min(18rem,calc(100vw-2rem))] gap-0 p-0">
                    <SheetHeader className="border-b border-border pr-14">
                      <SheetTitle>Primary navigation</SheetTitle>
                      <SheetDescription>CO2 Forecast Lab destinations</SheetDescription>
                    </SheetHeader>
                    <nav className="space-y-1 px-3 py-5" aria-label="Mobile navigation">
                      <NavigationItems
                        activePage={activePage}
                        onNavigate={navigateFromShell}
                      />
                    </nav>
                  </SheetContent>
                </Sheet>
              </div>
              <div className="min-w-0">
                <p className="truncate text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  CO2 Forecast Lab
                </p>
                <p className="truncate text-sm font-medium text-foreground">{activeLabel}</p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger
                  render={
                    <Button
                      variant="ghost"
                      size="icon"
                      className="min-h-11 min-w-11"
                      aria-label={`Theme: ${themeLabel(theme)}`}
                    />
                  }
                >
                  <SunMoon aria-hidden="true" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="min-w-36">
                  <DropdownMenuRadioGroup
                    value={theme}
                    onValueChange={(value) => {
                      if (value === 'light' || value === 'dark' || value === 'system') {
                        setTheme(value)
                      }
                    }}
                  >
                    <DropdownMenuLabel>Theme</DropdownMenuLabel>
                    <DropdownMenuRadioItem value="light">Light</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="dark">Dark</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="system">System</DropdownMenuRadioItem>
                  </DropdownMenuRadioGroup>
                </DropdownMenuContent>
              </DropdownMenu>
              <div
                className="flex items-center gap-2 text-xs font-medium text-muted-foreground"
                role="status"
                aria-live="polite"
              >
                <span className={`size-2 rounded-full ${statusColor}`} aria-hidden="true" />
                <span className="hidden sm:inline">API {statusLabel}</span>
                <span className="sr-only sm:hidden">API {statusLabel}</span>
              </div>
            </div>
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1500px] px-4 py-7 sm:px-8 lg:px-10 lg:py-10">
          {children}
        </main>
      </div>
    </div>
  )
}
