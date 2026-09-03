import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { modelInfoFixture } from '../test/fixtures'
import { ModelEvaluationPage } from './ModelEvaluationPage'

describe('ModelEvaluationPage', () => {
  it('shows development selection separately from the final-test winner', () => {
    render(<ModelEvaluationPage modelInfo={modelInfoFixture} />)

    expect(screen.getByText('Selected model')).toBeVisible()
    const selectedModelCard = screen.getByText('Selected model').parentElement
    if (!selectedModelCard) throw new Error('Selected model card is missing.')
    expect(within(selectedModelCard).getByText('SARIMA')).toBeVisible()
    expect(screen.getByText('Selected by development')).toBeVisible()
    expect(screen.getAllByText('Lowest final-test MAE')).toHaveLength(2)
    const finalTestSection = screen.getByRole('heading', {
      name: 'Final-test evaluation',
    }).parentElement
    if (!finalTestSection) throw new Error('Final-test section is missing.')
    expect(within(finalTestSection).getByText('Exponential Smoothing')).toBeVisible()
    const lowestMetricLabel = screen.getByText('Lowest final-test MAE', {
      selector: 'p',
    }).parentElement
    if (!lowestMetricLabel) throw new Error('Final-test metric card is missing.')
    expect(within(lowestMetricLabel).getByText('0.237')).toBeVisible()
    expect(screen.queryByText('Best MAE')).not.toBeInTheDocument()
  })
})
