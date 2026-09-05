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

## Deployment preparation status

Deployment preparation is implemented for a single Vercel Hobby project, but no
public production URL is claimed by this repository. Production project
creation, bundle publication, deployment, and public verification remain
owner-gated post-merge actions.

The target topology is one public origin:

```text
Vercel project root
  frontend/dist/       React/Vite static output
  /api/*               api/index.py -> existing FastAPI app
```

The Vercel configuration builds the frontend with
`npm --prefix frontend run build` and publishes `frontend/dist`. The application
currently navigates between pages internally, so no catch-all SPA rewrite is
needed. If URL-based deep links are introduced later, any rewrite must exclude
`/api/*`.

## API routing and CORS

`api/index.py` mounts the existing `src.api.main:app` under `/api`, without
copying endpoint implementations. The production contract is:

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

## Serving dependency isolation

Canonical evidence generation continues to install the full `requirements.txt`
under `constraints/evidence-linux-py311.txt` on Ubuntu 24.04 with Python
3.11.16. Vercel's Python runtime automatically installs the root
`pyproject.toml` serving dependencies. The committed build command is
`npm --prefix frontend ci && npm --prefix frontend run build`, so frontend Node
dependencies remain installed before the static build. The root declaration
contains only FastAPI, NumPy, pandas, statsmodels, and uvicorn. The
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

The feature-branch local bundle test is not the canonical main bundle. The
canonical bundle is **not yet created in this deployment-preparation stage**.

After this PR is merged, the owner/ChatGPT should:

1. run the manual workflow from protected green `main`;
2. inspect the archive, metadata, and SHA artifact;
3. publish the archive as a public, immutable, pinned release asset;
4. create the Vercel Hobby project with repository root as its root directory;
5. configure `CO2_SERVING_BUNDLE_URL` and `CO2_SERVING_BUNDLE_SHA256` without
   putting credentials in the URL;
6. deploy from protected green `main`;
7. verify all public API endpoints and all five pages at desktop/mobile widths;
8. inspect console/network behavior before adding any public URL to README or
   GitHub About.

## Runtime limitations and rollback

The first request on a cold function instance may download and validate the
pinned public bundle, so startup latency depends on the archive size and host
network. No current-data ingestion, hosted retraining, monitoring service,
database, persistent cache, or SLA is claimed. The fixed-origin historical
forecast and its documented one-step interval limitation remain unchanged.

Rollback means redeploying a known-good Vercel build with the previously pinned
bundle URL and SHA, or correcting the two environment variables to a previously
verified immutable asset. Do not retrain or regenerate evidence on Vercel.
