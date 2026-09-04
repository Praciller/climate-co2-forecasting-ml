import { expect, test } from '@playwright/test'

import {
  freezeAnimations,
  navigateToPage,
  waitForDashboard,
} from './helpers'

test('desktop overview evidence summary remains stable @desktop', async ({ page }) => {
  await page.goto('/')
  await waitForDashboard(page)
  await freezeAnimations(page)
  const region = page
    .getByRole('heading', { name: 'Observed monthly concentration', exact: true })
    .locator('..')
    .locator('..')
  await expect(region).toHaveScreenshot('overview-evidence.png', {
    animations: 'disabled',
  })
})

test('desktop model-evaluation distinction remains stable @desktop', async ({ page }, testInfo) => {
  await page.goto('/')
  await waitForDashboard(page)
  await navigateToPage(page, testInfo, 'Model Evaluation')
  await freezeAnimations(page)
  const region = page
    .getByRole('heading', { name: 'Development selection', exact: true })
    .locator('..')
    .locator('..')
  await expect(region).toHaveScreenshot('model-evaluation-selection.png', {
    animations: 'disabled',
  })
})

test('desktop forecast evidence area remains stable @desktop', async ({ page }, testInfo) => {
  await page.goto('/')
  await waitForDashboard(page)
  await navigateToPage(page, testInfo, 'Forecasting')
  await expect(page.getByRole('heading', { name: 'Forecast evidence', exact: true })).toBeVisible()
  await freezeAnimations(page)
  const region = page
    .getByRole('heading', { name: 'Forecast evidence', exact: true })
    .locator('..')
    .locator('..')
  await expect(region).toHaveScreenshot('forecast-evidence.png', {
    animations: 'disabled',
  })
})

test('mobile overview shell remains stable @mobile', async ({ page }) => {
  await page.goto('/')
  await waitForDashboard(page)
  await freezeAnimations(page)
  const region = page
    .getByRole('heading', { name: /Historical CO₂ evidence/ })
    .locator('..')
    .locator('..')
  await expect(region).toHaveScreenshot('overview-mobile-shell.png', {
    animations: 'disabled',
  })
})
