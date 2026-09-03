# AGENTS.md

## Mission

Maintain this repository as a **reproducible, leakage-safe historical CO₂ forecasting portfolio system**. Prefer evidence, explicit boundaries, deterministic verification, and small reviewable changes over feature volume.

This project is **not** a current atmospheric feed, climate-policy model, production monitoring service, or scientific anomaly detector. Do not weaken those boundaries in code, UI, or documentation.

## Start every task here

1. Read the issue/spec and its acceptance criteria.
2. Read `CONTEXT.md` for domain language and invariants.
3. Read the relevant docs under `docs/` and any ADRs under `docs/adr/`.
4. For frontend work, read `DESIGN.md` before editing UI.
5. Inspect the existing implementation and reuse established seams/components before adding new ones.
6. Make a short plan before editing. If a material product/architecture decision is unresolved, stop and record/resolve it before implementation.

## Repository map

- `src/` — data, feature, model, evaluation, anomaly, API, and verification code.
- `tests/` — backend/regression tests.
- `frontend/` — React + TypeScript + Vite dashboard.
- `data/` — packaged raw, processed, and sample data used for reproducible evidence.
- `reports/` — generated evaluation/governance evidence and screenshots.
- `models/` — model artifacts where applicable.
- `notebooks/` — executable analysis notebooks.
- `docs/` — source, modeling, evaluation, API, frontend, deployment, verification, ADRs, and postmortems.

## Data/ML invariants — do not violate

- Time is ordered. Never introduce random train/test splitting for forecasting evidence.
- The final-test period is used **once after selection**. Never use it for model selection, hyperparameter choice, feature design, or interval calibration.
- Features for a target timestamp must use only information available before that target. No target leakage or future fill.
- Development rolling-origin folds are the selection evidence; final-test metrics do not retroactively change the selected model.
- Keep one-step evaluation semantics distinct from fixed-origin multi-step API projections.
- The 90% residual-quantile interval is calibrated/evaluated for the documented one-step protocol. Do not imply general multi-horizon calibration.
- The LSTM remains a pipeline smoke demonstration unless a new governed experiment explicitly promotes it.
- Anomaly outputs are exploratory statistical signals, not verified climate events or causal claims.
- Generated evidence must remain traceable through the manifest/checksum verification path.
- Never hand-edit generated metrics to make results look better. Change the pipeline, regenerate, and preserve the evidence trail.

## Frontend rules

- `DESIGN.md` is the design contract.
- Reuse existing components before creating near-duplicates.
- Use shared design tokens; do not scatter one-off colors, spacing, radii, or typography values.
- Data visualization must favor interpretation over decoration: readable axes/units, clear uncertainty, explicit model/protocol labels, and non-color-only encodings.
- Preserve keyboard focus, reduced-motion behavior, responsive tables/charts, loading/empty/error states, and API-unavailable states.
- Never turn statistical signals into alarmist visual language.
- For UI changes, verify the rendered result in a real browser at desktop and mobile widths; add automated component/E2E coverage when the test stack supports it.

## Backend/API rules

- Preserve bounded inputs and explicit response provenance/limitations.
- Read governed repository artifacts only; never accept arbitrary user-controlled artifact paths.
- Keep readiness stricter than liveness: readiness means required governed artifacts validate.
- Prefer structured, parseable logs with stable fields when adding operational logging. Never log secrets.
- API/documentation changes must stay synchronized with `docs/api.md` and tests.

## Commands

### Backend / full evidence

```bash
python -m src.pipeline
ruff check src tests
python -m compileall -q src
python -m pytest -q
python -m src.verify_repository
```

Execute the notebook when analysis/notebook behavior changes:

```bash
jupyter nbconvert --to notebook --execute notebooks/01_eda.ipynb --output executed.ipynb --output-dir /tmp
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run build
npm audit --audit-level=high
```

Run any additional test, Storybook, accessibility, or E2E scripts that exist after the SDLC quality-gate work lands.

### Container contract

```bash
docker compose config --quiet
```

Use `docker compose up --build` only when integration behavior needs a running stack.

## Change discipline

- One issue/spec should map to one coherent branch/PR whenever practical.
- Keep changes vertically sliced and reviewable; avoid unrelated cleanup.
- Prefer regression tests before fixes for reproducible bugs.
- Do not add a dependency when the existing stack can solve the problem cleanly.
- Do not commit secrets, local credentials, `.env`, caches, virtualenvs, node_modules, or ungoverned binary artifacts.
- When a decision changes architecture, model semantics, evaluation policy, API contract, or design-system rules, add/supersede an ADR instead of silently changing intent.
- Documentation must describe code/evidence that actually exists; never claim hosted production behavior without verified deployment evidence.

## Agent-skill policy

Use skills by **progressive disclosure**: install the approved skill sets, but invoke a skill only when the task matches it. Do not load every skill into every task.

Preferred flow when available:

- Matt Pocock skills: repository setup/context → clarify with docs → spec/tickets → TDD/implementation → code review/research/architecture as needed.
- 9arm skills: use debugging, scrutiny, postmortem, context-control, Qwen delegation, or management communication only for matching work.
- `/graftify`: use only if the installed skill can be identified from a trusted source and its behavior is appropriate for the task; never auto-install an unverified package merely because the name appears in a prompt.

## Definition of done

A task is done only when:

- acceptance criteria are demonstrably satisfied;
- relevant backend/frontend checks pass;
- generated evidence is regenerated and verified when affected;
- UI changes were visually checked when applicable;
- security/data-boundary regressions were considered;
- docs/ADR are updated when behavior or decisions changed;
- the PR explains verification evidence and remaining limitations.
