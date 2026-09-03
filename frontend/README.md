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

The Issue #5 foundation covers MetricCard, LoadingState, ErrorMessage,
ModelComparisonTable, and AppShell. Issue #6 adds contract-accurate page
fixtures, model-evaluation and forecast behavior tests, and Storybook states
for the chart components. Full application E2E and committed visual regression
are intentionally deferred to the later browser-quality issue.
