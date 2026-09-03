import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { AppShell } from './AppShell'

describe('AppShell', () => {
  it('exposes the active page and navigates from keyboard-friendly buttons', async () => {
    const onNavigate = vi.fn()
    const user = userEvent.setup()

    render(
      <AppShell
        activePage="forecasting"
        apiStatus="connected"
        pageTitle="Forecasting"
        onNavigate={onNavigate}
      >
        <p>Fixed-origin historical projection</p>
      </AppShell>,
    )

    expect(screen.getByRole('heading', { name: 'Forecasting' })).toBeVisible()
    expect(screen.getByText('API connected')).toBeVisible()
    expect(screen.getByText('Fixed-origin historical projection')).toBeVisible()

    const forecastingButtons = screen.getAllByRole('button', { name: 'Forecasting' })
    expect(forecastingButtons).toHaveLength(2)
    forecastingButtons.forEach((button) => {
      expect(button).toHaveAttribute('aria-current', 'page')
    })

    await user.click(
      within(screen.getByRole('navigation', { name: 'Primary navigation' })).getByRole(
        'button',
        { name: 'Data Explorer' },
      ),
    )
    expect(onNavigate).toHaveBeenCalledWith('data')
  })
})
