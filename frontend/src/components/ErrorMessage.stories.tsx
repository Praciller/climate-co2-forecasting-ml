import type { Meta, StoryObj } from '@storybook/react-vite'
import { fn } from 'storybook/test'

import { ErrorMessage } from './ErrorMessage'

const meta = {
  title: 'Components/ErrorMessage',
  component: ErrorMessage,
  tags: ['autodocs', 'test'],
  args: {
    onRetry: fn(),
  },
} satisfies Meta<typeof ErrorMessage>

export default meta
type Story = StoryObj<typeof meta>

export const ApiUnavailable: Story = {
  args: {
    message: 'API data is unavailable.',
  },
}
