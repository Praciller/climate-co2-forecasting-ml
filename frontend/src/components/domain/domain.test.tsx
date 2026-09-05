import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { AnomalyEvidence } from './AnomalyEvidence'
import { ForecastEvidence } from './ForecastEvidence'
import { ModelComparison } from './ModelComparison'
import { ModelSelectionSummary } from './ModelSelectionSummary'
import { anomalyFixture, forecastFixture, historicalFixture, modelInfoFixture } from '../../test/fixtures'

describe('evidence domain modules', () => {
  it('separates development selection from final-test ranking', () => {
    render(<><ModelSelectionSummary selection={modelInfoFixture.selection} developmentMae={0.221} foldCount={5} /><ModelComparison selectedModel="SARIMA" finalTest={modelInfoFixture.metrics.final_test} /></>)
    expect(screen.getByText('Selected by development')).toBeInTheDocument()
    expect(screen.getByText('Lowest final-test MAE')).toBeInTheDocument()
    expect(screen.queryByText('Best model')).not.toBeInTheDocument()
    expect(screen.getByText(/final-test metrics are not used to retune or replace it/)).toBeInTheDocument()
  })

  it('uses prediction interval and fixed-origin limitation language', () => {
    render(<ForecastEvidence forecast={forecastFixture} historical={historicalFixture} />)
    expect(screen.getByText(/prediction interval/i)).toBeInTheDocument()
    expect(screen.getAllByText(/fixed-origin multi-step/i)).not.toHaveLength(0)
    expect(screen.getByText(/multi-horizon coverage claim/i)).toBeInTheDocument()
  })

  it('keeps anomaly methods visible and exploratory', () => {
    render(<AnomalyEvidence anomalies={anomalyFixture} />)
    expect(screen.getByText(/Isolation Forest flagged months/)).toBeInTheDocument()
    expect(screen.getByText(/Residual method/)).toBeInTheDocument()
    expect(screen.getByText(/exploratory and are not verified climate events/)).toBeInTheDocument()
  })

  it('uses semantic landmarks and table headers for comparison evidence', () => {
    render(<ModelComparison selectedModel="SARIMA" finalTest={modelInfoFixture.metrics.final_test} />)
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(within(screen.getByRole('table')).getByRole('columnheader', { name: 'Evidence role' })).toBeInTheDocument()
  })
})
