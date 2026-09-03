import type { Meta, StoryObj } from '@storybook/react-vite'

import { TimeSeriesChart } from './TimeSeriesChart'

const meta = {
  title: 'Components/TimeSeriesChart',
  component: TimeSeriesChart,
  tags: ['autodocs', 'test'],
} satisfies Meta<typeof TimeSeriesChart>

export default meta
type Story = StoryObj<typeof meta>

export const HistoricalMonthlyObservations: Story = {
  args: {
    data: [
      { date: '2001-10-31', co2: 368.6, rolling_mean_12: 368.2 },
      { date: '2001-11-30', co2: 370.5, rolling_mean_12: 369.1 },
      { date: '2001-12-31', co2: 371.02, rolling_mean_12: 369.8 },
    ],
  },
}
