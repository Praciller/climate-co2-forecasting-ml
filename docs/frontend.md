# Frontend

## Stack

- React 19
- TypeScript
- Vite 8
- Tailwind CSS 4
- Recharts
- Lucide icons

## Pages

- Overview
- Data Explorer
- Forecasting
- Anomaly Detection
- Model Evaluation

## Architecture

API calls live in `src/services/api.ts`. Shared data loading lives in `useDashboardData`. `App.tsx` composes lazy-loaded pages and navigation instead of owning chart or table implementation.

## States

- skeleton loading state
- explicit API-unavailable state with retry
- selected navigation state
- interactive forecast horizon selector
- horizontally scrollable mobile tables

## Build

```bash
cd frontend
npm ci
npm run lint
npm run test
npm run build
npm run build-storybook
npx playwright install --with-deps chromium
npm run test:storybook
npm audit --audit-level=high
```

## Quality foundation

The unit suite uses Vitest, jsdom, and Testing Library with `jest-dom` matchers.
Representative coverage includes MetricCard, LoadingState, ErrorMessage,
ModelComparisonTable, and AppShell. Storybook stories cover the same shared
surface and run through Storybook's official Vitest browser integration with
the a11y addon configured to fail on violations.

This issue intentionally does not add full application Playwright E2E or visual
regression tooling. Those checks belong to the later browser-quality issue.

Set `VITE_API_URL` to override the default `http://localhost:8000`.
