import { expect, test } from '@playwright/test'

const destinations = [
  'Overview',
  'Data Explorer',
  'Forecasting',
  'Anomaly Detection',
  'Model Evaluation',
]

test.beforeEach(async ({ page }) => {
  test.skip(!process.env.PREVIEW_E2E, 'Preview-only shell contract')
  await page.goto('/')
  await expect(page.getByRole('status')).toContainText('API unavailable')
})

test('desktop shell exposes all destinations when API data is unavailable @preview @desktop', async ({ page }) => {
  const navigation = page.getByRole('navigation', { name: 'Primary navigation' })
  await expect(navigation).toBeVisible()

  for (const destination of destinations) {
    await expect(navigation.getByRole('button', { name: destination })).toBeVisible()
  }

  await navigation.getByRole('button', { name: 'Model Evaluation' }).click()
  await expect(page.getByText('Model Evaluation', { exact: true }).last()).toBeVisible()
})

test('mobile shell opens navigation and changes the active destination @preview @mobile', async ({ page }) => {
  await page.getByRole('button', { name: 'Open navigation' }).click()
  const navigation = page.getByRole('navigation', { name: 'Mobile navigation' })
  await expect(navigation).toBeVisible()

  for (const destination of destinations) {
    await expect(navigation.getByRole('button', { name: destination })).toBeVisible()
  }

  await navigation.getByRole('button', { name: 'Forecasting' }).click()
  await expect(page.getByText('Forecasting', { exact: true }).last()).toBeVisible()
})
