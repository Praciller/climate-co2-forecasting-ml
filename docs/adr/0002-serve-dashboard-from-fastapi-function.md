# ADR 0002: Serve the dashboard from the FastAPI function

- Status: Accepted
- Date: 2026-09-05

## Context

The Vercel deployment exposes the existing FastAPI application at `/api/*`,
but the React/Vite dashboard is not served at `/`. Vercel's Python deployment
packages the FastAPI entrypoint as a function, while the current function
exclusion intentionally omits all of `frontend/**` to keep `node_modules` and
source files out of the bundle.

## Options

1. Add a second Vercel Service for the frontend. This preserves separation but
   adds routing and operational surface for a problem one FastAPI function can
   solve.
2. Remove the `frontend/**` exclusion and have the function reference the Vite
   output. This risks bundling frontend dependencies and source files.
3. Build the Vite app, stage only its generated output under the function tree,
   and serve it with FastAPI's low-priority `app.frontend()` helper.

## Decision

Choose option 3. The build stages only validated `frontend/dist` artifacts into
the ignored `api/frontend_dist/` directory. The Vercel entrypoint registers the
existing `/api` mount before `app.frontend("/", ...)`, preserving same-origin
API routing and API-route priority. The FastAPI dependency floor is raised to a
version that supports the frontend helper.

## Consequences

- The public topology remains one origin: dashboard at `/`, API at `/api/*`.
- The Python function can read the generated dashboard without packaging
  `frontend/node_modules`, frontend source, or governed training artifacts.
- `api/frontend_dist/` is build output and must never be committed.
- Vercel Preview must verify root HTML, static assets, API health, and function
  size before the change is considered ready for production verification.
