import type { Meta, StoryObj } from '@storybook/react-vite'

import { MetricCard } from './MetricCard'

const meta = {
  title: 'Components/MetricCard',
  component: MetricCard,
  tags: ['autodocs', 'test'],
} satisfies Meta<typeof MetricCard>

export default meta
type Story = StoryObj<typeof meta>

export const FinalTestMae: Story = {
  args: {
    label: 'Final-test MAE',
    value: '0.243 ppm',
    detail: 'SARIMA · 78 historical test months',
  },
}

export const IntervalCoverage: Story = {
  args: {
    label: 'Measured one-step coverage',
    value: '91.0%',
    detail: '90% nominal · 71 of 78 final-test forecasts',
  },
}
