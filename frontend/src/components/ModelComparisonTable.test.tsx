import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ModelComparisonTable } from './ModelComparisonTable'

describe('ModelComparisonTable', () => {
  it('renders numeric model rows and names the selected best-MAE model', () => {
    render(
      <ModelComparisonTable
        bestModel="SARIMA"
        models={{
          SARIMA: { mae: 0.243, rmse: 0.298, mape: 0.1, smape: 0.2, mase: 0.197 },
          'Exponential Smoothing': {
            mae: 0.237,
            rmse: 0.295,
            mape: 0.2,
            smape: 0.3,
            mase: 0.191,
          },
        }}
      />,
    )

    const table = screen.getByRole('table')
    const rows = within(table).getAllByRole('row')
    expect(rows).toHaveLength(3)
    expect(within(rows[1]).getAllByRole('cell')[0]).toHaveTextContent(
      'Exponential Smoothing',
    )
    expect(screen.getByText('Best MAE')).toBeVisible()
    expect(within(table).getByText('0.100%')).toBeVisible()
  })
})
