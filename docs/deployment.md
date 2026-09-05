# Deployment

## Local Docker Compose

```bash
docker compose up --build
```

This starts:

- API on `http://localhost:8000`
- frontend on `http://localhost:5173`

The API image uses `requirements-api.txt`, so local serving does not install
notebook or training dependencies.

## Verified portfolio deployment

The public portfolio demo is verified at
[https://climate-co2-forecasting-ml.vercel.app](https://climate-co2-forecasting-ml.vercel.app).
Final production verification on 2026-09-05 used protected `main` SHA
`7d791b44c65e36de36ef00c481473389cb216036` and Vercel deployment
`dpl_GW4WK9HPf5vxHrzuYv55Fo4v66RW`, which reached `READY` on Python 3.12.

Verification confirmed the dashboard root and all six `/api/*` contracts return
HTTP 200 with `ready=true`, 526 historical rows, a 24-month SARIMA forecast, and
8 Isolation Forest / 0 residual anomaly signals. Live Playwright verification
passed all 14 production dashboard checks across desktop and 390px mobile; the
two Preview-only checks were intentionally skipped. Production runtime-log
inspection found no 5xx responses and no error/fatal entries during the final
verification window.

This remains a portfolio deployment of the pinned historical governed bundle.
It is not a current atmospheric feed, hosted retraining system, monitoring SLA,
or production forecasting service.

The production topology is one public origin:

```text
Vercel project root
  api/frontend_dist/   staged React/Vite static output (generated, ignored)
  /api/*               api/index.py -> existing FastAPI app
```

The Vercel configuration builds the frontend with
`npm --prefix frontend run build`, then stages only its `index.html` and built
assets into `api/frontend_dist/`. The source tree, `node_modules`, and original
`frontend/dist/` remain excluded from the Python function upload. `api/index.py`
serves that generated directory with FastAPI's `app.frontend()` helper after the
`/api` mount; normal API routes therefore retain priority, and the explicit
`index.html` fallback supports client-side dashboard paths. If URL-based deep
links are introduced later, any rewrite must exclude `/api/*`.

## API routing and CORS

`api/index.py` serves the generated dashboard at `/` and mounts the existing
`src.api.main:app` under `/api`, without copying endpoint implementations. The
production API contract is:

- `/api/health`
- `/api/ready`
- `/api/model-info`
- `/api/historical-data`
- `/api/forecast?horizon_months=24`
- `/api/anomalies`

The local application continues to expose the unprefixed routes used by Docker,
Uvicorn, and existing tests. Local split frontend/API development retains
localhost and `127.0.0.1` CORS. The production frontend calls `/api` on the same
origin, so production does not need a CORS allowlist, credentials, or wildcard
`Access-Control-Allow-Origin`.

The staging command is portable Python and validates that the build output has
`index.html`, contains no symlinks, and contains none of the source, test,
training, data, or dependency directories that must remain outside the
function. Frontend-public assets such as the dashboard's evidence images remain
valid build output. It replaces only the generated `api/frontend_dist/`
directory and does not modify tracked repository files.

## Serving dependency isolation

Canonical evidence generation continues to install the full `requirements.txt`
under `constraints/evidence-linux-py311.txt` on Ubuntu 24.04 with Python
3.11.16. The committed Vercel install override is intentionally empty so the
dashboard's project-level install command cannot select the full training
environment. The committed build command installs the root `pyproject.toml`
serving dependencies, then runs `npm --prefix frontend ci` before the static
build. The root declaration contains only FastAPI, NumPy, pandas, statsmodels,
and uvicorn. The
`.vercelignore` upload boundary excludes `requirements.txt`,
`requirements-api.txt`, constraints, training data, generated reports, models,
notebooks, tests, and local build outputs from Vercel inputs. In particular,
`torch` is not a serving dependency and is not installed in the function.

The lowest currently supported Vercel Python runtime selected for this project
is 3.12. This is intentionally distinct from the canonical evidence-generation
runtime: Vercel only serves a completed bundle and never regenerates evidence or
trains models. See the [Vercel Python runtime
documentation](https://vercel.com/docs/functions/runtimes/python) and
[FastAPI deployment documentation](https://vercel.com/docs/frameworks/backend/fastapi)
for the current platform contract.

## Governed serving bundle

The API reads a complete immutable bundle rather than repository runtime-only
files. `scripts/package_serving_bundle.py` reads
`reports/model_manifest.json`, validates every manifest artifact, preserves its
repository-relative POSIX path, writes deterministic tar metadata, and emits an
outer SHA-256. It does not add unreferenced model binaries; the current
precomputed `ForecastService` path needs zero `.joblib` or `.pt` files.

`scripts/install_serving_bundle.py` accepts these explicit production variables:

```text
CO2_SERVING_BUNDLE_URL=https://...
CO2_SERVING_BUNDLE_SHA256=<64 hex characters>
```

Both variables are required together. The URL must be HTTPS and contain no
credentials or query data. Installation downloads to temporary storage, checks
the outer SHA-256 before extraction, rejects traversal, links, duplicates,
oversized files, and escaping paths, then revalidates the manifest and all
artifact checksums. A process-local cache avoids downloading once per request.
The extracted root is read-only by application convention; it is not a
retraining workspace.

## Canonical bundle workflow

`.github/workflows/serving-bundle.yml` is manual-only (`workflow_dispatch`),
has `contents: read` permission, runs on `ubuntu-24.04` with Python `3.11.16`
and `constraints/evidence-linux-py311.txt`, and fails unless selected from
`refs/heads/main`. It uses the canonical deterministic environment variables,
runs the pipeline, strict drift verification, repository verification, package
creation, safe extraction, manifest validation, FastAPI/service smoke checks,
and uploads the archive, SHA file, and small metadata JSON as an Actions
artifact. It does not deploy, publish a GitHub Release, or grant write access.

The canonical serving bundle is published as an immutable commit-pinned GitHub
Release asset:

- release tag: `serving-bundle-de31c1e949faacf1af2d8979b46edda72d4f0428`
- source commit: `de31c1e949faacf1af2d8979b46edda72d4f0428`
- archive SHA-256: `d3301ed1b2d06fcd205cb9b78b2a37c954333a6e99b4743ceb4b16cda4a9d1a1`

The Vercel Production environment uses that pinned release URL together with the
matching SHA-256. Startup downloads the archive, validates the outer checksum,
extracts it safely, and revalidates every manifest-governed artifact before the
API reports ready.

Final delivery verification completed in this order:

1. protected `main` CI and CodeQL passed after the dashboard-root serving fix;
2. Vercel Production reached `READY` on the merged SHA;
3. the root plus all six API endpoints were verified publicly;
4. all five dashboard destinations passed live desktop/mobile Playwright checks;
5. production runtime logs were checked for 5xx and error/fatal events;
6. the canonical alias was approved for README and GitHub About use.

## Runtime limitations and rollback

The first request on a cold function instance may download and validate the
pinned public bundle, so startup latency depends on the archive size and host
network. No current-data ingestion, hosted retraining, monitoring service,
database, persistent cache, or SLA is claimed. The fixed-origin historical
forecast and its documented one-step interval limitation remain unchanged.

Rollback means redeploying a known-good Vercel build with the previously pinned
bundle URL and SHA, or correcting the two environment variables to a previously
verified immutable asset. Do not retrain or regenerate evidence on Vercel.
