# CO2 Forecast Lab Design System v2

## 1. Status and metadata

| Field | Decision |
|---|---|
| Status | Stage A design specification; implementation has not started |
| Issue | #25 — Frontend design: specify and implement CO2 Forecast Lab Design System v2 |
| Parent | #24 — CO2 Forecast Lab v2 design system and verified live portfolio delivery |
| Deployment follow-up | #26; outside this issue |
| Baseline | `main` at `049789a257f1065807286e63c02446d2ed54770a` |
| Branch | `docs/design-system-v2-spec` |
| Scope | `frontend/` presentation architecture and design language only |
| Source of truth | This specification defines the v2 delta; `DESIGN.md` remains the current product design contract until the implementation PR synchronizes it |
| Unresolved questions | NONE |

This document is deliberately implementation-ready but does not itself initialize
shadcn, install packages, edit runtime code, edit `DESIGN.md`, or refresh visual
baselines. The implementation PR must turn this document into code in reviewable
slices and keep the repository green after each slice.

## 2. Problem

CO2 Forecast Lab already communicates unusually important scientific boundaries:
historical-only data, causal preparation, development-fold selection, one-time
final-test evaluation, fixed-origin serving, bounded prediction-interval claims,
and exploratory anomaly signals. The dashboard is visually calm and the current
browser evidence is useful. The problem is not missing decoration; it is missing
a small, explicit system that makes those decisions consistent across five pages.

The current interface feels like a custom dashboard rather than a mature design
system because the implementation has a single token file and several good
one-off components, but no shared primitive layer, no deliberate theme contract,
no mobile drawer model, no domain component boundary for scientific semantics,
and no intentional Storybook taxonomy. Repeated utility-class decisions are
spread across `AppShell`, pages, tables, loading/error states, and three chart
wrappers. A future change can therefore improve one surface while silently
diverging from another.

The v2 goal is a restrained, evidence-first component foundation with small
interfaces, clear seams, and reusable domain modules. It must improve hierarchy,
keyboard/mobile behavior, themeability, and reviewability without changing the
API contract, data semantics, model language, anomaly caveats, or governed
evidence.

## 3. Current-state audit

The audit is based on `DESIGN.md`, `CONTEXT.md`, the frontend source, current
Storybook stories/tests, current Playwright tests and committed Linux snapshots,
plus a live local render of all five pages at the requested mobile viewport and
the desktop target. The local stack was run with the repository pipeline, FastAPI,
and Vite; generated pipeline output was runtime-only or restored before this
documentation change. No current screenshot was committed.

The verified frontend baseline is React/ReactDOM `19.2.7`, Vite `8.0.16`,
TypeScript `6.0.3`, Tailwind CSS and `@tailwindcss/vite` `4.3.0`, Recharts
`3.8.1`, Lucide `1.17.0`, Storybook `10.6.0`, Vitest `4.1.11`, and Playwright
`1.62.1` as resolved by `frontend/package-lock.json` on this branch.

| Category | CURRENT | PROBLEM | KEEP | CHANGE | RATIONALE |
|---|---|---|---|---|---|
| Product visual identity | Calm blue/neutral scientific workbench, evidence-led copy | Identity is expressed by scattered classes rather than named roles | Scientific, calm, precise tone | Encode identity in semantic variables and foundation stories | Reviewers should recognize one coherent product language |
| Semantic color tokens | Tailwind v4 `@theme` names such as `canvas`, `surface`, `ink`, `accent`, `anomaly` in `frontend/src/index.css` | Tokens are not paired foreground/background roles and have no dark theme | OKLCH palette, one blue accent, reserved anomaly amber | Map to shadcn semantic variables plus domain chart/status variables | Theme changes should be local and safe |
| Light theme | Single light palette | No explicit theme contract or contrast review | Current light values as starting points | Intentional light token set with contrast checks | Light remains the default visual reference |
| Dark theme | Not implemented | Inversion would make rules, charts, amber signals, and muted text ambiguous | Meaning of every semantic role | Add deliberate `.dark` values and chart-specific values | Dark mode must preserve scientific interpretation |
| Typography | Inter/system-first stack, tabular metric class | Repeated heading/metadata utility strings, no documented type scale in code | System-first font, tabular numbers, readable metadata | Define a small type role vocabulary and use it consistently | Avoid font novelty while improving hierarchy |
| Spacing/density | Mostly `space-y-10`, `gap-5/6/8`, and page-specific padding | Density is consistent by instinct but not enforceable | Compact, readable, reflow-not-shrink principle | Define page gutter, section, evidence, and control spacing tokens | Dense evidence needs predictable rhythm |
| Radius/borders/elevation | Thin borders and 6/8/12px-like radii; one tooltip shadow | Radius and overlay treatment are repeated ad hoc | Structural borders, minimal elevation | Define radius scale and overlay-only elevation | Prevent generic card/glass drift |
| AppShell/sidebar/navigation | Hand-built 248px desktop aside; sticky header; mobile horizontal nav | Desktop is not collapsible; mobile consumes header space and does not model a drawer; shell state is duplicated by breakpoint | Five destinations, `aria-current`, status region, identity | Use a compact shell seam with persistent desktop rail and Base UI Sheet mobile navigation; evaluate shadcn Sidebar but do not adopt its full dashboard block by default | Shell is the highest-leverage shared interface |
| Page header hierarchy | Sticky shell title plus page-local `h2` | Two title levels compete; overview hero is larger than evidence context | Clear page titles and short methodological context | Add a shared `PageHeader` contract: title, description, optional context/action | Every page should establish its question before details |
| Panel/card usage | Most evidence is border separators; `MetricCard` is actually a top-rule metric; error/image use rounded containers | No explicit region policy; future additions could become a KPI wall | Thin structure and restrained metric presentation | Treat sections/evidence regions as default; use Card only for bounded interactive/overlay content | Containers should carry meaning, not decorate paragraphs |
| Metric presentation | `MetricCard` repeated across pages, with labels and details | Metrics can appear as unrelated rows and are not grouped by reviewer question | Tabular values and denominator/context details | Replace with a small `Metric`/`MetricGroup` contract and limit reviewer-critical metrics | Makes hierarchy visible without adding cards |
| Status/badge language | Text chips for selected/final-test labels; colored API dot | Status shape and semantics are not centralized; dot carries state alone | Explicit words `Selected by development`, `Lowest final-test MAE`, `API connected` | Adopt Badge for compact labels plus text/icon; reserve Alert for substantive state | Scientific and operational status need different emphasis |
| Buttons/actions | Native buttons styled inline; retry and navigation use different classes | No shared focus/size/variant contract | Keyboard behavior and 44px intent | Adopt Button variants for retry, shell, theme, and horizon actions | Shared interaction semantics reduce drift |
| Tabs/selects/tooltips | Native select only for forecast horizon; Recharts tooltips; no tabs | Native controls and chart tooltip styling are disconnected; critical methodology must not be hover-only | Native select behavior where it is adequate; inline methodology | Use Select only where styling/keyboard behavior needs it; keep text alternatives beside charts; no page Tabs by default | Avoid a component for a pattern that is not present |
| Loading/skeleton | `LoadingState` uses three animated rounded blocks and `aria-busy` | Shape is generic and not tied to page regions; animation is not a theme-aware primitive | Explicit loading announcement and reduced motion rule | Adopt Skeleton with page-region shapes and no content claims | Loading should preview structure without pretending to be data |
| Empty/error states | `ErrorMessage` is explicit, retryable, and `role=alert`; no first-class empty state | Error panel is visually separate from shared state vocabulary | API unavailable copy, retry, alert semantics | Add Alert/empty state contracts and preserve current retry path | Failure states are part of the reviewer path |
| Data tables | Semantic `<table>`, scope headers, horizontal overflow, sticky forecast header | Table styling repeated in three pages; selected/final-test semantics partly hidden in cells | Real tables, numeric right alignment, local overflow | Adopt a styled Table primitive and domain comparison/forecast table wrappers; no TanStack | Current data volume does not require table framework machinery |
| Charts | Three direct Recharts wrappers with shared grid/axis/tooltip styling | Each wrapper repeats grammar; no accessibility layer or shared chart config; current forecast legend/tooltip language is not centralized | Recharts, responsive containers, units, origin, method labels | Add a thin chart foundation/config and domain chart modules without hiding Recharts | Centralize meaning while preserving direct chart control |
| Legends | Recharts top legends with text labels | Placement and mobile wrapping are per-chart; visual meaning still depends partly on color | Explicit series names and marker differences | Use consistent legend position/stacking and direct labels where space permits | Consistency improves reading across pages |
| Chart tooltips | Recharts default tooltip customized with CSS | Exact date/value/protocol fields differ by chart; tooltip is not a sufficient screen-reader alternative | Exact ppm values and labels | Define a shared tooltip content contract; keep nearby text/table alternative | Hover detail must not be the only route to evidence |
| Annotations | Forecast origin `ReferenceLine` with label | Annotation styling is only implemented for forecast origin; no shared annotation grammar | Visible origin boundary and caveat text | Standardize origin/threshold/agreement annotations with text and non-color symbols | Annotations explain analytical boundaries |
| Model-selection semantics | Overview and evaluation distinguish selection and final-test winner in copy/table labels | The distinction is distributed across metrics, paragraphs, and row badges; a future card could conflate them | SARIMA development-selected vs Exponential Smoothing final-test MAE distinction | Use `ModelSelectionSummary` and `ModelComparison` with separate evidence regions | This is a scientific invariant, not a visual preference |
| Forecast-interval semantics | Forecast page says 90% prediction interval and one-step coverage limitation | The chart itself does not encode protocol/origin as a reusable contract | Never say confidence interval; fixed-origin and one-step distinction | Use `ForecastEvidence` + `ForecastIntervalLegend` with adjacent limitation | Prevents overclaiming at the chart seam |
| Anomaly semantics | Amber IF markers, outlined residual markers, agreement text; current 8 vs 0 counts | Marker grammar is local and “signal” boundary is page copy only | Exploratory language, 8 Isolation Forest, 0 residual | Use `AnomalyEvidence` with an explicit inline signal legend; no alert styling | Statistical signals are not incidents |
| Focus/keyboard | Global `:focus-visible`; buttons and native select keyboard accessible | Ring is a raw color-mix rule; mobile nav duplicates controls; charts lack keyboard layer | Visible focus and semantic controls | Map `ring` token and add explicit focus/keyboard tests for drawer, theme, controls, chart alternatives | Focus should be testable and theme-safe |
| Mobile behavior | No page overflow at 390×844; local table overflow; horizontal nav | Five labels compete in a strip; no accessible mobile navigation affordance; chart minimum width is not a documented contract | No document overflow and local overflow only | Compact header + Sheet/drawer; preserve minimum chart height and table wrapper | Mobile should reflow, not squeeze navigation/evidence |
| Storybook | Stories exist for shared components, all under `Components/*`; a11y addon configured | No foundations, theme, state, domain, or chart taxonomy; few responsive/interaction states | Existing representative story tests and a11y gate | Reorganize into a small intentional catalog and add light/dark states | Storybook is the design review surface |
| Visual regression | Four focused Linux/Chromium snapshots and baseline verifier | Coverage is intentionally narrow but v2 ownership rules are not in code/docs | Four-surface discipline, canonical Linux, no update in final CI | Refresh only selected reviewer-critical regions after implementation | Keep visual evidence small and reviewable |

The strongest existing qualities are semantic honesty, a clear source-of-truth
design contract, token names that already map to product meaning, real API-backed
positive-path E2E coverage, explicit retry/empty-like failure behavior, and
committed reviewer-critical Linux snapshots. V2 is a refinement of that system,
not a visual rebrand.

## 4. Goals

1. Give the frontend one coherent component foundation while retaining Vite,
   React 19, TypeScript, Tailwind CSS v4, Recharts, Lucide, Storybook, Vitest,
   and Playwright.
2. Make semantic tokens, light/dark themes, focus treatment, spacing, and
   surface hierarchy consistent across all five pages.
3. Put scientific meaning behind small domain interfaces that are easy to test
   and review in Storybook.
4. Make desktop navigation compact and persistent and mobile navigation
   accessible without document overflow.
5. Make the hierarchy of selection, final-test evaluation, forecast origin,
   interval scope, anomaly methods, provenance, and limitations obvious without
   relying on color or hover.
6. Preserve current API types, loading/error/retry behavior, route behavior,
   governed evidence semantics, and existing positive-path E2E expectations.
7. Create a bounded, reviewer-critical visual regression migration plan.

## 5. Non-goals

- No Next.js, MUI, Ant Design, Chakra, Mantine, Carbon React, or Carbon Charts
  migration.
- No backend, API, CORS, model, feature, evaluation, anomaly, dataset, report,
  manifest, or governed-evidence change.
- No current-data feed, live monitoring, causal climate claim, or production SLA.
- No information architecture change: the five current destinations remain.
- No generic dashboard block copied from a component library.
- No chart-library replacement; Recharts remains the renderer.
- No TanStack Table or DataTable framework until sorting, filtering, pagination,
  or column control is a demonstrated product requirement.
- No broad visual snapshot expansion, snapshot masking, or tolerance inflation.
- No font dependency added for novelty.
- No generic Card wrapper around every existing section.
- No runtime or deployment work in this Stage A PR.

## 6. Options considered

| Option | Compatibility | Accessibility | Customization and identity | Migration/test/dependency cost | Maintenance and portfolio quality | Decision |
|---|---|---|---|---|---|---|
| A. shadcn/ui + Base UI + custom CO2 theme + Recharts + selected Carbon visualization guidance | Direct fit for current Vite/React 19/Tailwind v4 stack; official Vite path and Base UI default are current | Headless primitives supply tested interaction behavior; domain charts and text alternatives remain our responsibility | High: generated source is owned by the repository and tokens retain the scientific identity | Moderate, incremental; adds only adopted primitives and a small utility seam; existing tests remain relevant | Strong: demonstrates judgment, restraint, and domain semantics rather than library branding | **Recommended** |
| B. Full Carbon React + Carbon Charts migration | Requires a second UI/chart ecosystem and a visual/structural migration away from existing Tailwind/Recharts | Mature guidance, but migration creates new integration and semantic mapping surfaces | Lower product distinctiveness and higher risk of looking like a Carbon product | High code churn, new packages, chart rewrite, baseline churn, and duplicated design concepts | Weak fit for this portfolio’s custom evidence-first identity | Rejected |
| C. Continue fully custom Tailwind without a headless foundation | Compatible immediately | Every popup, drawer, theme control, and focus contract remains custom burden | High short-term freedom, but current drift remains likely | Low package cost but high long-term review/test cost; repeated seams persist | Demonstrates styling effort more than system design | Rejected |

Option A is chosen because it adds depth at the right seams: shared primitives
hide interaction mechanics, while domain modules retain the small interfaces
that encode forecast and evaluation meaning. It does not require importing a
complete library visual language.

## 7. Decision

Adopt a source-owned shadcn/ui foundation using the current Base UI variant for
new primitives, a custom semantic token/theme layer, existing Lucide icons, and
existing Recharts. Use Carbon only as a cited visualization design reference:
hierarchy, consistent chart composition, purposeful annotations, concise labels,
legend discipline, and accessible table alternatives.

The future implementation should use the shadcn CLI only as a controlled
generator in a clean implementation slice, then review the generated source as
repository code. It must adopt only the primitives in the inventory below. A
`components.json` file is a generator configuration, not a runtime design
authority; the semantic values in the CSS token layer and the synchronized
`DESIGN.md` remain the product source of truth.

Official research reviewed on 2026-09-05:

- [shadcn Vite installation](https://ui.shadcn.com/docs/installation/vite) documents existing Vite setup, Tailwind v4, aliases, and component addition.
- [shadcn Tailwind v4](https://ui.shadcn.com/docs/tailwind-v4) states full React 19/Tailwind v4 support and OKLCH-oriented defaults.
- [Base UI as the default](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) states that Base UI is now the default for new shadcn projects while Radix remains supported.
- [shadcn theming](https://ui.shadcn.com/docs/theming) recommends CSS variables and semantic background/foreground pairs.
- [shadcn components.json](https://ui.shadcn.com/docs/components-json) documents aliases, blank Tailwind v4 config, and CSS-variable configuration.
- [shadcn Vite dark mode](https://ui.shadcn.com/docs/dark-mode/vite) documents a local `light`/`dark`/`system` provider and local persistence.
- [shadcn charts](https://ui.shadcn.com/docs/components/base/chart) documents Recharts v3, direct composition, chart configuration, theme variables, legends, tooltips, and `accessibilityLayer`.
- [shadcn Sidebar](https://ui.shadcn.com/docs/components/base/sidebar) documents a composable, themeable sidebar with `SidebarProvider`, collapse modes, and a `SidebarTrigger`.
- [shadcn Sheet](https://ui.shadcn.com/docs/components/base/sheet) documents the Base UI-backed dialog sheet and accessible composition.
- [Base UI quick start](https://base-ui.com/react/overview/quick-start) verifies the `@base-ui/react` package and tree-shakable single-package model.
- [Carbon dashboard guidance](https://carbondesignsystem.com/data-visualization/dashboards/), [chart anatomy](https://carbondesignsystem.com/data-visualization/chart-anatomy/), [legends](https://carbondesignsystem.com/data-visualization/legends/), and [axes and labels](https://carbondesignsystem.com/data-visualization/axes-and-labels/) inform visualization composition only.

## 8. Architecture and seams

The future implementation should preserve the current `App.tsx` data-loading
seam and page modules. It should add the following source-owned seams under
`frontend/src/`:

```text
components/ui/                 generated/adapted shadcn primitives only
components/layout/             AppShell, PageHeader, navigation composition
components/domain/             evidence/provenance/status semantic modules
components/charts/              thin Recharts wrappers and shared chart config
components/states/              loading, empty, unavailable, retry presentation
lib/utils.ts                    class composition helper, if generated source needs it
components/theme-provider.tsx  local Light/Dark/System state
```

The exact file split may remain smaller if a module would be shallow. The
deletion test applies: do not add a module that only forwards props to one
consumer. A domain module earns its seam when it prevents semantic duplication
across pages, provides a stable Storybook surface, or centralizes a meaningful
accessibility contract. The external interface should accept data and callbacks
from the page and return rendered evidence; it must not fetch data, read
arbitrary artifact paths, or recalculate model/evaluation results.

`App.tsx` continues to own page selection and `useDashboardData` continues to
own shared API loading. `ForecastingPage` may continue to own the horizon fetch
because that is a real page-specific state transition. Components receive typed
API data or narrow view-model props and do not change API types.

## 9. Component foundation

Use shadcn source-owned components with the Base UI primitive library selected
for new components. Prefer the repository’s existing Lucide stack through the
shadcn icon configuration. Do not import a full block or install components
that have no current consumer.

The foundation contract is:

- Tailwind v4 remains the CSS engine; leave the Tailwind config path blank in
  `components.json` if the CLI is used.
- Add a single `@/*` alias rooted at `frontend/src/*` consistently in the
  TypeScript and Vite resolver configuration, then use it for generated source.
- Use CSS variables for semantic tokens; utilities consume semantic roles such
  as `bg-background`, `text-foreground`, `border-border`, and `ring-ring`.
- Keep the generated primitive API local to `components/ui`; pages should use
  domain/layout modules where a scientific semantic exists.
- Retain direct Recharts composition. A chart helper may standardize config,
  tooltip, legend, and accessibility context but must not hide all Recharts
  components behind an opaque renderer.
- Do not adopt shadcn’s full dashboard example. Compose the shell around the
  product’s five destinations and evidence hierarchy.

### DESIGN.md relationship

The following existing `DESIGN.md` principles remain unchanged: evidence first;
one strong blue accent; thin structural depth; tabular numbers; visible bounded
uncertainty; exploratory anomaly signals; non-color-only meaning; responsive
reflow; restrained cards; system-first typography; and explicit loading/error
states.

The implementation PR must synchronize `DESIGN.md` with the actual v2 values in
these exact areas: frontmatter token names and light/dark values; Typography;
Layout/App shell; Components (Panel, Metric, Callout, Badge, Table); Charts and
visual grammar; Navigation and interaction; Accessibility; and Verification for
UI changes. It must not silently delete the v1 history. The CSS variables are
the executable token layer, the synchronized `DESIGN.md` is the human product
contract, and this spec is the approved v2 delta until both are updated.

## 10. Token architecture

Use OKLCH for the palette where browser/Tailwind v4 support is compatible. All
values must be selected as intentional pairs, then checked for WCAG AA text and
control contrast in both themes. Keep one principal interactive/forecast accent.
Do not use purple gradients, glass, glow, decorative neon, or giant shadows.

### Semantic roles

| Role | Meaning | Light direction | Dark direction |
|---|---|---|---|
| `background` / canvas | Application page background | Very light blue-neutral canvas | Deep blue-neutral canvas, not pure black |
| `foreground` / ink | Primary text, axes, identifiers | Dark blue-neutral ink | Light blue-neutral ink |
| `surface` | Primary evidence region and table/chart surface | Near-white blue-neutral | Elevated but quiet dark surface |
| `surface-muted` | Skeleton, quiet grouping, secondary inset | Cool gray-blue | Darker quiet inset with readable text |
| `border` / rule | Structural separator, chart grid, table rule | Low-contrast blue-gray | Subtle but visible blue-gray |
| `primary` / accent | Primary action, active nav, forecast line, focus association | Existing calm blue accent | Lightened blue with sufficient contrast |
| `primary-muted` | Selected/hover background and interval fill base | Pale blue | Dark blue tint with readable foreground |
| `muted` | Metadata and secondary text | Existing muted ink checked against canvas | Light muted ink checked against surface |
| `success` | API ready/validated state only | Green with text/icon | Dark-theme green with readable pair |
| `warning` | Connecting or bounded caution, only when a real warning exists | Amber/orange distinct from danger | Dark-theme amber with explicit label |
| `danger` | API failure/retry/error only | Red/orange error | Dark-theme danger with explicit label |
| `anomaly` | Exploratory method signal only | Existing amber signal | Lightened amber signal, never an alarm background |
| `ring` / focus | Focus-visible outline | High-contrast blue ring | Light high-contrast ring |

The following concrete values are the starting token contract for the
implementation. The implementation PR may make a small contrast-driven
adjustment, but it must preserve each role’s meaning and record the change in
`DESIGN.md`.

| Token | Light value | Dark value |
|---|---|---|
| `background` | `oklch(0.975 0.006 235)` | `oklch(0.18 0.02 245)` |
| `foreground` | `oklch(0.245 0.025 245)` | `oklch(0.93 0.015 240)` |
| `surface` | `oklch(0.995 0.004 235)` | `oklch(0.23 0.022 245)` |
| `surface-muted` | `oklch(0.945 0.009 235)` | `oklch(0.28 0.025 245)` |
| `border` | `oklch(0.875 0.014 240)` | `oklch(0.40 0.025 245)` |
| `primary` | `oklch(0.48 0.12 238)` | `oklch(0.72 0.12 238)` |
| `primary-foreground` | `oklch(0.99 0.005 235)` | `oklch(0.16 0.02 245)` |
| `primary-muted` | `oklch(0.92 0.04 238)` | `oklch(0.32 0.07 238)` |
| `muted-foreground` | `oklch(0.50 0.025 245)` | `oklch(0.72 0.025 240)` |
| `success` | `oklch(0.58 0.12 155)` | `oklch(0.72 0.12 155)` |
| `warning` | `oklch(0.64 0.17 78)` | `oklch(0.76 0.15 90)` |
| `anomaly` | `oklch(0.68 0.15 65)` | `oklch(0.78 0.13 75)` |
| `destructive` | `oklch(0.58 0.18 28)` | `oklch(0.72 0.14 28)` |
| `ring` | `oklch(0.48 0.12 238)` | `oklch(0.80 0.10 238)` |
| `chart-historical` | `oklch(0.50 0.025 245)` | `oklch(0.72 0.025 240)` |
| `chart-forecast` | `oklch(0.48 0.12 238)` | `oklch(0.72 0.12 238)` |
| `chart-interval` | `oklch(0.92 0.04 238)` | `oklch(0.32 0.07 238)` |
| `chart-anomaly` | `oklch(0.68 0.15 65)` | `oklch(0.78 0.13 75)` |
| `chart-grid` | `oklch(0.875 0.014 240)` | `oklch(0.40 0.025 245)` |

### Chart roles

| Token | Meaning | Shape/stroke partner |
|---|---|---|
| `chart-historical` | Monthly historical observations/reference | Neutral solid line |
| `chart-forecast` | Fixed-origin point forecast | Accent solid line |
| `chart-interval` | 90% prediction interval area/boundaries | Pale/accent band plus boundary or legend text |
| `chart-anomaly` | Anomaly method marks | Explicit method symbol and label |
| `chart-grid` | Grid/reference scaffolding | Subtle dashed or light rule |

Add `status-ready` and `status-unavailable` variables as semantic aliases of
the success/danger roles only if the status component needs separate theme
control. Do not collapse `anomaly` into `danger`, or model quality into
`success`.

### Tailwind v4/shadcn mapping

The implementation CSS layer should define the standard shadcn variables as
semantic values, with paired foreground variables:

```css
:root {
  --background: oklch(0.975 0.006 235);
  --foreground: oklch(0.245 0.025 245);
  --card: oklch(0.995 0.004 235); /* only for adopted bounded Card surfaces */
  --card-foreground: oklch(0.245 0.025 245);
  --popover: oklch(0.995 0.004 235); /* menus, sheets, and popovers only */
  --popover-foreground: oklch(0.245 0.025 245);
  --primary: oklch(0.48 0.12 238);
  --primary-foreground: oklch(0.99 0.005 235);
  --secondary: oklch(0.945 0.009 235);
  --secondary-foreground: oklch(0.245 0.025 245);
  --muted: oklch(0.945 0.009 235);
  --muted-foreground: oklch(0.50 0.025 245);
  --accent: oklch(0.92 0.04 238);
  --accent-foreground: oklch(0.245 0.025 245);
  --warning: oklch(0.64 0.17 78);
  --warning-foreground: oklch(0.245 0.025 245);
  --destructive: oklch(0.58 0.18 28);
  --destructive-foreground: oklch(0.99 0.005 235);
  --border: oklch(0.875 0.014 240);
  --input: oklch(0.875 0.014 240);
  --ring: oklch(0.48 0.12 238);
  --chart-historical: oklch(0.50 0.025 245);
  --chart-forecast: oklch(0.48 0.12 238);
  --chart-interval: oklch(0.92 0.04 238);
  --chart-anomaly: oklch(0.68 0.15 65);
  --chart-grid: oklch(0.875 0.014 240);
  --status-ready: oklch(0.58 0.12 155);
  --status-unavailable: oklch(0.58 0.18 28);
}
```

Tailwind v4 `@theme inline` maps these variables into utilities. Existing
`--color-canvas`, `--color-surface`, `--color-ink`, and related roles should be
temporarily retained as aliases during the implementation migration only if
that avoids a broad one-step rewrite; the final implementation must have one
canonical value per semantic role and no contradictory duplicate palette.

`DESIGN.md` names product concepts; CSS variables are the executable values;
Tailwind theme mappings are the utility interface. A token change must update
the CSS and the synchronized design contract in the same implementation PR.

## 11. Light/dark theme contract

Implement a small local theme provider with the contract below:

- Theme state is exactly `light`, `dark`, or `system`.
- Initial state follows the operating-system preference when no saved choice
  exists; the provider default is `system`.
- Persist only the selected theme string in `localStorage` under a product-
  namespaced key such as `co2-forecast-lab-theme`.
- Apply a `light` or `dark` class to `document.documentElement`; do not add a
  server dependency or a remote theme service.
- The bootstrap should set the class before the first meaningful paint where
  practical in Vite so a saved dark choice does not flash light. If the first
  implementation cannot eliminate every flash, document the measured behavior
  in the implementation PR rather than hiding it.
- `system` must respond to `prefers-color-scheme` changes while active.
- The theme control must expose Light, Dark, and System as named choices. A
  compact icon control may open a DropdownMenu, but it must have a visible or
  screen-reader name and must not be the only indication of the current choice.
- Storybook must expose light and dark review, with a theme control or explicit
  paired stories. The a11y addon must run in both themes for adopted states.
- Playwright must cover choosing each mode, persistence across reload, system
  initial behavior where controllable, focus visibility, and no document
  overflow at 390×844.
- Contrast review covers muted text, borders where they communicate structure,
  focus rings, status labels, chart labels, and both selected/final-test model
  markers. A dark theme is not accepted if it is merely an inversion.

## 12. AppShell v2

### Desktop

At `lg` and above, use a compact persistent left shell rather than a marketing
header: product identity, five primary destinations, a deliberate API/readiness
status area, and an optional theme control. The current 248px rail is a useful
starting measure but its final width must preserve the content column at 1440px.
The content region uses a readable max width and 24–32px desktop gutters.

The active destination has at least three cues chosen from shape/background,
text weight, icon treatment, and a small rule/indicator; color is not the sole
cue. Navigation uses `aria-current="page"`, buttons or links with accessible
names, and a single semantic `nav` landmark. Status text remains a live status,
but its dot is supplementary to words such as `API connected`, `API connecting`,
and `API unavailable`.

### Mobile and intermediate widths

Below the desktop shell breakpoint, use a compact header with product/page title,
status, theme control if it fits, and a named menu button. The menu opens a
left-side Base UI Sheet containing all five destinations. Selecting a page
closes the sheet and moves focus predictably to the page heading or menu trigger.
The Sheet includes an accessible title/description, close action, escape
handling, inert background, and visible focus.

Use the shadcn Sidebar only if its Base UI implementation can be composed into
this smaller shell without importing unused block behavior. The default choice
is a smaller custom `AppShell` built from Button, Sheet, and shared navigation
data, because the current product has five flat destinations, no nested groups,
no workspace switcher, and no need for a resizable rail. If an implementation
uses shadcn Sidebar, it must still omit the dashboard block and preserve this
five-item flat navigation contract.

Touch targets are at least 44×44 CSS pixels. The document must not overflow
horizontally. Charts may have an internal minimum width only when that produces
a clearly labeled local scroll region; tables use a local overflow wrapper with
the first meaningful column understandable. Do not force five navigation labels
into a horizontally scrolling header strip.

## 13. Primitive inventory (YAGNI)

The inventory is a usage decision, not a request to import every shadcn example.

### Required now

| Primitive | Use |
|---|---|
| Button | Navigation, retry, mobile menu, theme trigger, and explicit page actions with shared size/focus/disabled behavior |
| Badge | Compact `Selected by development`, `Lowest final-test MAE`, `Ready`, `Unavailable`, and method labels; always paired with text meaning |
| Alert | API unavailable/retry and bounded limitation callouts; not for anomaly counts |
| Select | Forecast horizon and any future bounded single-choice control where native select styling is insufficient; keep label/value semantics |
| Skeleton | Loading regions with `aria-busy`/status behavior and reduced-motion-safe presentation |
| Sheet | Mobile navigation drawer, with accessible dialog semantics and focus management |
| DropdownMenu | Three-choice theme menu if it is the smallest accessible control for Light/Dark/System |
| Table | Shared table structure/styles for forecast values, anomalies, and model comparison; preserve native semantics |

### Optional later

| Primitive | Gate before adoption |
|---|---|
| Tooltip | Only for non-critical supplemental icon/control explanation; never for methodology, status, or chart conclusions |
| Tabs | Only if a page gains a real mutually exclusive view set; current five-page navigation is not Tabs |
| Separator | Useful when a semantic divider is needed inside a region; current border/spacing rules may remain sufficient |
| Sidebar | Use only if the Base UI sidebar composition is measurably simpler than the smaller custom shell described above |
| Popover | Only for a real compact contextual inspector or filter with enough content to justify a portal |
| ScrollArea | Only if native local overflow is insufficient; do not replace simple table overflow with it by default |
| Switch | Only for a real two-state chart/view preference; theme is three-state and uses DropdownMenu/Select |
| Card | Only for a bounded interactive surface or a genuinely grouped, elevated overlay; not as the page default |
| Dialog | Only for a destructive/confirming action or a modal review workflow that cannot be inline |

### Not needed for the current v2

| Candidate | Reason |
|---|---|
| DataTable / TanStack Table | Current tables have small static evidence sets and require no sorting, filtering, pagination, selection, or column controls; native Table is more transparent |
| Generic dashboard block | It would import unneeded layout assumptions and weaken the product-specific evidence hierarchy |

Card is intentionally neither a default nor a ban: the panel policy below is
the stronger rule. A primitive is adopted only when it removes real repeated
behavior and has a current consumer.

## 14. Domain components and interfaces

The accepted domain modules below protect meaning, remove repeated page code,
and provide useful Storybook/test seams. They are not a mandatory one-component-
per-paragraph decomposition.

| Module | Purpose | Props/input contract | Semantic responsibility | Accessibility contract | Storybook states | Test responsibility |
|---|---|---|---|---|---|---|
| `HistoricalScope` | Explain packaged source, period, frequency, unit, and historical-only boundary | `dataset: DatasetMetadata`; optional compact/detail mode | Never imply current data; formats source scope consistently | Definition list with associated labels; no color-only historical marker | Full, compact, long metadata, missing optional values | Renders period/unit/source and historical-only wording; handles long wrapping |
| `DataProvenance` | Present dataset and causal preparation lineage | `dataset`, `preprocessing`, optional `splitBoundaries` | Keeps source module, row counts, imputation strategy, and feature cutoff together | Heading/region label; definition lists; readable hashes/identifiers | Full provenance, compact inset, API unavailable | No invented values; preserves source/preprocessing labels |
| `ReadinessStatus` | Show API connection/readiness state | `status: connected | connecting | unavailable`; optional detail | Distinguishes process/UI status from governed artifact claims | Live status text, not only a dot | `role=status`, polite updates, icon hidden from AT, explicit unavailable wording |
| `LimitationCallout` | Place a bounded caveat next to the claim it constrains | `title`, `children`, `tone: neutral | warning`, optional `icon` | Keeps interval, historical-only, anomaly, or final-test boundaries visible | Default, long copy, dark, narrow width | `role=note` or `alert` by tone; no emergency language; keyboard-visible links/actions |
| `MetricDefinition` | Render one reviewer-critical number with denominator/protocol context | `label`, `value`, optional `detail`, optional `unit`, optional `emphasis` | Prevents bare ppm/MAE/coverage numbers from losing context | Uses `dt/dd` or labeled region; tabular numerals; no status by color alone | Selected model, coverage, count, unavailable | Exact value/detail and optional em dash behavior; no generic “best” label |
| `ModelSelectionSummary` | Make development selection and final-test result impossible to conflate | `selectedModel`, development metric/fold context, `finalTestWinner`, final-test metric, `rationale` | Explicitly labels SARIMA development-selected and Exponential Smoothing final-test winner when data says so | Separate headings/regions, text labels, table relationship, optional icon supplement | Normal governed fixture, unavailable, long model name | Asserts both labels remain separate and final test cannot overwrite selection |
| `ModelComparison` | Provide a table wrapper with protocol and status columns | `selectedModel`, `models`, `selectionContext`, `evaluationContext` | Orders/renders final-test comparison while retaining development selection label | Native table headers/scope/caption; right numeric alignment; local overflow | All candidates, selected winner differs, null metric | Rows, labels, null formatting, semantic table, no “Best MAE” shorthand |
| `ForecastEvidence` | Compose forecast chart context, origin, model/protocol, and nearby limitation | `historical`, `forecast`, `metadata`, `horizon`, `onHorizonChange` | Distinguishes fixed-origin projection from rolling one-step evaluation | Region heading, labeled control, chart text alternative, limitation adjacent | 6/24/60 months, loading, error, dark, narrow | Origin/protocol/interval copy and control retry/loading behavior |
| `ForecastIntervalLegend` | Explain historical, forecast, interval, origin, and coverage scope | `nominalCoverage`, `coverageScope`, optional series visibility | Uses “prediction interval,” never “confidence interval”; explains one-step boundary | Text labels plus line/fill/marker samples; not color-only | Normal, long limitation, mobile stacked | Exact terminology, visible labels, no blanket multi-horizon claim |
| `AnomalyEvidence` | Compose method counts, timeline/table context, and caveat | `anomalies`, `historical` | Distinguishes Isolation Forest, residual threshold, agreement/disagreement; keeps 8/0 exploratory semantics | Legend names symbols; table alternative; no alert role for statistical signal | 8 IF/0 residual, agreement fixture, empty, dark | Counts and method labels match input; no event/incidence language |

Every module above accepts already-loaded data and emits no network or file
side-effect. Page modules remain responsible for choosing which evidence is
primary; domain modules are responsible for rendering that evidence faithfully.

## 15. Page-by-page v2 design

All pages use the same `PageHeader` pattern: plain-language page question,
one-sentence methodological context, and an optional control aligned to the
right on desktop and stacked on mobile. No page receives a giant hero or a
generic KPI wall.

### Overview

- **Primary evidence:** a compact scope/selection summary followed by one
  historical time-series region. The selected model, development rationale,
  final-test distinction, measured one-step interval coverage, and historical
  boundary are visible before or immediately beside the chart.
- **Secondary evidence:** a deliberate two-column evidence row: `ModelSelectionSummary`
  and `LimitationCallout`/interval boundary. The final-test comparison remains
  a full-width native table below, not a wall of seven cards.
- **Supporting details:** `HistoricalScope`, provenance, latest historical
  value, and a small group of reviewer-critical metrics.
- **Limitation placement:** historical-only copy is in the page header/scope;
  selection and final-test limitations are adjacent to their summary; interval
  and anomaly limitations appear beside those claims.
- The historical chart title states monthly month-end means and `ppm`; data
  remains ordered and the chart has a nearby textual alternative.

### Data Explorer

- **Primary evidence:** provenance/preparation region, with source module,
  packaged period, frequency, unit, observed/missing counts, monthly rows, and
  causal imputation/feature lineage.
- **Secondary evidence:** the full-width historical time series with month-end
  means and trailing 12-month mean.
- **Supporting details:** compact metrics for row count and observed range;
  metadata uses definition lists and wraps long values.
- **Table contract:** if a dense monthly table is shown or expanded in a later
  implementation, use 12–14px body text, tabular numeric values, sticky header
  only inside a bounded local scroller, and keep the date column visible or
  understandable. Do not add filtering/pagination absent a real need.
- **Mobile:** chart keeps a meaningful minimum height; any wide table scrolls
  inside its region and never expands document width.

### Forecasting

- **Primary evidence:** `ForecastEvidence` with historical line, forecast line,
  forecast-origin boundary, 90% prediction interval band/boundaries, and the
  selected horizon control.
- **Chart anatomy:** title and short context; y-axis `ppm`; x-axis month-end
  dates; consistent legend; exact tooltip date/value/series/protocol; vertical
  origin annotation; interval band; immediately adjacent coverage limitation.
- **Supporting details:** model/version, origin, horizon, frequency, and
  interval method in a compact evidence group; exact values in a bounded table.
- **Limitation placement:** state that measured coverage belongs to documented
  rolling one-step final-test forecasts and that the fixed-origin multi-step
  projection reuses a development-derived radius without separately established
  multi-horizon coverage. Never use “confidence interval.”
- Horizon changes remain bounded to the existing 1–60 API behavior. Loading,
  error, and retry state keep the current semantics.

### Anomaly Detection

- **Primary evidence:** timeline plus `AnomalyEvidence` and its explicit inline signal legend
  showing Isolation Forest and residual-threshold marks with distinct shape or
  stroke, method names, and agreement/disagreement text.
- **Supporting evidence:** current governed counts remain visible as `8`
  Isolation Forest, `0` residual-threshold, and `0` agreements when the API
  returns those values; flagged-month table remains the accessible detail view.
- **Language:** use “exploratory statistical signal,” “Isolation Forest,”
  “residual threshold,” “agreement,” and “disagreement.” Do not use incident,
  alert, emergency, verified climate event, or causality language.
- **Color:** anomaly amber is a method signal token only. Marker shape, border,
  method text, and table labels carry the distinction.

### Model Evaluation

- **Primary evidence:** a two-column selection/evaluation summary with strong
  headings exactly separating `Selected by development` from `Lowest final-test
  MAE`. The selected-model region must explicitly say `SARIMA` when governed
  data says so; the final-test region must explicitly say `Exponential Smoothing`
  when it has the lower final-test MAE.
- **Required annotation:** “The final test evaluates after selection; it does
  not choose or replace the serving model.” Keep this copy near both the summary
  and table.
- **Secondary evidence:** comparison table with separate status column and
  protocol caption. Never use a single generic “best model” label.
- **Supporting details:** residual timeline and error-distribution images can
  remain bounded evidence regions with meaningful alt text and no false chart
  interactivity.
- **Responsive:** comparison table scrolls locally; summary stacks at narrow
  widths; no color-only selected row.

## 16. Chart and data-visualization grammar

Keep Recharts and expose its composition through thin repository-owned wrappers.
The official shadcn chart guidance is useful because it keeps Recharts directly
composable, supports a shared chart configuration, supports CSS/OKLCH variables,
and provides an `accessibilityLayer` option. Use those ideas without adopting a
chart abstraction that hides the data semantics.

### Shared grammar

| Evidence | Visual treatment | Text/semantic treatment |
|---|---|---|
| Historical observation | `chart-historical`, neutral solid stroke, no decorative fill | “Historical observations” and `ppm` unit |
| Forecast point estimate | `chart-forecast`, accent solid stroke, slightly stronger weight | “Fixed-origin forecast,” model, origin, protocol |
| 90% prediction interval | `chart-interval` low-opacity band plus boundary/legend label; never a confidence interval | “90% prediction interval”; one-step measured coverage limitation nearby |
| Forecast origin | Vertical rule/dashed marker with a readable label | `Forecast origin` and exact date |
| Isolation Forest signal | Filled, distinct symbol such as circle/triangle and method label | `Isolation Forest signal`, exploratory boundary |
| Residual signal | Outlined, distinct symbol such as diamond/ring and method label | `Residual-threshold signal` |
| Agreement/disagreement | Overlaid or paired marker plus explicit text/table method details | “Agreement,” “Isolation Forest only,” or “Residual threshold only” |
| Selected model | Text badge/label and optional check icon | `Selected by development` |
| Final-test comparison | Neutral table/marks with explicit status label | `Lowest final-test MAE`; evaluation only |
| Grid | `chart-grid`, subtle and secondary | Never compete with data |

All charts include a descriptive qualitative title, a readable unit, date
formatting that reflects monthly data, consistent minimum height (at least
`min-h-[320px]` desktop and `min-h-[280px]` mobile unless a documented surface
needs more), and responsive measurement. A line chart may use a non-zero y-axis
domain to show a trend, but the axis and context must make that choice clear;
comparison bars/areas must not exaggerate relative differences.

Tooltip content is structured as date/period, series name, exact value/unit,
and relevant model/protocol/method context. It is supplemental, not the only
access path. Every chart has a nearby concise textual conclusion and, where the
conclusion depends on individual rows, a semantic table or equivalent text
alternative. Use `accessibilityLayer` where the Recharts version supports it
without changing the current data behavior; test keyboard access rather than
claiming the library made the domain chart accessible automatically.

Legends use the same relative position across related charts, may stack on
mobile, and use clear full names rather than unexplained acronyms. Direct labels
are preferred when the number of series and available space make them clearer.
Do not hide a required legend without a visible “View legend” action and an
accessible equivalent.

## 17. Typography and density

Retain `Inter, "Segoe UI", system-ui, sans-serif` as the system-first stack and
do not add a web font. The implementation should express these roles through
shared classes or component variants rather than repeating arbitrary utilities:

| Role | Direction |
|---|---|
| Page title | Responsive 28–36px, semibold, compact tracking; no marketing hero treatment |
| Section title | 18–22px, semibold; question/evidence oriented |
| Body | 14–16px, line-height about 1.55 |
| Metadata | 12–14px, muted but contrast-checked; not below 12px for required information |
| Table | 12–14px, left labels/right numeric values, tabular numerals |
| Metric | 24–32px where reviewer-critical, with unit and denominator/context |
| Technical identifier | System monospace only for hashes, paths, versions, or compact machine output |

Use tabular numerals for ppm, MAE/RMSE, coverage, counts, and dates when
comparison benefits. Use sentence case for page headings and controls. The
overall feel is compact, precise, technical, calm, and credible—not luxury SaaS,
marketing landing page, or generic AI dashboard.

## 18. Panel/card policy

- A **section** groups a page question and its evidence. It needs hierarchy and
  spacing, not necessarily a border.
- A **panel** represents one meaningful evidence group, such as provenance,
  forecast evidence, or model-selection summary. Use `surface`, one `border`,
  restrained radius, and no shadow by default.
- An **inset evidence region** groups a related table, legend, annotation, or
  definition list inside a panel when the relationship needs a quiet visual
  boundary. Prefer a separator or background shift before adding another box.
- A **metric** is a labeled value with unit/denominator/protocol context. A few
  reviewer-critical metrics may share one evidence region.
- A **callout** is for a claim boundary, limitation, unavailable state, or
  actionable retry. Use semantic text and an appropriate `role`.
- A **Card** is reserved for a bounded interactive or overlay surface whose
  independent container is meaningful. It is not the default page primitive.
- Paragraphs alone do not need cards. Do not convert every existing border row,
  chart, metric, or table into a generic Card.
- One panel should answer one meaningful evidence question. If the only reason
  to add a container is visual variety, use spacing or a separator instead.

## 19. Accessibility contract

The implementation must preserve and strengthen:

- semantic `header`, `nav`, `main`, `section`, `figure`, `table`, `caption`,
  `th scope`, and definition-list structure;
- one clear page heading and a named heading relationship for each evidence
  region;
- `aria-current="page"` on the active destination;
- `role=status` for connection/loading updates and `role=alert` for actionable
  API failure, without turning anomaly signals into alerts;
- visible `:focus-visible` using the `ring` token, never an outline removed for
  aesthetics;
- accessible names for menu/theme/horizon controls and meaningful icon hiding;
- 44px minimum touch targets on mobile;
- keyboard navigation and focus return for Sheet, DropdownMenu, Select, and
  any future Tooltip-triggered action;
- text, labels, icon/shape/stroke, and table semantics in addition to color;
- reduced-motion behavior for skeletons and transitions;
- chart titles, units, origin/protocol/interval text, `accessibilityLayer` where
  supported, and a nearby text/table alternative;
- readable zoom/reflow at 390×844 and intermediate widths.

Base UI/shadcn primitives reduce custom burden for focus management, portals,
keyboard handling, and modal inertness. They do not know the difference between
a fixed-origin forecast and a rolling one-step evaluation, nor whether an amber
mark is exploratory. Domain modules own those responsibilities and must be
tested through their interfaces.

## 20. Responsive contract

Verify at 1440×900 desktop and 390×844 mobile, plus an intermediate tablet-like
width around 768px. The exact future Playwright viewport fixtures remain the
current named targets.

- Desktop: persistent compact rail, content max width, 24–32px gutters, and
  two-column evidence only where both columns remain readable.
- Tablet: rail may collapse to an icon/compact mode or transition to the mobile
  menu at a documented breakpoint; no squeezed labels.
- Mobile: compact header and Sheet nav; page gutters around 16px; single-column
  evidence by default; metrics stack or form a readable two-column group only
  when labels remain clear.
- Charts: retain minimum height and readable axis/legend spacing. If an internal
  scroll region is necessary, its affordance and scope are visible.
- Tables: local horizontal overflow, sticky header only inside the local region,
  right-aligned tabular numerics, and no document-level overflow.
- Long provenance/model/limitation text wraps rather than clipping; technical
  identifiers may break at safe boundaries or use a bounded scroll treatment.
- The layout must not shrink type, chart height, or touch targets until the
  evidence becomes illegible.

## 21. Storybook v2 strategy

Use a small intentional catalog, not hundreds of generated stories:

```text
Foundations/
  Colors
  Typography
  Spacing
  Theme
Primitives/
  Button
  Badge
  Alert
  Select
  Skeleton
  Sheet
  DropdownMenu
  Table
Layout/
  AppShell
  PageHeader
Domain/
  HistoricalScope
  DataProvenance
  ReadinessStatus
  LimitationCallout
  MetricDefinition
  ModelSelectionSummary
  ModelComparison
  ForecastEvidence
  ForecastIntervalLegend
  AnomalyEvidence
Charts/
  TimeSeries
  Forecast
  Anomaly
  ModelComparison
States/
  Loading
  Empty
  APIUnavailable
  Retry
  HistoricalOnlyLimitation
```

Only adopted primitives receive stories. Required controls expose relevant
variants and keyboard interaction. Domain stories use governed fixtures and
include normal, long-copy, empty/unavailable, selected-vs-final-test, 8/0
anomaly, dark, and narrow states where relevant. Chart stories show legend,
tooltip, origin, interval, and text-alternative context; they must not assert
that a screenshot alone proves accessibility. The a11y addon remains configured
to fail on violations, and Storybook’s Vitest browser project exercises the
stories in both themes where practical.

## 22. Test strategy

This stage adds no tests. The implementation must extend the existing test
surface in proportion to the new behavior:

1. **Unit/component:** test each adopted domain module through its public
   interface. Cover metric context, model-selection separation, anomaly counts,
   interval wording, status roles, empty/error/retry, and theme provider state.
2. **Interaction:** use Testing Library/user-event for mobile Sheet open/close,
   focus return, navigation, theme choice/persistence, Select horizon changes,
   retry, and keyboard focus.
3. **Storybook browser/a11y:** run `build-storybook` and the existing official
   Vitest browser project; review light/dark and narrow stories.
4. **Application E2E:** preserve real API-backed positive paths across all five
   destinations. Keep request routing only for the deterministic failure path.
   Assert heading hierarchy, `aria-current`, non-color labels, no page overflow,
   forecast limitation language, anomaly caveat, and model-selection distinction.
5. **Visual:** refresh only the approved canonical Linux/Chromium regions after
   implementation, with animations disabled and generated timestamps outside
   the clip.
6. **Gates:** retain the repository’s format/lint/typecheck/unit/integration/
   Storybook/E2E/a11y/security gate order applicable to the frontend. A design
   change does not justify weakening CI or the baseline verifier.

## 23. Visual-regression migration plan

The current four committed baselines under
`frontend/e2e/snapshots/visual.spec.ts-snapshots/` are canonical Linux/Chromium
regions:

1. `overview-evidence-desktop-linux.png`
2. `model-evaluation-selection-desktop-linux.png`
3. `forecast-evidence-desktop-linux.png`
4. `overview-mobile-shell-mobile-linux.png`

The redesign is expected to invalidate at least some of these images. The
implementation PR must:

- run visual updates only in the canonical GitHub Actions Linux/Chromium
  environment described in `docs/verification.md`, not native Windows;
- review each changed image as a diff against the intended v2 hierarchy;
- keep the final set to the four regions above unless a reviewer-critical
  surface is demonstrably missing;
- preserve region names and platform suffix conventions where practical;
- keep generated timestamps, transient API state, and caret/animation noise out
  of clips;
- never commit Windows snapshots;
- never let final CI use `--update-snapshots`;
- never add broad masks or a large tolerance to force green;
- run `npm run test:e2e:verify-baselines` and the full E2E suite after refresh.

The recommended v2 regions are still exactly: Overview evidence hierarchy;
Model Evaluation selection-versus-final-test distinction; Forecast evidence with
interval/origin grammar; and mobile AppShell/Overview. Data Explorer and Anomaly
Detection remain covered by semantic E2E and Storybook unless a later reviewer
identifies a visual regression that those four regions cannot catch.

## 24. Dependency-impact plan

No dependency changes occur in Stage A. The implementation must verify the
actual generated dependency graph before editing the lockfile.

| Package or artifact | Why | Direct/transitive | Alternative | Required? | Security/maintenance consideration |
|---|---|---|---|---|---|
| `shadcn` CLI/config | Generate/adapt source-owned primitives and record aliases/base/style | Development tool/config; not a page runtime feature | Manual copy of official component source | Required only for the chosen generation workflow; not required to run the built app | Pin/review CLI changes; do not run blindly over dirty files; inspect generated diff |
| `@base-ui/react` | Base UI runtime primitives used by generated/adapted components | Direct runtime dependency if selected components import it | Radix remains supported, but switching is a deliberate exception | Required for adopted Base UI components; exact version must be resolved by the implementation lockfile | Single tree-shakable package; audit and pin through normal npm lockfile review |
| `class-variance-authority` | Variant contracts for generated/adapted Button/Badge/etc. if emitted | Direct runtime utility if generated source imports it | Small local variant helper, but duplication is undesirable | Required only if generated source uses it | Small focused dependency; no second variant system |
| `clsx` | Conditional class composition if generated source uses it | Direct runtime utility | Existing string composition, but brittle for variants | Required only if generated source uses it | Keep one helper path |
| `tailwind-merge` | Resolve conflicting Tailwind utilities in `cn` helper if generated source uses it | Direct runtime utility | Avoid if no class merging is needed | Required only if generated source uses it | Review version and behavior with Tailwind v4 |
| `tw-animate-css` | Official shadcn animation utilities if adopted components require them | Direct CSS dependency if generated source imports it | Minimal local transitions | Required only if emitted source uses it | Keep reduced-motion override; do not add animation for decoration |
| `lucide-react` | Existing icon stack and shadcn icon configuration | Already direct | No new icon library | **No new package; preserve existing** | Avoid duplicate icon sets and extra maintenance |
| `recharts` | Existing chart renderer and shadcn chart composition | Already direct | Carbon Charts or another renderer | **No new package; preserve existing** | Keep current version and test Recharts v3 behavior |
| TanStack Table | Sorting/filtering/pagination/column controls | Would be direct | Native table | **No** for current UX | Avoid complexity, bundle, and new accessibility surface without a real requirement |
| Carbon React/Charts | Full Carbon migration | Would be direct | Selected Carbon guidance only | **No** | Avoid duplicate design system and chart library |

The implementation PR must record exact resolved versions in its normal
dependency diff and run `npm audit --audit-level=high`. It must not add both
Radix and Base UI for the same adopted primitive, and it must not add a theme
library when the small local provider satisfies the contract.

## 25. Implementation slices and dependencies

No slice is implemented by this Stage A task.

1. **Foundation and inventory lock.** Confirm generated Base UI package output,
   add `components.json`/aliases only after review, create the `cn` seam if
   needed, define standard/domain CSS variables, and add Button, Badge, Alert,
   Select, Skeleton, Table, and Sheet source. Depends on this
   spec and a clean post-merge main; blocks every later slice.
2. **Theme and shell.** Implement Light/Dark/System persistence, intentional
   light/dark tokens, compact desktop rail, mobile Sheet navigation, status,
   and `PageHeader`. Preserve five page IDs and `App.tsx` loading/page seams.
   Depends on Slice 1.
3. **Domain/evidence modules.** Implement provenance/scope/status/limitation/
   metric and model-selection/comparison modules, then chart config, shared
   tooltip/legend context, forecast interval/origin, and anomaly grammar.
   Depends on tokens/primitives; must be tested with governed fixtures.
4. **Page migration.** Migrate Overview, Data Explorer, Forecasting, Anomaly
   Detection, and Model Evaluation in vertical page slices, preserving API
   types, current values, loading/error/retry, and wording invariants. Depends
   on Slices 2–3; use one reviewable commit/PR slice per page where practical.
5. **Storybook and test hardening.** Reorganize the catalog, add domain/state/
   theme stories, component interaction tests, a11y coverage, and updated
   semantic E2E assertions. Depends on each migrated module being stable.
6. **Canonical visual refresh and verification.** Run full frontend gates,
   review the four canonical regions in Linux/Chromium, update only intended
   baselines, verify committed baselines, then run the full repository gates.
   Depends on all prior slices and reviewer acceptance of the visual diff.

Each slice must leave the application buildable and the current API-backed
positive path runnable. A failing slice is fixed or reverted before starting the
next; no slice changes #26 deployment configuration.

## 26. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Generated shadcn source brings unexpected packages or API shape | Generate in an isolated implementation slice, inspect exact diff/lockfile, use only adopted primitives, and audit before merging |
| Base UI API changes current event/render patterns | Keep generated source local, pin the lockfile, test interactions in jsdom/Storybook/browser, and do not mix Radix/Base UI for one primitive |
| Dark theme reduces contrast or changes chart meaning | Use paired semantic tokens, contrast-test both themes, and story every domain state in both themes |
| Shell migration breaks keyboard/mobile navigation | Preserve five-item navigation data, add tests for `aria-current`, focus return, Sheet escape, 44px targets, and page overflow |
| Generic Card usage recreates dashboard clutter | Enforce panel/card policy in review and prefer sections/evidence regions |
| Chart wrapper hides or changes protocol semantics | Keep direct Recharts composition and test titles, labels, origin, interval wording, and text alternatives |
| Visual baseline churn masks a real regression | Keep four focused clips, canonical Linux only, no masks/tolerance inflation, and review the image diff semantically |
| A11y primitives give false confidence for domain evidence | Test domain interfaces, table alternatives, non-color markers, and chart text separately |
| CSS token duplication causes theme drift | Maintain one canonical CSS variable value and synchronize `DESIGN.md` in the implementation PR |
| Scope expands into deployment or backend work | Keep #26 handoff informational; classify any API need as out of scope and stop for a separate issue |

## 27. Rollback strategy

Rollback is slice-oriented and reversible:

1. Revert the implementation slice or PR that introduced the regression; do not
   reset unrelated user work or rewrite history.
2. Because the API types, page data seams, and governed artifacts remain
   unchanged, restoring the prior frontend source restores the previous runtime
   contract.
3. If a primitive is faulty, remove its consumers and generated source in the
   same slice, restore the previous native control/table/chart wrapper, and
   remove only dependency entries proven to be owned by that slice.
4. If the visual refresh is wrong, restore the prior four canonical images from
   the parent commit or revert the visual slice; do not mask or retune snapshots.
5. If only the theme is faulty, set the provider back to the system/light
   behavior and restore the preceding CSS token values; local storage should be
   ignored safely when it contains an unknown value.
6. Re-run the affected component, Storybook/a11y, E2E, baseline-verifier, and
   repository CI checks before declaring rollback complete.

No rollback plan permits deleting or regenerating governed model/evidence
artifacts, changing backend contracts, disabling required CI, or deploying.

## 28. Acceptance criteria

The Stage A specification is accepted when:

- this document is the only intended file changed by the Stage A PR;
- the current frontend stack and all five page seams are accurately audited;
- options A/B/C are compared and Option A is justified with current official
  shadcn/Base UI evidence;
- required/optional/not-needed primitive decisions are explicit, including
  Card and DataTable/TanStack Table;
- each accepted domain module has purpose, input, semantic responsibility,
  accessibility, Storybook, and test contracts;
- the token mapping includes standard shadcn variables plus domain chart/status
  variables, light/dark direction, OKLCH compatibility, and prohibited styles;
- the theme contract specifies system initial behavior, Light/Dark/System,
  local persistence, class application, FOUC handling, Storybook, Playwright,
  and contrast review;
- AppShell desktop/mobile behavior, primitive choice, active-state semantics,
  touch targets, and overflow contracts are implementation-ready;
- all five pages have primary/secondary/supporting/limitation hierarchy and
  preserve exact model, interval, and anomaly meanings;
- chart grammar, tooltip/legend/annotation, units, minimum height, responsive
  behavior, and non-color meaning are concrete;
- Storybook taxonomy, test strategy, and four-surface canonical Linux baseline
  migration are explicit;
- implementation slices have dependencies, risk/rollback boundaries, and no
  slice starts in this Stage A task;
- deployment handoff to #26 is limited to future static/theme/API-base
  considerations and contains no deployment implementation;
- a fresh review finds no unresolved implementation placeholder or deferred-
  design language, unresolved product/architecture question, scope creep, or
  contradiction.

The subsequent implementation issue is accepted only when it also passes the
repository’s frontend gates, real browser desktop/mobile review, accessibility
checks, semantic E2E checks, canonical Linux visual review, and post-merge main
CI. Design approval is not implementation approval.

## 29. Deployment handoff to #26

Issue #26 owns hosting/deployment. The later deployment work may rely on this
spec’s following constraints:

- the theme provider is client-local and works in a static Vite build;
- no v2 design behavior requires server-side rendering;
- a future `VITE_API_URL` remains the only frontend API-base configuration seam;
- static asset paths and residual plot images remain compatible with the chosen
  hosting mode;
- production CORS, API hosting, readiness, monitoring, and live URL claims are
  separately verified in #26.

This Stage A task does not configure Vercel/Netlify/Render, alter CORS, set a
live API URL, edit README deployment claims, or change GitHub project metadata.

## 30. Explicit unresolved questions

NONE. The implementation PR may verify exact generated package versions and
choose the smaller of two equivalent file splits, but those are execution
checks within the decisions above, not open product or architecture questions.
