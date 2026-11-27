# frontend/

React + TypeScript + ECharts (Vite). Thin — no metric logic, no direct warehouse
queries; it talks to the backend, which talks to the semantic layer. See ADR-0002
for why this is built thin rather than on Grafana Scene.

## Run

```bash
npm install
npm run dev        # http://localhost:5173, proxies /api -> backend 127.0.0.1:8001
```

## Build

```bash
npm run build      # tsc --noEmit (typecheck) + vite build -> dist/
```

## Structure

- `src/api.ts` — typed client for the backend API (`/api/cubes`, `/api/query`)
- `src/App.tsx` — dashboard (KPI cards) + Explore (dimension picker)
- `src/components/BarChart.tsx` — ECharts bar chart
- `src/components/MetricCard.tsx` — big-number card

Phase 2 currently ships bar charts + big-number cards; more chart types, filters,
time-grain, drill-down, and dashboard persistence are still open (see roadmap).
