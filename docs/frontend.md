# Frontend

## Stack

- React 19
- TypeScript
- Vite 8
- Tailwind CSS 4
- Recharts
- Lucide icons

## Pages

- Overview
- Data Explorer
- Forecasting
- Anomaly Detection
- Model Evaluation

## Architecture

API calls live in `src/services/api.ts`. Shared data loading lives in `useDashboardData`. `App.tsx` composes lazy-loaded pages and navigation instead of owning chart or table implementation.

## States

- skeleton loading state
- explicit API-unavailable state with retry
- selected navigation state
- interactive forecast horizon selector
- horizontally scrollable mobile tables

## Build

```bash
cd frontend
npm ci
npm run lint
npm run build
```

Set `VITE_API_URL` to override the default `http://localhost:8000`.
