import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { forecastFixture } from '../test/fixtures'
import { ForecastingPage } from './ForecastingPage'

const { getForecast } = vi.hoisted(() => ({
  getForecast: vi.fn(),
}))

vi.mock('../services/api', () => ({ getForecast }))

describe('ForecastingPage', () => {
  beforeEach(() => {
    getForecast.mockResolvedValue(forecastFixture)
  })

  it('labels fixed-origin interval evidence without overstating coverage', async () => {
    render(
      <ForecastingPage
        historical={[
          { date: '2001-11-30', co2: 370.5, rolling_mean_12: 370 },
          { date: '2001-12-31', co2: 371.02, rolling_mean_12: 370.85 },
        ]}
      />,
    )

    expect(await screen.findByText('Fixed-origin forecast')).toBeVisible()
    expect(screen.getByText(/fixed-origin multi-step forecast/)).toBeVisible()
    expect(screen.getByText('90% nominal')).toBeVisible()
    expect(screen.getByText(/rolling one-step final test only/)).toBeVisible()
    expect(screen.getByText(/no separately established multi-horizon coverage/)).toBeVisible()
    expect(screen.queryByText(/confidence interval/i)).not.toBeInTheDocument()
  })
})
