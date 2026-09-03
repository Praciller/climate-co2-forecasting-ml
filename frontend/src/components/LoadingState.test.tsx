import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { LoadingState } from './LoadingState'

describe('LoadingState', () => {
  it('announces that dashboard data is loading', () => {
    render(<LoadingState />)

    expect(screen.getByRole('status', { name: 'Loading dashboard' })).toHaveAttribute(
      'aria-busy',
      'true',
    )
  })
})
