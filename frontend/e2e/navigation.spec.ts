import { expect, test } from '@playwright/test'

import {
  PAGE_LABELS,
  expectNoPageOverflow,
  navigateToPage,
  pageNavigation,
  waitForDashboard,
} from './helpers'

test('the shell supports keyboard navigation across every page @desktop @mobile', async ({
  page,
}, testInfo) => {
  await page.goto('/')
  await waitForDashboard(page)

  const navigation = pageNavigation(page, testInfo)
  if (testInfo.project.name === 'mobile') {
    if (!(await navigation.isVisible())) {
      await page.getByRole('button', { name: 'Open navigation' }).click()
    }
  }
  await expect(navigation).toBeVisible()
  const buttons = navigation.getByRole('button')
  await expect(buttons).toHaveCount(PAGE_LABELS.length)

  await buttons.nth(0).focus()
  await expect(buttons.nth(0)).toBeFocused()
  await page.keyboard.press('Tab')
  await expect(buttons.nth(1)).toBeFocused()

  for (const label of PAGE_LABELS) {
    await navigateToPage(page, testInfo, label)
    if (testInfo.project.name === 'mobile') {
      await page.getByRole('button', { name: 'Open navigation' }).click()
      await expect(pageNavigation(page, testInfo)).toBeVisible()
    }
    await expect(
      pageNavigation(page, testInfo)
        .getByRole('button', { name: label, exact: true }),
    ).toHaveAttribute('aria-current', 'page')
    if (testInfo.project.name === 'mobile') {
      await expectNoPageOverflow(page)
    }
  }
})
