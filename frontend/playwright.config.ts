import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig } from '@playwright/test'

const frontendRoot = path.dirname(fileURLToPath(import.meta.url))
const repositoryRoot = path.resolve(frontendRoot, '..')
const externalBaseURL = process.env.PLAYWRIGHT_BASE_URL
const liveMode = Boolean(externalBaseURL)
const vercelAutomationBypassSecret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET

export default defineConfig({
  testDir: './e2e',
  snapshotDir: './e2e/snapshots',
  outputDir: './test-results',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: externalBaseURL ?? 'http://127.0.0.1:4173',
    browserName: 'chromium',
    colorScheme: 'light',
    reducedMotion: 'reduce',
    caret: 'hide',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    extraHTTPHeaders: vercelAutomationBypassSecret
      ? {
          'x-vercel-protection-bypass': vercelAutomationBypassSecret,
          'x-vercel-set-bypass-cookie': 'true',
        }
      : undefined,
  },
  testIgnore: liveMode ? ['**/visual.spec.ts'] : undefined,
  projects: [
    {
      name: 'desktop',
      grep: /@desktop/,
      use: {
        viewport: { width: 1440, height: 900 },
        deviceScaleFactor: 1,
      },
    },
    {
      name: 'mobile',
      grep: /@mobile/,
      use: {
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 1,
        isMobile: true,
      },
    },
  ],
  webServer: liveMode
    ? undefined
    : [
        {
          command: 'node frontend/e2e/start-backend.mjs',
          cwd: repositoryRoot,
          url: 'http://127.0.0.1:8000/ready',
          timeout: 180_000,
          reuseExistingServer: false,
        },
        {
          command: 'npm run dev -- --host 127.0.0.1 --port 4173 --strictPort',
          cwd: frontendRoot,
          url: 'http://127.0.0.1:4173',
          timeout: 30_000,
          reuseExistingServer: false,
        },
      ],
})
