import type { Meta, StoryObj } from '@storybook/react-vite'

import { ModelComparisonTable } from './ModelComparisonTable'

const meta = {
  title: 'Components/ModelComparisonTable',
  component: ModelComparisonTable,
  tags: ['autodocs', 'test'],
} satisfies Meta<typeof ModelComparisonTable>

export default meta
type Story = StoryObj<typeof meta>

export const SelectedByDevelopment: Story = {
  args: {
    bestModel: 'SARIMA',
    models: {
      SARIMA: { mae: 0.243, rmse: 0.298, mape: 0.1, smape: 0.2, mase: 0.197 },
      'Exponential Smoothing': {
        mae: 0.237,
        rmse: 0.295,
        mape: 0.2,
        smape: 0.3,
        mase: 0.191,
      },
      Naive: { mae: 1.136, rmse: 1.276, mape: 0.8, smape: 0.9, mase: 0.918 },
    },
  },
}
