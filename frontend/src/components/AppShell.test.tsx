import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { ThemeProvider } from '../theme/ThemeProvider'
import { AppShell } from './AppShell'

function renderShell(activePage: 'overview' | 'data' | 'forecasting' | 'anomalies' | 'evaluation' = 'forecasting') {
  return render(
    <ThemeProvider>
      <AppShell
        activePage={activePage}
        apiStatus="connected"
        onNavigate={vi.fn()}
      >
        <h1 id="page-heading" tabIndex={-1}>Forecasting</h1>
      </AppShell>
    </ThemeProvider>,
  )
}

describe('AppShell', () => {
  it('exposes five flat destinations and one active primary item', () => {
    renderShell()

    const navigation = screen.getByRole('navigation', { name: 'Primary navigation' })
    const buttons = within(navigation).getAllByRole('button')
    expect(buttons).toHaveLength(5)
    expect(within(navigation).getByRole('button', { name: 'Forecasting' })).toHaveAttribute(
      'aria-current',
      'page',
    )
    expect(screen.getByRole('status')).toHaveTextContent('API connected')
  })

  it('opens the named mobile Sheet and closes it after navigating', async () => {
    const onNavigate = vi.fn()
    const user = userEvent.setup()
    render(
      <ThemeProvider>
        <AppShell activePage="overview" apiStatus="connected" onNavigate={onNavigate}>
          <h1 id="page-heading" tabIndex={-1}>Overview</h1>
        </AppShell>
      </ThemeProvider>,
    )

    const trigger = screen.getByRole('button', { name: 'Open navigation' })
    expect(trigger).toHaveAttribute('aria-haspopup', 'dialog')
    await user.click(trigger)

    const dialog = await screen.findByRole('dialog', { name: 'Primary navigation' })
    const forecasting = within(dialog).getByRole('button', { name: 'Forecasting' })
    expect(forecasting).toHaveClass('min-h-11')
    await user.click(forecasting)

    expect(onNavigate).toHaveBeenCalledWith('forecasting')
    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Primary navigation' })).not.toBeInTheDocument())
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Overview' })).toHaveFocus())
  })

  it('provides an accessible theme control with all three choices', async () => {
    const user = userEvent.setup()
    renderShell()

    await user.click(screen.getByRole('button', { name: /Theme:/ }))
    expect(await screen.findByRole('menuitemradio', { name: 'Light' })).toBeVisible()
    expect(screen.getByRole('menuitemradio', { name: 'Dark' })).toBeVisible()
    expect(screen.getByRole('menuitemradio', { name: 'System' })).toBeVisible()
  })
})
