---
version: "1.0"
name: "CO2 Forecast Lab"
description: "A calm scientific data workbench for inspecting historical CO2 evidence, model evaluation, forecasts, uncertainty, and exploratory anomaly signals."
product_archetype: "scientific analytics dashboard"
colors:
  canvas: "oklch(0.975 0.006 235)"
  surface: "oklch(0.995 0.004 235)"
  surfaceMuted: "oklch(0.945 0.009 235)"
  ink: "oklch(0.245 0.025 245)"
  inkMuted: "oklch(0.500 0.025 245)"
  rule: "oklch(0.875 0.014 240)"
  accent: "oklch(0.480 0.120 238)"
  accentSoft: "oklch(0.920 0.040 238)"
  anomaly: "oklch(0.680 0.150 65)"
  success: "oklch(0.580 0.120 155)"
  danger: "oklch(0.580 0.180 28)"
typography:
  family: "Inter, Segoe UI, system-ui, sans-serif"
  display:
    weight: 650
    tracking: "-0.025em"
  heading:
    weight: 650
    tracking: "-0.015em"
  body:
    weight: 400
    lineHeight: 1.55
  data:
    fontVariantNumeric: "tabular-nums"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  base: "16px"
  lg: "24px"
  xl: "32px"
  section: "48px"
radius:
  sm: "6px"
  md: "8px"
  lg: "12px"
elevation:
  default: "1px border using colors.rule; no shadow"
  floating: "subtle shadow only for temporary overlays/tooltips"
layout:
  contentMax: "1440px"
  pageGutterDesktop: "32px"
  pageGutterMobile: "16px"
  gridColumnsDesktop: 12
  minimumTouchTarget: "44px"
components:
  panel:
    background: "{colors.surface}"
    border: "1px solid {colors.rule}"
    radius: "{radius.lg}"
  metricCard:
    background: "{colors.surface}"
    border: "1px solid {colors.rule}"
    radius: "{radius.lg}"
  primaryAction:
    background: "{colors.accent}"
    foreground: "white"
    radius: "{radius.md}"
  statusChip:
    radius: "999px"
charts:
  historical: "{colors.inkMuted}"
  forecast: "{colors.accent}"
  interval: "{colors.accentSoft}"
  anomaly: "{colors.anomaly}"
  grid: "{colors.rule}"
---

# Overview

CO2 Forecast Lab should read as a **scientific/data workbench**, not a growth-marketing dashboard. The visual hierarchy exists to help a technical reviewer inspect evidence, compare models, understand uncertainty, and see limitations quickly.

The design should feel calm, precise, credible, and information-dense without becoming cramped. Decorative choices must never compete with the data.

## Design principles

1. **Evidence first.** The most important visual object on a page is the evidence needed to answer the page's question.
2. **One strong accent.** Blue is the primary interactive/forecast accent. Other semantic colors are reserved for explicit meaning.
3. **Thin structural depth.** Prefer borders, spacing, and grouping over heavy shadows, glass effects, or floating cards.
4. **Numbers are first-class content.** Use tabular numerals for metrics, dates, ppm values, errors, coverage, and sample counts.
5. **Uncertainty is visible.** Forecast intervals and methodological limitations belong near the forecast, not in hidden footnotes.
6. **Signal is not truth.** Anomaly styling must communicate method output without implying verified incidents.
7. **Accessible by more than color.** Shape, label, stroke pattern, icon, and text must carry meaning alongside color.
8. **Responsive by reflow, not shrink.** On narrow screens, stack information and enable safe table scrolling instead of compressing charts/text until unreadable.

## Visual direction

Use the restraint of modern data-team tools as inspiration: compact navigation, strong table/chart legibility, neutral surfaces, low visual noise, and clear information hierarchy. Do **not** copy another product's brand, exact layout, or marketing aesthetics.

Avoid the common AI-generated dashboard look: oversized gradient hero areas, excessive pill badges, glowing cards, decorative blobs, arbitrary purple/blue gradients, and every metric enclosed in its own elevated box.

## Colors

The existing Tailwind/CSS theme in `frontend/src/index.css` is the source implementation of the tokens above. When this file and CSS disagree, update both in the same change and explain why.

### Semantic roles

- `canvas` — application background.
- `surface` — primary panels and table/chart containers.
- `surfaceMuted` — secondary regions, skeletons, quiet grouping.
- `ink` — primary text/axes.
- `inkMuted` — secondary labels and historical/reference series.
- `rule` — separators, chart grids, panel borders.
- `accent` — primary action, selected navigation, forecast line, focus treatment.
- `accentSoft` — selected/hover backgrounds and forecast interval fill.
- `anomaly` — anomaly-method marks only; pair with explicit labels/symbols.
- `success` — validated/ready/pass states only.
- `danger` — real failures/errors only, not statistical anomaly signals.

Never encode model quality, anomaly membership, readiness, or pass/fail using color alone.

## Typography

Use the existing system-first Inter stack. Do not add a web-font dependency solely for visual novelty.

- Page title: 28–36px responsive, weight 650, compact tracking.
- Section heading: 18–22px, weight 650.
- Body: 14–16px, line-height around 1.55.
- Table/axis metadata: 12–14px, never below 12px for required information.
- KPI/metric value: 24–32px, tabular numerals, concise unit immediately adjacent.
- Technical identifiers, hashes, paths, and compact machine output may use the repository's monospace/system monospace style when needed.

Use sentence case for titles and controls. Avoid all-caps except very short technical labels where established.

## Layout

### App shell

Desktop:

- Persistent navigation may occupy a compact left rail/sidebar.
- Main content uses a maximum readable width around 1440px.
- Keep 24–32px page gutters and approximately 48px between major sections.
- Use a 12-column grid conceptually; dashboard content may compose as 4/8, 6/6, 3/9, or full-width regions.

Mobile/tablet:

- Navigation must collapse without removing destinations.
- Main content becomes one column by default.
- Charts should retain meaningful minimum height and horizontal room for axes.
- Wide comparison tables may scroll horizontally with the first meaningful column remaining understandable.

### Density

Prefer fewer, larger evidence regions over many tiny cards. A page should normally contain:

1. question/title + short methodological context;
2. one primary evidence visualization/table;
3. supporting metrics/details;
4. limitations/provenance near the evidence.

## Charts and data visualization

Charts are scientific communication surfaces, not decoration.

### Required chart behavior

- Label CO₂ units (`ppm`) wherever values could be ambiguous.
- Dates must preserve temporal ordering and readable intervals.
- Tooltips should show exact date/value and relevant series/protocol.
- Forecast plots must visually distinguish historical observations, forecast point estimates, and prediction interval.
- Model-comparison charts/tables must identify the **selected-by-development** model without implying the final-test winner selected it.
- Anomaly plots must distinguish each method and disagreement/overlap without relying on color alone.
- Avoid truncated axes when that would exaggerate differences; if a non-zero baseline is analytically useful, make the scale obvious.
- Avoid 3D, gauges, donut charts for scalar metrics, decorative area fills, and dual axes unless there is a documented analytical reason.
- Keep chart grid lines subtle and secondary to the series.

### Forecast visual grammar

- Historical observation: neutral/ink-muted solid line.
- Forecast: accent solid line with explicit `Forecast` label.
- 90% interval: accent-soft fill/band plus boundary/legend text; never call it a confidence interval.
- Historical/forecast boundary: visible origin marker or annotation.
- Nearby copy should state that measured coverage is established for the documented one-step evaluation scope, not all multi-step horizons.

### Anomaly visual grammar

- Treat `anomaly` as a method signal color, not an emergency color.
- Use different symbols/strokes for Isolation Forest vs residual-threshold outputs.
- Show agreement/disagreement explicitly in legend/text.
- Pair the visualization with a short boundary: exploratory signal, not verified climate event.

## Components

### Panel

Use for a coherent evidence region. Default to `surface`, 1px `rule` border, `lg` radius, and no shadow. A panel needs a reason to exist; do not wrap every paragraph in one.

### Metric card

Use only for a small number of reviewer-critical metrics such as selected model, final-test MAE, measured interval coverage, or sample counts. Include context/denominator when the number is otherwise easy to misread.

### Table

- Left-align labels; right-align numeric columns.
- Use tabular numerals.
- Keep units in headers where possible.
- Provide visible hover/focus only if rows are interactive.
- Mark the selected model with text/icon + semantic label, not background color alone.
- Preserve headers during horizontal scrolling where practical.

### Status chip

Use sparingly for states such as `Ready`, `Unavailable`, `Selected`, or method labels. Chips are not decoration and should not replace explanatory text.

### Error/loading/empty states

Every data-dependent region must have a designed state for loading, empty, API unavailable, and recoverable error where relevant. Error copy should say what failed and what the reviewer can do next.

## Navigation and interaction

- Active navigation is indicated by more than color: shape/background + text weight/indicator.
- All interactive elements need visible keyboard focus.
- Minimum target size is 44px for primary interactive controls on touch layouts.
- Do not hide critical methodology behind hover-only UI.
- Respect `prefers-reduced-motion`; motion is optional and should never be required to understand state.
- Transitions, if present, should be short and functional. No continuous decorative animation.

## Accessibility

Target WCAG AA behavior for text/controls where practical.

- Keyboard access is required for navigation and controls.
- Use semantic HTML before ARIA.
- Provide meaningful accessible names for chart containers/controls and concise text/table alternatives for critical chart conclusions.
- Never use color as the sole information channel.
- Maintain visible focus.
- Preserve readable zoom/reflow at common mobile widths.
- If a chart library renders inaccessible SVG/canvas detail, provide nearby textual evidence and tabular data for the core conclusion.

## Page intent

### Overview

Answer: **What is this system and what evidence should I trust first?**

Prioritize selected model, governed split/protocol, final-test performance, measured interval coverage, data period/boundary, and one primary historical/forecast view. Keep limitations visible.

### Data Explorer

Answer: **What historical data entered the system and how was it prepared?**

Show temporal coverage, missing/imputation lineage, historical values, and transformations without suggesting live/current data.

### Forecasting

Answer: **What does the selected historical model project from the fixed origin, and what uncertainty is actually supported?**

Make forecast origin, horizon, interval semantics, and historical-record end date unmistakable.

### Anomaly Detection

Answer: **Where do exploratory methods flag unusual behavior, and where do the methods disagree?**

Method comparison and caveats matter more than a raw anomaly count.

### Model Evaluation

Answer: **Why was this model selected and how did candidates behave under development and final test?**

Lead with protocol and selection rule, then comparison evidence and residual diagnostics.

## Content rules

- Prefer plain technical language over marketing superlatives.
- Use `historical`, `development`, `final test`, `selected`, `fixed-origin`, `one-step`, `prediction interval`, and `exploratory signal` consistently with `CONTEXT.md`.
- Do not write `production-ready`, `real-time`, `live`, `scientific anomaly`, or `current CO2` unless the capability genuinely changes and is evidenced.
- Put limitations close to the claim they constrain.

## Verification for UI changes

Before a frontend PR is ready:

1. `npm run lint`
2. `npm run build`
3. Run component/unit tests when present.
4. Run Storybook checks when present.
5. Run Playwright E2E/accessibility/visual checks when present.
6. Inspect the real rendered dashboard at desktop and mobile widths.
7. Confirm loading, empty/error, keyboard focus, and API-unavailable behavior for affected surfaces.
8. Capture/update reviewer screenshots only after the implementation passes checks.

## Known gaps to close

The current repository does not yet have a complete executable component catalog, frontend unit/component test suite, Playwright E2E/visual regression gate, or automated accessibility gate. Add those deliberately as separate SDLC work rather than hiding them behind this design document.
