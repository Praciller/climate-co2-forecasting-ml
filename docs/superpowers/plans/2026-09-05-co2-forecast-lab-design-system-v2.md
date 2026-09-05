# CO2 Forecast Lab Design System v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.
> Owner directive: do not dispatch subagents.

**Goal:** Implement the approved CO2 Forecast Lab Design System v2 without changing scientific, API, or governed-evidence semantics.

**Architecture:** Source-owned shadcn/ui components using Base UI primitives, CO2 Forecast Lab semantic CSS tokens with Light/Dark/System themes, a compact custom AppShell, repository-owned domain evidence components, and thin shared Recharts grammar. Existing page data flow and API types remain the application seam; new modules present small interfaces and keep behavior local.

**Tech Stack:** React 19, TypeScript 6, Vite 8, Tailwind CSS 4, shadcn/ui, Base UI, Recharts 3, Lucide, Storybook 10, Vitest, Testing Library, and Playwright.

**Spec:** `docs/superpowers/specs/2026-09-05-co2-forecast-lab-design-system-v2-design.md`

## Global Constraints

- The implementation branch is `feat/design-system-v2`, based on green main merge `f9463bcdafeea94e30d66640decf8ce7724e79bd`.
- Use Base UI through current shadcn generation; do not introduce Radix, React Aria, Carbon React, Carbon Charts, TanStack Table, or another UI library.
- The exact theme storage key is `co2-forecast-lab-theme`; accepted values are only `light`, `dark`, and `system`; invalid storage falls back to `system`.
- Preserve the historical-only boundary, SARIMA development selection, Exponential Smoothing lower final-test MAE, post-selection final-test evaluation, 90% prediction interval wording, one-step coverage boundary, fixed-origin serving protocol, and exploratory 8 Isolation Forest / 0 residual anomaly semantics.
- Do not change `src/`, `data/`, `reports/`, `models/`, backend behavior, deployment configuration, README live-demo claims, or hosted services.
- Keep Recharts and direct composition available; shared chart modules may centralize tokens, formatting, legends, and annotations but must not become a generic chart renderer.
- Keep page-level overflow at zero on 390px mobile; wide data tables may scroll inside their own bounded wrapper.
- Use `retries: 0`; canonical visual screenshots are light-theme Linux/Chromium evidence only.
- Every implementation slice ends with its named test command and a logical commit.

## File and module map

The following ownership is the target after migration. Existing filenames stay in place when moving them would add risk without improving the interface.

- `frontend/components.json` — current shadcn CLI configuration for the existing Vite app.
- `frontend/src/lib/utils.ts` — one `cn(...inputs: ClassValue[]): string` class-merging seam used by source-owned primitives.
- `frontend/src/theme/ThemeProvider.tsx` — `Theme` type, `ThemeProvider`, `useTheme`, system preference listener, persistence, and resolved root class behavior.
- `frontend/src/components/ui/` — source-owned Base UI primitives: `button.tsx`, `badge.tsx`, `alert.tsx`, `select.tsx`, `skeleton.tsx`, `sheet.tsx`, `dropdown-menu.tsx`, and `table.tsx`.
- `frontend/src/components/layout/AppShell.tsx` — responsive custom shell, desktop rail, mobile Sheet navigation, status, and theme control.
- `frontend/src/components/layout/PageHeader.tsx` — one page heading, context copy, optional action/context slot, and heading ref/id.
- `frontend/src/components/domain/` — accepted evidence modules: `HistoricalScope`, `DataProvenance`, `ReadinessStatus`, `LimitationCallout`, `MetricDefinition`, `ModelSelectionSummary`, `ModelComparison`, `ForecastEvidence`, `ForecastIntervalLegend`, and `AnomalyEvidence`.
- `frontend/src/components/charts/chart-grammar.ts` — semantic chart color tokens, date/value formatters, and small chart constants.
- `frontend/src/components/charts/ChartTooltip.tsx` and `ChartLegend.tsx` — accessible text-first Recharts adapters that accept only the series data they display.
- `frontend/src/components/charts/TimeSeriesChart.tsx`, `ForecastChart.tsx`, and `AnomalyTimeline.tsx` — existing chart implementations retained or moved with compatibility exports; direct Recharts composition remains visible.
- `frontend/src/components/states/LoadingState.tsx` and `ErrorMessage.tsx` — primitive-backed loading/error state modules, with compatibility exports only while consumers migrate.
- `frontend/src/pages/*.tsx` — five page compositions that consume domain modules and `PageHeader`, not raw repeated evidence markup.
- `frontend/src/index.css` and `frontend/index.html` — semantic light/dark values, Tailwind v4 mappings, base focus/typography/motion rules, and pre-paint theme bootstrap.
- `frontend/src/App.tsx` and `frontend/src/main.tsx` — provider/app-shell composition without API or page-data contract changes.
- `frontend/.storybook/preview.tsx` and `frontend/.storybook/main.ts` — theme review and intentional story taxonomy support.
- `frontend/src/**/*.stories.tsx`, `frontend/src/**/*.test.tsx`, and `frontend/e2e/*.spec.ts` — governed fixtures and regression coverage.
- `DESIGN.md` and `docs/frontend.md` — synchronized implementation contract and usage/review guide.

## Slice 1: Foundation, CLI configuration, tokens, and adopted primitives

### Task 1.1: Verify the clean foundation and initialize shadcn

**Files:**

- Create: `frontend/components.json` through the current CLI.
- Modify only if emitted: `frontend/package.json`, `frontend/package-lock.json`, `frontend/src/index.css`, `frontend/tsconfig.json`, `frontend/tsconfig.app.json`, `frontend/vite.config.ts`.
- Inspect after generation: every emitted file under `frontend/src/components/ui/`.

**Interfaces:**

- Consumes: clean `feat/design-system-v2`, existing Tailwind v4/Vite configuration, current official shadcn CLI 4.21.0.
- Produces: Base UI configuration with `style: "new-york"`, `tailwind.config` blank for v4, `tailwind.css: "src/index.css"`, `cssVariables: true`, TypeScript aliases, and `iconLibrary: "lucide"` or the exact current schema equivalent.

- [ ] Record `git status --short` and `git diff` before generation.
- [ ] Run from `frontend/`:

```powershell
npx --yes shadcn@latest init --template vite --base base --yes --no-monorepo --css-variables --no-pointer
```

- [ ] Inspect `frontend/components.json` against the live schema at `https://ui.shadcn.com/schema.json`; retain only fields emitted by the CLI.
- [ ] Inspect the package diff and reject any Radix, React Aria, Carbon, or unrelated UI dependency.
- [ ] Reconcile any CLI rewrite of `src/index.css` with the existing product token contract before adding components.
- [ ] Run `npm ls --depth=0` and record exact new direct dependencies in the implementation commit message or PR notes.

### Task 1.2: Establish the semantic token contract

**Files:**

- Modify: `frontend/src/index.css`.
- Modify: `DESIGN.md`.
- Test: `frontend/src/theme/ThemeProvider.test.tsx` will assert root class/token behavior after Task 2; foundation smoke checks will assert required CSS variable names exist.

**Interfaces:**

- Consumes: approved OKLCH values in Section 10 of the spec.
- Produces: `@theme inline` mappings for `background`, `foreground`, `card`, `popover`, `primary`, `secondary`, `muted`, `accent`, `destructive`, `border`, `input`, `ring`, plus `success`, `warning`, `anomaly`, `status-ready`, `status-unavailable`, `chart-historical`, `chart-forecast`, `chart-interval`, `chart-anomaly`, and `chart-grid`.

- [ ] Replace legacy-only `--color-canvas`/`--color-ink` references with one semantic value per role; compatibility aliases may remain only when they point to the standard semantic variable.
- [ ] Add light values: background `oklch(0.975 0.006 235)`, foreground `oklch(0.245 0.025 245)`, surface/card `oklch(0.995 0.004 235)`, surface-muted/secondary `oklch(0.945 0.009 235)`, border `oklch(0.875 0.014 240)`, primary `oklch(0.48 0.12 238)`, primary-muted `oklch(0.92 0.04 238)`, muted-foreground `oklch(0.50 0.025 245)`, success `oklch(0.58 0.12 155)`, warning `oklch(0.64 0.17 78)`, anomaly `oklch(0.68 0.15 65)`, destructive `oklch(0.58 0.18 28)`, and ring `oklch(0.48 0.12 238)`.
- [ ] Add dark values from the approved contract: background `oklch(0.18 0.02 245)`, foreground `oklch(0.93 0.015 240)`, surface/card `oklch(0.23 0.022 245)`, surface-muted/secondary `oklch(0.28 0.025 245)`, border `oklch(0.40 0.025 245)`, primary `oklch(0.72 0.12 238)`, primary-muted `oklch(0.32 0.07 238)`, muted-foreground `oklch(0.72 0.025 240)`, success `oklch(0.72 0.12 155)`, warning `oklch(0.76 0.15 90)`, anomaly `oklch(0.78 0.13 75)`, destructive `oklch(0.72 0.14 28)`, and ring `oklch(0.80 0.10 238)`.
- [ ] Keep chart roles distinct: neutral historical, blue forecast, soft blue interval, amber anomaly, and rule grid; use `currentColor`/token references rather than literal palette values in components.
- [ ] Preserve reduced-motion rules and add a visible, token-backed `:focus-visible` ring.
- [ ] Synchronize the same role names, values, and policy in `DESIGN.md`.

### Task 1.3: Add only the approved source-owned primitives

**Files:**

- Create: `frontend/src/components/ui/button.tsx`, `badge.tsx`, `alert.tsx`, `select.tsx`, `skeleton.tsx`, `sheet.tsx`, `dropdown-menu.tsx`, and `table.tsx` through the current CLI.
- Create if emitted and used: `frontend/src/lib/utils.ts`.
- Test: stories for each adopted primitive in `frontend/src/components/ui/*.stories.tsx`.

**Interfaces:**

- Consumes: current Base UI generated APIs, including `render` composition where emitted.
- Produces: importable primitives with the generated props plus CO2-specific class variants; `Button` supplies `variant`/`size`, `Sheet` supplies left-side modal behavior, `Select` supplies keyboard selection, and `DropdownMenu` supplies theme actions.

- [ ] Run:

```powershell
npx --yes shadcn@latest add button badge alert select skeleton sheet dropdown-menu table --yes
```

- [ ] Inspect each generated module for Base UI imports and `data-slot` attributes; delete unused generated variants only after a repository-wide consumer search.
- [ ] Keep source ownership local: no wrapper that simply renames every generated export, and no generic dashboard block.
- [ ] Add one representative story per required primitive, covering default/disabled or unavailable behavior where meaningful.
- [ ] Run `npm run lint`, `npm run test`, and `npm run build` before committing.
- [ ] Commit: `feat(ui): establish design system foundations`.

## Slice 2: Theme contract, responsive shell, and PageHeader

### Task 2.1: Write failing theme tests and implement the provider

**Files:**

- Create: `frontend/src/theme/ThemeProvider.tsx`.
- Create: `frontend/src/theme/ThemeProvider.test.tsx`.
- Modify: `frontend/src/main.tsx`, `frontend/index.html`, `frontend/src/index.css`.
- Story: `frontend/src/theme/ThemeProvider.stories.tsx`.

**Interfaces:**

```typescript
export type Theme = 'light' | 'dark' | 'system'

export interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
}

export interface ThemeContextValue {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
}

export function ThemeProvider(props: ThemeProviderProps): JSX.Element
export function useTheme(): ThemeContextValue
```

- [ ] Add failing tests for no storage/system default, saved light/dark classes, invalid storage fallback, exact persistence values, system `matchMedia` changes, and an accessible theme trigger contract.
- [ ] Run the focused test before implementation:

```powershell
npm run test -- src/theme/ThemeProvider.test.tsx
```

Expected: failures for the missing provider and behavior.

- [ ] Implement safe storage reads that accept only `light`, `dark`, and `system`; catch storage access errors; persist only the exact theme string.
- [ ] Apply exactly one explicit `light` or `dark` class to `document.documentElement`; subscribe to `MediaQueryList` changes only while `theme === 'system'`; remove the listener on cleanup.
- [ ] Add a small synchronous bootstrap in `frontend/index.html` that reads `co2-forecast-lab-theme`, validates it, resolves system preference, and applies the root class before the module loads. The bootstrap must not add a second key or long transition.
- [ ] Wrap `<App />` with `ThemeProvider` in `main.tsx`; run the focused test again and expect PASS.

### Task 2.2: Add the custom AppShell and PageHeader

**Files:**

- Create: `frontend/src/components/layout/PageHeader.tsx`.
- Move or modify: `frontend/src/components/AppShell.tsx` to `frontend/src/components/layout/AppShell.tsx`, retaining a compatibility re-export only if existing tests/stories need it during migration.
- Modify: `frontend/src/App.tsx`.
- Modify: `frontend/src/components/AppShell.test.tsx` or its new layout path.
- Story: `frontend/src/components/layout/AppShell.stories.tsx`, `PageHeader.stories.tsx`.

**Interfaces:**

```typescript
export interface PageHeaderProps {
  title: string
  description: string
  headingId?: string
  headingRef?: React.Ref<HTMLHeadingElement>
  children?: React.ReactNode
}

export function PageHeader(props: PageHeaderProps): JSX.Element

export interface AppShellProps extends PropsWithChildren {
  activePage: PageId
  apiStatus: 'connected' | 'connecting' | 'unavailable'
  onNavigate: (page: PageId) => void
}
```

- [ ] Write failing shell tests for five desktop destinations, exactly one `aria-current="page"`, named mobile menu, Sheet open/close/Escape, all 44px targets, and predictable focus after navigation.
- [ ] Replace the mobile horizontal navigation strip with a compact header and Base UI Sheet from the left; retain the five flat destinations and close the Sheet after selection.
- [ ] Make the mobile page heading the focus target after Sheet navigation; use a `ref`/`tabIndex={-1}` contract on `PageHeader` and restore focus only after the new page is rendered.
- [ ] Add a named DropdownMenu or Select theme control with Light, Dark, and System labels; do not expose only an unlabeled icon.
- [ ] Keep API status as a small status region; do not relabel UI connectivity as governed readiness unless the existing contract proves it.
- [ ] Ensure the desktop rail remains compact, uses active border/background plus text/icon/state, and has no marketing hero.
- [ ] Run focused shell/theme tests and `npm run build`.
- [ ] Commit: `feat(ui): add theme and responsive app shell`.

## Slice 3: Evidence-domain modules and chart grammar

### Task 3.1: Implement accepted domain modules

**Files:**

- Create: `frontend/src/components/domain/HistoricalScope.tsx`, `DataProvenance.tsx`, `ReadinessStatus.tsx`, `LimitationCallout.tsx`, `MetricDefinition.tsx`, `ModelSelectionSummary.tsx`, `ModelComparison.tsx`, `ForecastEvidence.tsx`, `ForecastIntervalLegend.tsx`, and `AnomalyEvidence.tsx`.
- Create: matching `frontend/src/components/domain/*.test.tsx` and governed `*.stories.tsx`.
- Modify: `frontend/src/types/api.ts` only if a shared existing type needs a named alias; do not duplicate API response shapes.

**Interfaces:**

```typescript
export function HistoricalScope(props: { period: string; frequency: string; unit: string }): JSX.Element
export function DataProvenance(props: { dataset: DatasetMetadata; preprocessing: PreprocessingMetadata }): JSX.Element
export function ReadinessStatus(props: { status: 'connected' | 'connecting' | 'unavailable'; detail?: string }): JSX.Element
export function LimitationCallout(props: { title?: string; children: React.ReactNode }): JSX.Element
export function MetricDefinition(props: { label: string; value: string; detail?: string }): JSX.Element
export function ModelSelectionSummary(props: { selection: ModelSelection; developmentMae?: number; foldCount: number }): JSX.Element
export function ModelComparison(props: { selectedModel: string; finalTest: EvaluationSplit }): JSX.Element
export function ForecastEvidence(props: { forecast: ForecastResponse; historical: HistoricalPoint[] }): JSX.Element
export function ForecastIntervalLegend(props: { nominalCoverage: number; coverageScope: string }): JSX.Element
export function AnomalyEvidence(props: { anomalies: AnomalyPoint[] }): JSX.Element
```

- [ ] Author the failing test cases first for semantic landmarks/`dl`/tables, model selection versus final-test winner, exact prediction-interval terminology, one-step limitation, and 8/0 exploratory anomaly language.
- [ ] Implement small, deep modules: each module owns its label/semantic copy and accepts existing domain types; callers do not reconstruct its meaning from primitives.
- [ ] Use `aria-live="polite"` only for status updates and `role="alert"` only for actual API failure; anomaly evidence stays an ordinary exploratory section.
- [ ] Ensure model modules render separate labels for `Selected by development` and `Lowest final-test MAE`; never render `Best model`.
- [ ] Ensure interval modules render `prediction interval`, `fixed-origin multi-step`, `forecast origin`, and the one-step coverage limitation in visible text.
- [ ] Ensure anomaly modules render Isolation Forest and residual methods with text plus distinct filled/outlined symbols; amber is not destructive red.
- [ ] Run focused domain tests and commit: `feat(ui): add scientific evidence components`.

### Task 3.2: Centralize thin Recharts grammar

**Files:**

- Create: `frontend/src/components/charts/chart-grammar.ts`, `ChartTooltip.tsx`, and `ChartLegend.tsx`.
- Move or modify: `frontend/src/components/TimeSeriesChart.tsx`, `ForecastChart.tsx`, and `AnomalyTimeline.tsx` into `frontend/src/components/charts/` with compatibility exports only if required.
- Test: `frontend/src/components/charts/chart-grammar.test.ts`, chart stories.

**Interfaces:**

```typescript
export const chartColors: Readonly<Record<'historical' | 'forecast' | 'interval' | 'anomaly' | 'grid', string>>
export function formatChartDate(value: string): string
export function formatPpm(value: number | null | undefined): string
export function ChartTooltip(props: ChartTooltipProps): JSX.Element
export function ChartLegend(props: ChartLegendProps): JSX.Element
```

- [ ] Keep direct `LineChart`/`ComposedChart` composition in the chart implementations; centralize only tokens, exact ppm/date formatting, legend text, and shared accessibility labels.
- [ ] Add `accessibilityLayer` to Recharts v3 charts where the installed types and runtime support it; retain `role="img"` labels and a nearby text/table explanation.
- [ ] Keep forecast history neutral solid, forecast blue solid, visible origin rule/label, soft interval band, and ppm exact tooltips.
- [ ] Keep anomaly symbols distinct by fill/stroke/shape and include an explicit inline legend.
- [ ] Add empty-data guards that render an explanatory state rather than invalid `Math.min(...[])` ranges.
- [ ] Run chart tests, lint, typecheck/build, and commit with Slice 3 if not already committed.

## Slice 4: Migrate the five pages and shared states

### Task 4.1: Refactor shared LoadingState, ErrorMessage, and MetricCard

**Files:**

- Move or modify: `frontend/src/components/LoadingState.tsx`, `ErrorMessage.tsx`, and `MetricCard.tsx`.
- Tests/stories: matching existing files and new `frontend/src/components/states/*.stories.tsx` if moved.

**Interfaces:**

```typescript
export function LoadingState(props?: { label?: string }): JSX.Element
export function ErrorMessage(props: { message: string; onRetry?: () => void }): JSX.Element
export function MetricCard(props: { label: string; value: string; detail?: string }): JSX.Element
```

- [ ] Replace raw buttons, borders, and skeleton blocks with adopted primitives while preserving `role=status`, `aria-busy`, `role=alert`, retry callback, API-unavailable copy, and reduced motion.
- [ ] Keep `MetricCard` as a restrained top-rule metric, not an elevated card wall; use `MetricDefinition` for new semantic metric contexts.
- [ ] Run existing loading/error/metric tests before moving to page migration.

### Task 4.2: Migrate each page through `PageHeader` and domain modules

**Files:**

- Modify: `frontend/src/pages/OverviewPage.tsx`, `DataExplorerPage.tsx`, `ForecastingPage.tsx`, `AnomalyDetectionPage.tsx`, and `ModelEvaluationPage.tsx`.
- Modify: `frontend/src/App.tsx` only for imports and heading-ref plumbing; keep `useDashboardData`, `getForecast`, and all page props/API calls intact.
- Update tests: `frontend/src/pages/ForecastingPage.test.tsx`, `ModelEvaluationPage.test.tsx`, and add page tests for Overview/Data Explorer/Anomaly Detection if the new modules require direct coverage.

**Interfaces:**

- Consumes: existing `HistoricalPoint`, `ForecastResponse`, `AnomalyPoint`, and `ModelInfo` types; domain modules from Slice 3.
- Produces: each page has one `PageHeader`, one primary evidence region, supporting evidence, and nearby limitations/provenance; no page introduces API fields or scientific claims.

- [ ] Overview: place `HistoricalScope`, `ModelSelectionSummary`, primary historical chart, bounded metrics, final-test comparison, and nearby limitation/provenance in that order.
- [ ] Data Explorer: place provenance and causal preparation before the historical chart; keep dense data tables bounded to their local scroll region.
- [ ] Forecasting: place `ForecastEvidence` and `ForecastIntervalLegend` near the chart; keep visible fixed-origin, forecast-origin, prediction-interval, and one-step boundary copy.
- [ ] Anomaly Detection: place `AnomalyEvidence` before/near the timeline and table; keep 8 Isolation Forest / 0 residual counts exploratory.
- [ ] Model Evaluation: place `ModelSelectionSummary` beside a `ModelComparison` that clearly separates SARIMA development selection from Exponential Smoothing final-test ranking.
- [ ] Replace all page-level raw native selects/buttons used for adopted interactions with `Select`/`Button`; keep native tables where semantic table behavior is the clearer interface.
- [ ] Run all unit/component tests, lint, and build.
- [ ] Commit: `feat(ui): migrate forecast lab pages`.

## Slice 5: Storybook, component tests, and Playwright contracts

### Task 5.1: Reorganize Storybook and add theme/a11y fixtures

**Files:**

- Modify: `frontend/.storybook/main.ts`, `frontend/.storybook/preview.tsx`.
- Modify/create stories under `frontend/src/` with titles `Foundations/*`, `Primitives/*`, `Layout/*`, `Domain/*`, `Charts/*`, and `States/*`.

**Interfaces:**

- Consumes: adopted primitive/domain/chart modules and deterministic fixtures from `frontend/src/test/fixtures.ts`.
- Produces: focused story catalog with light/dark review, no a11y disable rules, and governed states for long content, unavailable/error, narrow/mobile, selected-vs-final-test, 8/0 anomalies, historical-only, and interval limitation.

- [ ] Add foundation stories `Foundations/Colors`, `Typography`, `Spacing`, and `Theme`.
- [ ] Add adopted primitive stories only for the eight required primitives.
- [ ] Add domain/chart/state stories with explicit `parameters.viewport`/theme controls where needed; do not create duplicate stories for ungoverned combinations.
- [ ] Preserve the existing Storybook Vitest browser project and a11y error policy.
- [ ] Run `npm run build-storybook` and `npm run test:storybook`.

### Task 5.2: Expand Vitest and Playwright behavior tests

**Files:**

- Modify/create component tests in `frontend/src/theme/`, `frontend/src/components/layout/`, `frontend/src/components/domain/`, and existing state/page test paths.
- Modify: `frontend/e2e/helpers.ts`, `dashboard.spec.ts`, `navigation.spec.ts`, `error-recovery.spec.ts`, and `visual.spec.ts`.
- Modify: `frontend/playwright.config.ts` only for deterministic light storage bootstrap; keep `retries: 0`, desktop 1440×900, mobile 390×844, reduced motion, and two projects.

**Interfaces:**

- Consumes: rendered routes and real API positive path; request interception remains limited to failure recovery.
- Produces: assertions for Sheet navigation/focus, `aria-current`, theme selection/persistence/system preference, no document overflow, scientific copy, and retry recovery.

- [ ] Add tests for Light, Dark, and System selection plus reload persistence using `co2-forecast-lab-theme`.
- [ ] Add Playwright setup that writes the exact `light` storage value before visual pages load; do not rely on host color preference.
- [ ] Add mobile assertions that the named menu opens a left Sheet, all five destinations exist, selecting a destination closes it, and the new page heading is focused or the documented trigger fallback is focused.
- [ ] Assert all pages retain historical/not-live, selection, interval, and anomaly boundary language.
- [ ] Assert mobile document width equals viewport width; permit only local table wrappers to scroll.
- [ ] Run:

```powershell
npm run test
npm run test:e2e
```

- [ ] Commit: `test(ui): expand Storybook and browser coverage`.

## Slice 6: Canonical visual refresh, documentation, and full verification

### Task 6.1: Synchronize documentation

**Files:**

- Modify: `DESIGN.md`.
- Modify: `docs/frontend.md`.
- Modify `docs/verification.md` only if the actual baseline command/procedure needs clarification.

- [ ] Document semantic tokens and exact values, Light/Dark/System and storage key, compact AppShell/Sheet behavior, adopted primitives, domain ownership, chart grammar, panel/card policy, Storybook taxonomy, and four-baseline Linux policy.
- [ ] Document commands for local frontend checks, Storybook/a11y, Playwright functional tests, and committed baseline verification.
- [ ] Do not add a Live Demo section or hosted URL.
- [ ] Run a repository search confirming the old design contract does not contradict the implemented source.

### Task 6.2: Render and inspect every surface

**Files:**

- Modify source files only when a rendered finding is actionable.
- Expected visual files: the four existing Linux snapshots under `frontend/e2e/snapshots/visual.spec.ts-snapshots/`.

- [ ] Start the real API/Vite environment through the existing E2E harness; do not mock successful dashboard data.
- [ ] Inspect Overview, Data Explorer, Forecasting, Anomaly Detection, and Model Evaluation at 1440×900, 390×844, and approximately 768px in light and dark themes.
- [ ] Check hierarchy, no card wall, model distinction, interval language, anomaly meaning, Sheet behavior, focus, and document overflow.
- [ ] Force `co2-forecast-lab-theme=light` before visual screenshots.
- [ ] Run the existing canonical Linux update mechanism from `docs/verification.md`. If the local workflow cannot update safely, use one temporary branch-only Linux workflow to produce only the four named PNG artifacts, inspect all four, copy only verified files, remove the temporary workflow, and ensure the final workflow contains no `--update-snapshots`.
- [ ] Keep `retries=0`, no broad masks, no random waits, and no tolerance increase without a documented rendered reason.
- [ ] Inspect all four screenshot diffs and commit only Linux/Chromium baselines: `test(ui): refresh canonical visual baselines`.

### Task 6.3: Run all gates and perform the final scope review

**Files:**

- No backend/model/data/evidence files may be modified.
- Review: `git diff -- src/models src/evaluation src/anomaly data reports` must be empty.

- [ ] Run from `frontend/`:

```powershell
npm ci
npm run lint
npm run test
npm run build
npm run build-storybook
npx playwright install --with-deps chromium
npm run test:storybook
npm run test:e2e
npm run test:e2e:verify-baselines
npm audit --audit-level=high
```

- [ ] Run repository safety gates from the root:

```powershell
ruff check src tests
python -m compileall -q src
python -m pytest -q
python -m src.verify_repository
docker compose config --quiet
python -c "from src.api.main import app; print(app.title)"
```

- [ ] If notebook execution is required by the repository gate, execute it to a temporary output directory and do not commit the output.
- [ ] Run `npm ls --depth=0`; confirm no duplicate Radix/Base UI tree, no unused adopted primitive dependency, and no Storybook/test code in the production build.
- [ ] Run the two-axis manual review against `f9463bcdafeea94e30d66640decf8ce7724e79bd...HEAD`: Standards checks against `AGENTS.md`/`DESIGN.md`; Spec checks against the approved design; record findings and fixes in the final report.
- [ ] Commit documentation as `docs(ui): synchronize design system v2 contract` if documentation was not committed with the relevant slice.
- [ ] Run `git diff --check`, `git status --short --untracked-files=all`, and verify only approved frontend/docs/snapshot paths are changed.

## Plan self-review

- Spec coverage: Slice 1 covers CLI, dependencies, tokens, Tailwind v4, and required primitives; Slice 2 covers theme, FOUC, shell, Sheet, PageHeader, focus, and touch targets; Slice 3 covers all ten domain modules and chart grammar; Slice 4 covers state migration and all five pages; Slice 5 covers Storybook, Vitest, Playwright, themes, and API failure; Slice 6 covers documentation, rendered review, canonical Linux baselines, gates, security, and scope review.
- Scientific coverage: every page migration task names the historical-only, model-selection, interval, final-test, and anomaly invariants that must remain visible; no task permits API or evidence changes.
- Type consistency: theme exports `ThemeProvider`, `useTheme`, `Theme`, and `ThemeContextValue`; `PageHeader` and `AppShell` contracts are defined before page consumers; domain props reuse imported API types; chart seams use explicit `chartColors`, `formatChartDate`, `formatPpm`, `ChartTooltipProps`, and `ChartLegendProps`.
- YAGNI: only eight required primitives are generated; Card, Sidebar, DataTable/TanStack, and Carbon are excluded; chart helpers stay thin; compatibility re-exports are removed after consumer search.
- Placeholder scan: the plan contains no unresolved implementation placeholder or deferred-design language; each task has an exact file, interface, test, command, and commit action.
- Execution mode: this plan is executed inline in this task with no subagents.
