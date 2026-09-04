import { expect, type Page, type TestInfo } from '@playwright/test'

export const PAGE_LABELS = [
  'Overview',
  'Data Explorer',
  'Forecasting',
  'Anomaly Detection',
  'Model Evaluation',
] as const

export function pageNavigation(page: Page, testInfo: TestInfo) {
  const label = testInfo.project.name === 'mobile'
    ? 'Mobile navigation'
    : 'Primary navigation'
  return page.getByRole('navigation', { name: label })
}

export async function waitForDashboard(page: Page) {
  await expect(page.locator('header').getByRole('status')).toContainText(
    'API connected',
  )
  await expect(
    page.getByRole('heading', { level: 1, name: 'Overview', exact: true }),
  ).toBeVisible()
  await expect(
    page.getByRole('heading', { name: /Historical CO₂ evidence/ }),
  ).toBeVisible()
}

export async function navigateToPage(
  page: Page,
  testInfo: TestInfo,
  label: (typeof PAGE_LABELS)[number],
) {
  await pageNavigation(page, testInfo)
    .getByRole('button', { name: label, exact: true })
    .click()
  await expect(
    page.getByRole('heading', { level: 1, name: label, exact: true }),
  ).toBeVisible()
}

export function metricCard(page: Page, label: string) {
  return page.locator('p').filter({ hasText: label }).first().locator('..')
}

export async function expectNoPageOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }))
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth + 1)
}

export async function freezeAnimations(page: Page) {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
        caret-color: transparent !important;
      }
    `,
  })
}
