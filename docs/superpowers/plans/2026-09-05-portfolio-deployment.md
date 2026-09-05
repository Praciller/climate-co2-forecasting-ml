# Portfolio Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare a reviewable, same-origin Vercel Hobby delivery path for the historical CO2 Forecast Lab without changing governed evidence or claiming a production deployment.

**Architecture:** Vercel serves the Vite build from the repository root configuration and discovers one FastAPI ASGI app at `api/index.py`. The wrapper reuses `src.api.main:app`; a small service-root factory points it at a verified canonical bundle extracted into writable temporary storage when the two explicit bundle environment variables are present. Vercel dependency resolution uses a root `pyproject.toml` containing only serving dependencies, while canonical Linux evidence CI continues to install the unchanged full `requirements.txt` under its pinned constraints.

**Tech Stack:** Python 3.11.16 for canonical evidence generation, Vercel Python 3.12 serving runtime, FastAPI, pandas, NumPy, statsmodels, uvicorn, React/Vite, Playwright, pytest, and Python standard-library tar/SHA/archive handling.

**Spec:** `C:/Users/pakon/.codex/attachments/12e5ee3d-8d3d-47c7-a14c-207f434c9583/pasted-text.txt`

## Global Constraints

- Do not create a Vercel project, deploy publicly, publish a Release, edit GitHub About, add a README URL, merge, or close issues.
- Preserve `requirements.txt`, canonical Python 3.11.16 evidence generation, protected `backend`/`frontend`/`browser-e2e` checks, CodeQL, model logic, evaluation logic, anomaly logic, tracked evidence, and visual snapshots.
- Vercel must install serving dependencies only; `torch`, notebooks, training dependencies, model binaries, and retraining must not enter the function.
- Bundle generation is manual-only, main-only, manifest-driven, SHA-pinned, safe to extract, and uploaded only as an Actions artifact.
- Local development keeps `/health`, `/ready`, `/model-info`, `/historical-data`, `/forecast`, `/anomalies` and localhost CORS behavior.
- Production frontend defaults to same-origin `/api`; explicit `VITE_API_URL` remains the override.
- Live browser verification is functional/semantic only and must not compare production pixels with canonical snapshots.

---

### Task 1: Lock repository and hosting contracts

**Files:**
- Create: `docs/superpowers/plans/2026-09-05-portfolio-deployment.md`
- Inspect only: `AGENTS.md`, `CONTEXT.md`, `DESIGN.md`, deployment/API/verification docs, CI, source API, frontend configuration, and current Vercel official documentation.

**Interfaces:**
- Consumes: protected green `main` at `427df68ebf64e2072eaddbf628f44243dba76d18`.
- Produces: branch `feat/portfolio-deployment` and an implementation plan that names each changed file, acceptance behavior, and verification command.

- [x] **Step 1: Fetch and verify the protected main baseline.**

Run `git fetch origin --prune`, verify `origin/main` and the latest terminal-green CI/CodeQL runs, fast-forward local `main`, and confirm a clean tree before branch creation.

- [x] **Step 2: Create the feature branch from the verified SHA.**

Run `git switch -c feat/portfolio-deployment` only after confirming the local and remote branch do not already exist.

- [x] **Step 3: Record the dependency-resolution decision.**

Use the current official Vercel Python runtime documentation as the source for Python versions, ASGI discovery, dependency files, bundle limits, `excludeFiles`, rewrites, and Vite SPA behavior. Keep the root `requirements.txt` unchanged and use `pyproject.toml` as the serving dependency declaration, then prove the declared set in tests and local build inspection.

### Task 2: Add manifest-driven serving bundle packaging

**Files:**
- Create: `scripts/package_serving_bundle.py`
- Create: `tests/test_serving_bundle.py`
- Modify: `.gitignore` only if a generated local bundle path needs a narrow ignore rule.

**Interfaces:**
- Consumes: repository root, `reports/model_manifest.json`, and `src.artifacts.validate_manifest`.
- Produces: `package_bundle(root: Path, output_archive: Path, metadata_path: Path | None = None, source_commit: str | None = None) -> BundleResult` and deterministic `.tar.gz`, SHA-256, and optional metadata.

- [x] **Step 1: Write failing tests for the package contract.**

Cover a valid manifest, every manifest path, preserved POSIX repository paths, missing/unsafe manifest paths, extraction and revalidation, no unreferenced `.joblib`/`.pt` files, deterministic member order, bounded metadata, and generated outer SHA-256.

- [x] **Step 2: Run the focused tests and confirm they fail because the packaging module is absent.**

Run `python -m pytest tests/test_serving_bundle.py -q`; the expected failure is import/collection failure for `scripts.package_serving_bundle`.

- [x] **Step 3: Implement minimal manifest-driven packaging.**

Validate the complete manifest against the repository root, include `reports/model_manifest.json` plus exactly the resolved artifact files, reject absolute paths and `..`, normalize archive names to POSIX paths, sort members, set bounded deterministic tar metadata, write metadata without secrets, and calculate the archive digest in streaming chunks.

- [x] **Step 4: Run the focused tests and then the existing artifact tests.**

Run `python -m pytest tests/test_serving_bundle.py tests/test_artifacts.py -q`; all tests must pass before refactoring.

### Task 3: Add safe bundle installation and service-root injection

**Files:**
- Create: `scripts/install_serving_bundle.py`
- Modify: `src/api/main.py`
- Modify: `src/api/service.py` only if a factory seam is required.
- Modify: `src/utils/config.py` only for a small root resolver.
- Create or modify: focused tests under `tests/` for root resolution, installer failure modes, and API behavior.

**Interfaces:**
- Consumes: `CO2_SERVING_BUNDLE_URL`, `CO2_SERVING_BUNDLE_SHA256`, `PROJECT_ROOT`, and `ForecastService(root=Path)`.
- Produces: `resolve_serving_root() -> Path`, `install_serving_bundle(url: str, expected_sha256: str, cache_root: Path) -> Path`, and `create_forecast_service() -> ForecastService`.

- [x] **Step 1: Write failing tests for explicit production root selection and closed failures.**

Assert local default resolves to `PROJECT_ROOT`, a pinned HTTPS URL installs into a temporary cache only after matching the outer digest, tampered archives fail before extraction, traversal/symlink/duplicate entries are rejected, bounds are enforced, manifest validation runs after extraction, and invalid configuration leaves the API not ready without logging secrets or paths.

- [x] **Step 2: Run the focused tests and confirm the new interfaces fail.**

Run `python -m pytest tests/test_serving_bundle.py tests/test_deployment_root.py -q`; the expected failure is missing resolver/installer behavior.

- [x] **Step 3: Implement safe installation with no shell execution.**

Require an exact 64-hex SHA, HTTPS URL without credentials, bounded streamed download, SHA verification before opening the archive, safe tar member validation including symlink/hardlink and resolved-path containment, bounded file count/size, atomic cache placement, and post-extraction `validate_manifest`.

- [x] **Step 4: Refactor FastAPI lifespan through the factory without changing route bodies.**

Have lifespan call `create_forecast_service()`, pass the resolved root to `ForecastService`, preserve the local default, and retain sanitized readiness diagnostics.

- [x] **Step 5: Run installer, service, and existing API tests.**

Run `python -m pytest tests/test_serving_bundle.py tests/test_deployment_root.py tests/test_api.py tests/test_api_diagnostics.py -q`; all must pass.

### Task 4: Add the Vercel FastAPI entrypoint and dependency isolation

**Files:**
- Create: `api/index.py`
- Create: `pyproject.toml`
- Create: `vercel.json` only with settings proved necessary by local inspection/docs.
- Create: `.vercelignore` only with narrow exclusions for training/tests/caches/runtime-only generated files.
- Create: deployment configuration tests if needed.

**Interfaces:**
- Consumes: `src.api.main:app` and the serving-only dependency set from `requirements-api.txt`.
- Produces: a Vercel-discoverable ASGI variable `app`, `/api/*` routing, and a function packaging configuration that excludes unnecessary files without swallowing the API.

- [x] **Step 1: Write failing entrypoint/config tests.**

Import `api.index.app`, assert the six `/api` endpoint behaviors against a valid temporary bundle, assert local routes still work, parse `pyproject.toml` to assert the five serving requirements and absence of `torch`, `jupyter`, `pytest`, `ruff`, and scikit-learn, and inspect `vercel.json` rewrites to ensure no frontend catch-all captures `/api`.

- [x] **Step 2: Run the tests to confirm the entrypoint and configuration are absent.**

Run `python -m pytest tests/test_deployment_api.py tests/test_dependency_isolation.py -q`; the expected failure is missing `api.index`/configuration.

- [x] **Step 3: Add the smallest wrapper and Vercel project configuration.**

Export `app` from the existing core app, set serving dependencies in root `pyproject.toml` with `requires-python = ">=3.12,<3.13"`, configure the frontend build command/output only if Vercel detection requires it, and use only documented `excludeFiles`/rewrite syntax. Do not duplicate routes or add paid-only tuning.

- [x] **Step 4: Run focused deployment API and dependency tests.**

Run `python -m pytest tests/test_deployment_api.py tests/test_dependency_isolation.py tests/test_api.py -q`; all deployment routes and local routes must pass.

### Task 5: Switch frontend production API resolution and add live-mode E2E

**Files:**
- Modify: `frontend/src/services/api.ts`
- Create: `frontend/src/services/api-config.ts`
- Create: `frontend/src/services/api-config.test.ts`
- Modify: `frontend/playwright.config.ts`
- Modify: `frontend/package.json` only to add `test:e2e:live` if a script is clearer.
- Modify: `frontend/e2e/*` only for a small external-mode guard/helper.

**Interfaces:**
- Consumes: Vite `import.meta.env.VITE_API_URL`, `import.meta.env.PROD`, and `PLAYWRIGHT_BASE_URL`.
- Produces: `resolveApiBase(env: { VITE_API_URL?: string; PROD: boolean }): string` and `test:e2e:live` that starts no local servers when the external base URL is supplied.

- [x] **Step 1: Write failing frontend tests for the three API-base cases.**

Assert explicit override wins, development defaults to `http://localhost:8000`, production defaults to `/api`, and no test performs a network request.

- [x] **Step 2: Run the focused frontend test and confirm the helper is absent.**

Run `npm run test -- src/services/api-config.test.ts`; the expected failure is a missing module/export.

- [x] **Step 3: Implement the helper and use it for all frontend requests.**

Join the resolved base with existing endpoint paths without hardcoding a Vercel hostname or adding credentials.

- [x] **Step 4: Add external Playwright mode without changing local defaults.**

Use `PLAYWRIGHT_BASE_URL` when present, disable `webServer` in that mode, retain current local backend/Vite servers otherwise, and run semantic desktop/mobile checks at 1440x900 and 390x844 while skipping canonical visual tests in live mode.

- [x] **Step 5: Run frontend focused tests and inspect the config.**

Run `npm run test -- src/services/api-config.test.ts` and `npm run test:e2e:live -- --list`; confirm no local server command is configured for live mode and no snapshot project is selected.

### Task 6: Add the manual canonical bundle workflow

**Files:**
- Create: `.github/workflows/serving-bundle.yml`

**Interfaces:**
- Consumes: protected `main`, canonical constraints, deterministic environment variables, packaging script, and the existing verification commands.
- Produces: an Actions artifact named `co2-serving-bundle-${{ github.sha }}` containing archive, SHA, and metadata only.

- [x] **Step 1: Write a workflow contract test or static validation.**

Assert `workflow_dispatch` is the only trigger, `contents: read` is the only repository permission, the runner is `ubuntu-24.04`, Python is `3.11.16`, the workflow fails clearly unless `github.ref == 'refs/heads/main'`, and no deploy/release/write action exists.

- [x] **Step 2: Implement the workflow pipeline.**

Checkout, install `requirements.txt` with `constraints/evidence-linux-py311.txt`, set canonical deterministic environment variables, run pipeline, strict drift verifier, repository verifier, package, extract/revalidate, instantiate `ForecastService`, exercise all six service semantics, calculate SHA, and upload archive/SHA/metadata with `actions/upload-artifact@v4`.

- [x] **Step 3: Run static workflow validation locally.**

Parse the YAML and run the workflow contract tests; verify that the feature branch cannot produce a canonical bundle because of the main-only guard.

### Task 7: Document deployment handoff and verify the complete change

**Files:**
- Modify: `docs/deployment.md`
- Modify: `docs/verification.md` only for deployment-specific verification facts.
- Do not modify: `README.md`, `DESIGN.md`, scientific modeling/evaluation/anomaly docs, data, reports, models, or snapshots.

**Interfaces:**
- Consumes: implementation behavior and current official Vercel research.
- Produces: a no-claim deployment contract covering topology, `/api`, same-origin CORS, bundle lifecycle, canonical/serving runtimes, required Vercel variables, cold starts, rollback, no retraining, no SLA, and post-merge handoff.

- [x] **Step 1: Update deployment documentation without a public URL.**

State that deployment preparation is implemented but no production URL is claimed; document `CO2_SERVING_BUNDLE_URL`, `CO2_SERVING_BUNDLE_SHA256`, Vercel root/build settings, release asset handoff, SHA/manifest integrity, and rollback by redeploying a previously pinned bundle.

- [x] **Step 2: Run the full backend gates.**

Run `ruff check src tests`, `ruff format --check src tests`, `python -m compileall -q src`, `python -m pytest -q`, `python -m src.verify_repository`, `docker compose config --quiet`, temporary notebook execution, and API import. Use a temporary report for any adversarial retrieval/demo check and remove it afterward.

- [x] **Step 3: Run the full frontend gates.**

From `frontend/`, run `npm ci`, `npm run lint`, `npm run test`, `npm run build`, `npm run build-storybook`, Chromium installation, `npm run test:storybook`, `npm run test:e2e`, `npm run test:e2e:verify-baselines`, and `npm audit --audit-level=high`. Confirm canonical PNGs are unchanged.

- [x] **Step 4: Perform outsider scrutiny and two-axis code review sequentially.**

Trace `api/index.py -> src.api.main -> lifespan -> bundle root -> ForecastService -> validate_manifest -> endpoints`, frontend API-base resolution, Vercel rewrites, and live-mode server selection. Review standards against repository contracts and spec coverage against this plan; report findings with file/line evidence. Do not use subagents.

- [x] **Step 5: Verify diff boundaries and create logical commits.**

Run `git diff --check`, `git diff --stat`, `git diff -- data reports models frontend/e2e/snapshots`, and confirm no governed/snapshot changes. Commit packaging, API/dependency isolation, frontend/live tests, workflow, and docs in reviewable slices.

### Task 8: Push, open, and wait for the review PR

**Files:**
- Remote branch: `feat/portfolio-deployment`
- Pull request: base `main`, head `feat/portfolio-deployment`, title `feat(deploy): prepare verified Vercel portfolio delivery`.

**Interfaces:**
- Consumes: verified branch and fresh local gates.
- Produces: an open, unmerged PR that closes #26 on merge and records production as owner-gated.

- [ ] **Step 1: Push the branch and verify the remote SHA.**

Run `git push -u origin feat/portfolio-deployment` and compare `git rev-parse HEAD` with `git ls-remote origin refs/heads/feat/portfolio-deployment`.

- [ ] **Step 2: Create the PR with the required deployment sections and fields.**

Include `Closes #26`, parent #24, the hosting decision, dependency isolation proof, API prefix, same-origin CORS, bundle/workflow integrity, tests, limitations, and explicit `PUBLIC_DEPLOYMENT_CREATED=NO`.

- [ ] **Step 3: Wait for fresh PR CI and CodeQL.**

Require backend, frontend, browser-e2e, and CodeQL to finish green on the new head. Fix failures on this branch only; do not weaken tests or create a second PR.

- [ ] **Step 4: Stop at owner handoff.**

Leave the PR open, unmerged, and clean. Report `LOCAL_BUNDLE_TEST` separately from `CANONICAL_MAIN_BUNDLE`, which is not created in this PR stage; recommend merge, protected-main bundle generation, pinned release asset, Vercel project creation/configuration, production deployment, public API/browser verification, and only then README/About updates.
