import type { Meta, StoryObj } from '@storybook/react-vite'
import { fn } from 'storybook/test'

import { AppShell } from './AppShell'

const meta = {
  title: 'Components/AppShell',
  component: AppShell,
  tags: ['autodocs', 'test'],
  parameters: {
    layout: 'fullscreen',
  },
  args: {
    activePage: 'overview',
    apiStatus: 'connected',
    pageTitle: 'Overview',
    onNavigate: fn(),
    children: <p>Historical evidence overview</p>,
  },
} satisfies Meta<typeof AppShell>

export default meta
type Story = StoryObj<typeof meta>

export const Connected: Story = {}

export const Connecting: Story = {
  args: {
    apiStatus: 'connecting',
  },
}

export const ActiveForecasting: Story = {
  args: {
    activePage: 'forecasting',
    pageTitle: 'Forecasting',
    children: <p>Fixed-origin historical projection</p>,
  },
}
