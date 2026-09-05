import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { modelInfoFixture } from '../test/fixtures'
import { ModelEvaluationPage } from './ModelEvaluationPage'

describe('ModelEvaluationPage', () => {
  it('shows development selection separately from the final-test winner', () => {
    render(<ModelEvaluationPage modelInfo={modelInfoFixture} />)

    const selectionRegion = screen.getByRole('region', { name: 'Model selection' })
    expect(within(selectionRegion).getByRole('heading', { name: 'SARIMA' })).toBeVisible()
    expect(within(selectionRegion).getByText('Selected by development')).toBeVisible()
    expect(within(selectionRegion).getByRole('heading', { name: 'Lowest final-test MAE' })).toBeVisible()
    expect(within(selectionRegion).getByText('Exponential Smoothing')).toBeVisible()
    expect(within(selectionRegion).getByText('0.237 ppm')).toBeVisible()
    expect(within(selectionRegion).getByText('78 months')).toBeVisible()
    expect(within(selectionRegion).getByText(/final test evaluates after selection; it does not choose or replace the serving model/i)).toBeVisible()
    expect(screen.queryByText('Best model')).not.toBeInTheDocument()
  })
})
