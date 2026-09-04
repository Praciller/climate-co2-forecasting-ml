# Climate CO₂ Forecasting frontend

React 19 + TypeScript + Vite dashboard for the reproducible historical Mauna
Loa CO₂ forecasting system. The frontend consumes the repository's bounded API;
it is not a current atmospheric feed or live climate monitoring service.

## Commands

Run from this directory after cloning:

```bash
npm ci
npm run lint
npm run test
npm run build
npm run build-storybook
npx playwright install --with-deps chromium
npm run test:storybook
npm audit --audit-level=high
```

`VITE_API_URL` overrides the default `http://localhost:8000` API URL.

## Test architecture

- `src/**/*.test.{ts,tsx}`: Vitest + jsdom + Testing Library unit/component tests.
- `src/**/*.stories.*`: Storybook stories for representative shared components.
- `test:storybook`: Storybook's official Vitest browser project with Chromium and
  the a11y addon configured to fail on accessibility violations.
- `e2e/*.spec.ts`: Playwright Test browser checks against the real local API-backed
  application. Desktop uses 1440x900 and mobile uses 390x844 Chromium.

## Browser E2E and visual regression

From `frontend/`, `npm run test:e2e` starts the documented pipeline, FastAPI
readiness endpoint, and Vite automatically. It uses only the packaged historical
dataset and no internet data. The suite covers navigation, the five critical
pages, API-unavailable/retry recovery, mobile page overflow, and four focused
visual regions.

The HTML report is written to `playwright-report/`; inspect it with
`npm run test:e2e:report`. Test traces, screenshots, and videos are written to
`test-results/` on failures. Retries are disabled so a flaky test is visible.

Visual snapshots under `e2e/snapshots/` are canonical Linux/Chromium evidence
generated in the same Playwright environment as CI. Do not overwrite them from
Windows. To intentionally update snapshots, run
`npm run test:e2e:update-snapshots` in the canonical Linux environment, review
the diff, and commit only the intended snapshot files. `generated_at` is not
captured in any visual contract.

The positive path uses the governed Issue #15 artifacts and asserts the
development-selected SARIMA model, the distinct final-test comparison, and the
8 Isolation Forest / 0 residual anomaly baseline. The error-path test aborts
one API request through Playwright routing, verifies the designed unavailable
state, removes the route, and verifies recovery through Retry.
