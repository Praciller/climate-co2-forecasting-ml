import type { Meta, StoryObj } from '@storybook/react-vite'

import { AnomalyTimeline } from './AnomalyTimeline'

const meta = {
  title: 'Components/AnomalyTimeline',
  component: AnomalyTimeline,
  tags: ['autodocs', 'test'],
} satisfies Meta<typeof AnomalyTimeline>

export default meta
type Story = StoryObj<typeof meta>

export const DistinctMethodSignals: Story = {
  args: {
    historical: [
      { date: '1998-05-31', co2: 369.14, rolling_mean_12: 367.5 },
      { date: '1998-06-30', co2: 368.75, rolling_mean_12: 367.7 },
      { date: '1998-07-31', co2: 367.6, rolling_mean_12: 367.9 },
    ],
    anomalies: [
      {
        date: '1998-05-31',
        co2: 369.14,
        residual_ppm: 0.16,
        residual_anomaly: false,
        isolation_score: 0.58,
        isolation_forest_anomaly: true,
        methods: ['Isolation Forest'],
      },
      {
        date: '1998-06-30',
        co2: 368.75,
        residual_ppm: 0.37,
        residual_anomaly: true,
        isolation_score: 0.62,
        isolation_forest_anomaly: true,
        methods: ['Residual threshold', 'Isolation Forest'],
      },
    ],
  },
}
