import { expect, test } from '@playwright/test'

import {
  freezeAnimations,
  navigateToPage,
  setDeterministicLightTheme,
  waitForDashboard,
} from './helpers'

test('desktop overview evidence summary remains stable @desktop', async ({ page }) => {
  await setDeterministicLightTheme(page)
  await page.goto('/')
  await waitForDashboard(page)
  await freezeAnimations(page)
  const region = page.getByRole('region', { name: /Historical CO₂ evidence/ })
  await expect(region).toHaveScreenshot('overview-evidence.png', {
    animations: 'disabled',
  })
})

test('desktop model-evaluation distinction remains stable @desktop', async ({ page }, testInfo) => {
  await setDeterministicLightTheme(page)
  await page.goto('/')
  await waitForDashboard(page)
  await navigateToPage(page, testInfo, 'Model Evaluation')
  await freezeAnimations(page)
  const region = page.getByRole('region', { name: 'Model selection' })
  await expect(region).toHaveScreenshot('model-evaluation-selection.png', {
    animations: 'disabled',
  })
})

test('desktop forecast evidence area remains stable @desktop', async ({ page }, testInfo) => {
  await setDeterministicLightTheme(page)
  await page.goto('/')
  await waitForDashboard(page)
  await navigateToPage(page, testInfo, 'Forecasting')
  await expect(page.getByRole('heading', { name: 'Forecast evidence', exact: true })).toBeVisible()
  await freezeAnimations(page)
  const region = page.getByRole('region', { name: 'Forecast evidence' })
  await expect(region).toHaveScreenshot('forecast-evidence.png', {
    animations: 'disabled',
  })
})

test('mobile overview shell remains stable @mobile', async ({ page }) => {
  await setDeterministicLightTheme(page)
  await page.goto('/')
  await waitForDashboard(page)
  await freezeAnimations(page)
  await expect(page).toHaveScreenshot('overview-mobile-shell.png', {
    animations: 'disabled',
    fullPage: false,
  })
})
