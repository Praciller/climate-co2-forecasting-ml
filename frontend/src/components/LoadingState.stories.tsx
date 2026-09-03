import type { Meta, StoryObj } from '@storybook/react-vite'

import { LoadingState } from './LoadingState'

const meta = {
  title: 'Components/LoadingState',
  component: LoadingState,
  tags: ['autodocs', 'test'],
} satisfies Meta<typeof LoadingState>

export default meta
type Story = StoryObj<typeof meta>

export const DashboardLoading: Story = {}
