import type { Meta, StoryObj } from '@storybook/react-vite'

import { ForecastChart } from './ForecastChart'

const meta = {
  title: 'Charts/ForecastChart',
  component: ForecastChart,
  tags: ['autodocs', 'test'],
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof ForecastChart>

export default meta
type Story = StoryObj<typeof meta>

export const FixedOriginPredictionInterval: Story = {
  args: {
    historical: [
      { date: '2001-10-31', co2: 368.6, rolling_mean_12: 368.2 },
      { date: '2001-11-30', co2: 370.5, rolling_mean_12: 369.1 },
      { date: '2001-12-31', co2: 371.02, rolling_mean_12: 369.8 },
    ],
    forecast: [
      { date: '2002-01-31', prediction: 371.976, lower: 371.47, upper: 372.482 },
      { date: '2002-02-28', prediction: 372.749, lower: 372.244, upper: 373.255 },
      { date: '2002-03-31', prediction: 373.66, lower: 373.155, upper: 374.166 },
    ],
    forecastOrigin: '2001-12-31',
    intervalNominalCoverage: 0.9,
  },
}
