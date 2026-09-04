import { expect, test } from '@playwright/test'

import { waitForDashboard } from './helpers'

test('dashboard recovers after a deterministic API interruption @desktop @mobile', async ({
  page,
}) => {
  await page.route('**/historical-data', (route) => route.abort())
  await page.goto('/')

  const alert = page.getByRole('alert')
  await expect(alert).toBeVisible()
  await expect(alert).toContainText('Forecasting API unavailable')
  await expect(page.getByRole('button', { name: 'Retry connection' })).toBeVisible()
  await expect(page.locator('header').getByRole('status')).toContainText(
    'API unavailable',
  )

  await page.unroute('**/historical-data')
  await page.getByRole('button', { name: 'Retry connection' }).click()
  await waitForDashboard(page)
})
