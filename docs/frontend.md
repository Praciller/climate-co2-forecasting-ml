# Frontend

## Stack

- React 19
- TypeScript
- Vite 8
- Tailwind CSS 4
- shadcn CLI 4.21.0 with Base UI primitives
- Recharts
- Lucide icons

## Pages

- Overview
- Data Explorer
- Forecasting
- Anomaly Detection
- Model Evaluation

## Architecture

API calls live in `src/services/api.ts`. Shared data loading lives in
`useDashboardData`. `App.tsx` composes lazy-loaded pages and navigation instead
of owning chart or table implementation. Shared domain evidence modules live in
`src/components/domain/`, chart grammar lives in `src/components/charts/`, and
the semantic token/theme contract lives in `src/index.css` and
`src/theme/ThemeProvider.tsx`.

## States

- skeleton loading state
- explicit API-unavailable state with retry
- selected navigation state
- interactive forecast horizon selector
- horizontally scrollable mobile tables
- light, dark, and system theme modes with persisted preference

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

The application Playwright suite and focused visual baselines are maintained in
`e2e/`. Baselines are canonical Linux/Chromium evidence; Windows runs verify
semantics and must not update the committed snapshots.

## Issue #6 design audit

| Surface | Design problem addressed | Resulting behavior |
|---|---|---|
| Overview | Selection, evaluation, interval, and scope were mixed together | Historical scope, development-selected model, final-test winner, measured coverage, provenance, and limitations are visible together |
| Data Explorer | Preparation lineage was partly hard-coded and live scope was implicit | Dataset/preprocessing metadata comes from `/model-info`; historical-only status is explicit |
| Forecasting | Protocol and interval language was inaccurate or buried | Fixed-origin origin, horizon, 90% prediction interval, method, and one-step coverage boundary are adjacent to the chart |
| Anomaly Detection | Amber markers did not distinguish methods | Isolation Forest and residual signals have distinct marker treatments plus text labels and agreement counts |
| Model Evaluation | Final-test winner was labeled as the selected model | Development selection and final-test ranking are separate API-derived sections and table labels |
| AppShell/charts | Active state and chart semantics relied too much on color | Active navigation has borders/ARIA state; charts have legends, units, origin annotation, and token-based colors |

Set `VITE_API_URL` to override the default `http://localhost:8000`.

## Issue #25 design system v2

The approved v2 system is implemented as a compact evidence workbench:

- `AppShell` provides a 220px desktop rail and a Base UI Sheet on mobile;
  active navigation has text, border, background, and `aria-current` signals.
- `PageHeader` gives every page one keyboard-focusable page heading and a
  short methodological description.
- Domain modules keep historical scope, provenance, readiness, limitations,
  selection, comparison, forecast intervals, and anomaly caveats adjacent to
  the evidence they qualify.
- Recharts compositions use the shared historical/forecast/interval/anomaly
  token grammar, explicit units, text-first legends/tooltips, and accessible
  nearby evidence.
- Storybook stories are organized under `Foundations`, `Primitives`, `Layout`,
  `Domain`, `Charts`, and `States`; the official Vitest browser project runs
  the configured a11y checks.

The eight approved primitives are Button, Badge, Alert, Select, Skeleton,
Sheet, DropdownMenu, and Table. The frontend introduces no Radix UI or Carbon
dependency. The full verification route is documented in `docs/verification.md`.
