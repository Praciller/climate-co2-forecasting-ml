# Deployment

## Local Docker Compose

```bash
docker compose up --build
```

This starts:

- API on `http://localhost:8000`
- frontend on `http://localhost:5173`

The API image uses `requirements-api.txt` so serving does not install notebook or training dependencies.

## Optional Hosted Portfolio Mode

Recommended version 1:

- deploy the static frontend to Vercel or Netlify
- keep full training local
- host the API only when a stable free service is available
- treat generated reports and screenshots as the durable portfolio evidence

## Production Changes

Before a public API deployment:

- replace permissive localhost CORS with explicit origins
- add process-level health monitoring
- add forecast artifact versioning and checksum validation
- define resource and timeout limits
- rerun full model training and regenerate reports

Deployment is optional and no deployment status is claimed by this repository.
