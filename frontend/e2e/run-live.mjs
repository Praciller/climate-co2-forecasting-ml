import { spawnSync } from 'node:child_process'

const baseURL = process.env.PLAYWRIGHT_BASE_URL
if (!baseURL || !/^https?:\/\//i.test(baseURL)) {
  console.error('PLAYWRIGHT_BASE_URL must be an external http(s) URL for live E2E.')
  process.exit(1)
}

const command = process.platform === 'win32' ? 'npx.cmd' : 'npx'
const result = spawnSync(
  command,
  ['playwright', 'test', '--config', 'playwright.config.ts', ...process.argv.slice(2)],
  { stdio: 'inherit', shell: process.platform === 'win32' },
)
process.exit(result.status ?? 1)
