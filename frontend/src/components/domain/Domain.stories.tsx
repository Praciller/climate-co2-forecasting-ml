import type { Meta, StoryObj } from '@storybook/react-vite'
import { AnomalyEvidence } from './AnomalyEvidence'
import { DataProvenance } from './DataProvenance'
import { ForecastEvidence } from './ForecastEvidence'
import { ForecastIntervalLegend } from './ForecastIntervalLegend'
import { HistoricalScope } from './HistoricalScope'
import { LimitationCallout } from './LimitationCallout'
import { MetricDefinition } from './MetricDefinition'
import { ModelComparison } from './ModelComparison'
import { ModelSelectionSummary } from './ModelSelectionSummary'
import { ReadinessStatus } from './ReadinessStatus'
import { anomalyFixture, forecastFixture, historicalFixture, modelInfoFixture } from '../../test/fixtures'

const meta = { title: 'Domain/Evidence modules', tags: ['autodocs', 'test'] } satisfies Meta
export default meta
type Story = StoryObj<typeof meta>

export const Scope: Story = { render: () => <HistoricalScope period="1958-03 to 2001-12" frequency="Monthly" unit="ppm" /> }
export const Provenance: Story = { render: () => <DataProvenance dataset={modelInfoFixture.dataset} preprocessing={modelInfoFixture.preprocessing} /> }
export const Ready: Story = { render: () => <ReadinessStatus status="connected" /> }
export const Limitation: Story = { render: () => <LimitationCallout>Prediction intervals are calibrated for one-step evaluation only.</LimitationCallout> }
export const Metric: Story = { render: () => <dl><MetricDefinition label="Final-test MAE" value="0.243 ppm" detail="Post-selection evaluation" /></dl> }
export const Selection: Story = { render: () => <ModelSelectionSummary selection={modelInfoFixture.selection} developmentMae={0.239} finalTestWinner={{ model: 'Exponential Smoothing', mae: 0.236713, samples: 78 }} foldCount={11} /> }
export const SelectionNarrowDark: Story = { render: () => <div className="dark max-w-sm bg-background p-4 text-foreground"><ModelSelectionSummary selection={modelInfoFixture.selection} developmentMae={0.239} finalTestWinner={{ model: 'Exponential Smoothing', mae: 0.236713, samples: 78 }} foldCount={11} /></div> }
export const Comparison: Story = { render: () => <ModelComparison selectedModel={modelInfoFixture.selection.selected_model} finalTest={modelInfoFixture.metrics.final_test} /> }
export const Forecast: Story = { render: () => <ForecastEvidence forecast={forecastFixture} historical={historicalFixture} /> }
export const IntervalLegend: Story = { render: () => <ForecastIntervalLegend nominalCoverage={0.9} coverageScope="rolling one-step final-test forecasts" /> }
export const Anomalies: Story = { render: () => <AnomalyEvidence anomalies={anomalyFixture} /> }
