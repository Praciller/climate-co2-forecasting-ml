import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { MetricCard } from './MetricCard'

describe('MetricCard', () => {
  it('shows the metric value and its evidence context', () => {
    render(
      <MetricCard
        label="Final-test MAE"
        value="0.243 ppm"
        detail="SARIMA · 78 historical test months"
      />,
    )

    expect(screen.getByText('Final-test MAE')).toBeVisible()
    expect(screen.getByText('0.243 ppm')).toBeVisible()
    expect(screen.getByText('SARIMA · 78 historical test months')).toBeVisible()
  })
})
