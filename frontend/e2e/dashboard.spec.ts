import { expect, test } from '@playwright/test'

import {
  expectNoPageOverflow,
  metricCard,
  navigateToPage,
  waitForDashboard,
} from './helpers'

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await waitForDashboard(page)
})

test('overview communicates the historical evidence boundary @desktop @mobile', async ({
  page,
}) => {
  await expect(page.getByText(/does not ingest current atmospheric data/)).toBeVisible()
  await expect(
    metricCard(page, 'Selected by development').getByRole('heading', { name: 'SARIMA', exact: true }),
  ).toBeVisible()
  await expect(page.getByText(/final-test metrics are not used to retune or replace it/)).toBeVisible()
  await expect(page.getByText(/exploratory signals, not verified events/)).toBeVisible()
})

test('data explorer presents historical provenance and preparation @desktop @mobile', async ({
  page,
}, testInfo) => {
  await navigateToPage(page, testInfo, 'Data Explorer')
  await expect(page.getByText(/historical evidence, not a live atmospheric reading/)).toBeVisible()
  await expect(metricCard(page, 'Monthly rows').getByText('526')).toBeVisible()
  await expect(page.getByText('Preparation lineage', { exact: true })).toBeVisible()
  await expect(page.getByText('Historical only', { exact: true })).toBeVisible()
  await expectNoPageOverflow(page)
})

test('forecasting keeps origin, protocol, and interval limitations visible @desktop @mobile', async ({
  page,
}, testInfo) => {
  await navigateToPage(page, testInfo, 'Forecasting')
  await expect(page.getByText(/SARIMA · fixed-origin multi-step forecast from 2001-12-31/)).toBeVisible()
  await expect(page.getByText('90% nominal', { exact: true })).toBeVisible()
  await expect(page.getByRole('img', { name: /Historical CO2 and fixed-origin forecast/ })).toBeVisible()
  await expect(page.getByText(/no separately established multi-horizon coverage/)).toBeVisible()
})

test('anomaly page preserves method counts and exploratory language @desktop @mobile', async ({
  page,
}, testInfo) => {
  await navigateToPage(page, testInfo, 'Anomaly Detection')
  await expect(metricCard(page, 'Isolation Forest').getByText('8')).toBeVisible()
  await expect(metricCard(page, 'Residual-threshold signal').getByText('0')).toBeVisible()
  await expect(page.getByText(/not verified climate events/)).toBeVisible()
  await expect(
    page.getByRole('cell', { name: 'Isolation Forest only', exact: true }),
  ).toHaveCount(8)
})

test('model evaluation separates development selection from final-test ranking @desktop @mobile', async ({
  page,
}, testInfo) => {
  await navigateToPage(page, testInfo, 'Model Evaluation')
  await expect(page.getByText(/SARIMA was selected using/)).toBeVisible()
  await expect(page.getByText(/Exponential Smoothing has the lowest final-test MAE/)).toBeVisible()
  await expect(page.getByText('Selected by development', { exact: true })).toBeVisible()
  await expect(metricCard(page, 'Lowest final-test MAE')).toContainText(
    'Lowest final-test MAE',
  )
})
