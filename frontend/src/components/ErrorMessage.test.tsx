import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { ErrorMessage } from './ErrorMessage'

describe('ErrorMessage', () => {
  it('shows the failure and lets the reviewer retry', async () => {
    const onRetry = vi.fn()
    const user = userEvent.setup()

    render(<ErrorMessage message="API data is unavailable." onRetry={onRetry} />)

    expect(screen.getByRole('heading', { name: 'Forecasting API unavailable' })).toBeVisible()
    expect(screen.getByText(/API data is unavailable/)).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Retry connection' }))

    expect(onRetry).toHaveBeenCalledOnce()
  })
})
