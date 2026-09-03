# ADR-0001 — Adopt repo-local agent context and quality-gated SDLC

- Status: Accepted
- Date: 2026-09-03
- Decider: Repository owner

## Context

The repository already has strong forecasting/evaluation evidence, a FastAPI serving layer, a React dashboard, documentation, and CI. However, the development process is not yet fully encoded for AI coding agents or future contributors:

- no root agent operating guide or persistent domain context;
- no machine-readable design-system contract;
- no ADR convention to preserve durable decisions;
- no issue/PR templates that carry acceptance criteria and verification evidence;
- frontend CI currently proves lint/build/audit but not component behavior, E2E flows, accessibility, or visual regressions;
- `main` is currently not protected by required status checks.

The project is particularly sensitive to subtle semantic regressions: temporal leakage, accidental final-test tuning, overclaiming interval coverage, conflating one-step evaluation with fixed-origin serving, or presenting exploratory anomaly signals as verified events.

## Options considered

### 1. Keep process in ad-hoc prompts

**Pros**

- No repository files to maintain.
- Fast for one-off edits.

**Cons**

- Important invariants must be repeated every session.
- Higher risk of context drift and inconsistent UI/ML behavior.
- Decisions and acceptance criteria are difficult to review historically.

### 2. Adopt a large all-in-one agent framework as the project process

**Pros**

- Could provide a complete workflow out of the box.

**Cons**

- Adds process weight that is disproportionate for this single-repo portfolio system.
- Can obscure the repository's own domain language and verification commands.
- Encourages loading tools/process that are irrelevant to a specific task.

### 3. Keep a small repo-local SDLC contract and use composable skills progressively

Add lean repository context (`AGENTS.md`, `CONTEXT.md`, `DESIGN.md`, ADRs), issue/PR acceptance criteria, and deterministic CI quality gates. Install approved skill collections in the coding-agent environment, but invoke them only when a task matches.

**Pros**

- Important invariants live next to the code and survive agent/session changes.
- Works across Codex/Claude/other Agent-Skills-compatible harnesses.
- Keeps GitHub issues/PRs as visible review artifacts.
- Supports progressive disclosure instead of consuming context with every possible skill.
- Deterministic CI remains authoritative even when an AI review misses something.

**Cons**

- Requires maintaining small documentation files as the project evolves.
- Some controls, such as GitHub branch protection, remain repository settings rather than code.

## Decision

Choose **Option 3**.

The repository will use:

1. `AGENTS.md` for concise commands, boundaries, workflow, and definition of done.
2. `CONTEXT.md` for domain vocabulary and non-negotiable forecasting/serving invariants.
3. `DESIGN.md` for machine-readable visual tokens plus rationale and data-visualization rules.
4. `docs/adr/NNNN-slug.md` for one durable decision per file.
5. GitHub issues/specs with explicit acceptance criteria, preferably Given/When/Then where behavior can be observed.
6. Pull requests that state verification evidence, risk, generated-artifact impact, and documentation changes.
7. CI as the deterministic merge gate. The planned frontend gate adds component/unit, E2E, accessibility, and visual checks; security automation remains additive to human review.
8. Protected `main` with required CI checks once the final check names are stable.

### Agent skills

The coding environment may install the full approved Matt Pocock and thananon/9arm skill sets. Installation does **not** imply invoking every skill for every task. Skills are loaded only when their trigger matches the work.

`/graftify` is not considered approved solely by name. Before it is used or installed, the agent must identify the installed skill/package, source repository/publisher, and behavior from a trusted source. If that cannot be verified, skip it and report the ambiguity.

## Consequences

### Positive

- Agents start from the same forecasting semantics and UI language as the repository owner.
- ML/evaluation invariants become reviewable project policy rather than transient prompt context.
- UI work has a stable design contract and explicit visualization/accessibility standards.
- Issues and PRs become agent-ready handoff/evidence artifacts.
- Future CI improvements can be introduced as focused vertical slices with clear acceptance criteria.

### Trade-offs

- `AGENTS.md`, `CONTEXT.md`, and `DESIGN.md` must be kept lean and current.
- Generated evidence still has to be verified by the existing deterministic pipeline; agent reasoning is not evidence.
- Branch protection must be configured through GitHub repository settings/rulesets after CI check names are finalized.

## Follow-up work

- Add frontend unit/component testing and Storybook.
- Add Playwright critical-path E2E, accessibility, and focused visual regression.
- Harden CI/security/supply-chain checks without introducing noisy or paid dependencies.
- Refactor the dashboard against `DESIGN.md` and verify real desktop/mobile renders.
- Protect `main` with the final required checks after those workflows are stable.
