import type { Meta, StoryObj } from '@storybook/react-vite'
import { fn } from 'storybook/test'

import { AppShell } from './AppShell'
import { ThemeProvider } from '../theme/ThemeProvider'

const meta = {
  title: 'Components/AppShell',
  component: AppShell,
  tags: ['autodocs', 'test'],
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (Story) => (
      <ThemeProvider defaultTheme="light">
        <Story />
      </ThemeProvider>
    ),
  ],
  args: {
    activePage: 'overview',
    apiStatus: 'connected',
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
    children: <p>Fixed-origin historical projection</p>,
  },
}
