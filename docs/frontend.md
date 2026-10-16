# Frontend Service Documentation

## Purpose / Context
The Frontend is a specialized "Data Noir" terminal designed for high-density information display. It prioritizes speed, readability, and "Institutional" aesthetics over playful consumer design.

## 1. Key Technologies
- **Framework**: Next.js 16 (App Router, Turbopack), React 19
- **Styling**: Tailwind CSS
- **State**: React Query + Context
- **Charts**: Recharts / Lightweight Charts

## 2. Design System: "Data Noir"
> [!NOTE]
> See [Style Guide](style_guide.md) for full tokens.

- **Background**: `#0a0a0a` (Near Black)
- **Surface**: `#1a1a1a` (Dark Grey)
- **Primary Accent**: `#00ff9d` (Terminal Green) - Used for "Success/Edge".
- **Secondary Accent**: `#ff4444` (Alert Red) - Used for "Risk/Stop".
- **Typography**: Monospace (JetBrains Mono) for data, Sans (Inter) for UI.

## 3. Directory Structure

```
frontend/
├── app/                # Next.js App Router (Pages)
├── components/         # React Components
│   ├── strategies/     # Complex strategy builders
│   ├── shared/         # Buttons, Inputs, Cards
│   └── visualizations/ # Charts and Graphs
├── lib/                # Utils, API clients
└── public/             # Static Assets
```

## 4. Component Rules

### "The Terminal" Layout
- **Density**: High. Avoid excessive whitespace.
- **Borders**: Thin, subtle borders (`border-white/10`) define structure.
- **Feedback**: Immediate. Buttons should show loading states.

### Charting
- **Real-time**: Charts must handle streaming updates via WebSocket/SSE.
- **Tooltips**: Essential. Data points must be inspectable.

## 5. Development Guide

### Running Locally
Needs Node.js 20.9 or newer; the Docker image uses Node 24 LTS.
```bash
cd frontend
npm ci
npm run dev
```

Open the dev server at http://localhost:3000 (or 127.0.0.1). `next dev` serves its dev resources only to localhost and the origins in `allowedDevOrigins` (`next.config.js`); opened from another host or a LAN IP, the page loads but never becomes interactive until that origin is added there.

Checks: `npm run lint` (ESLint, `eslint.config.mjs`) and `npm run build`. `next build` type-checks but no longer lints. For a standalone type-check on a fresh checkout, run `npx next typegen` first, then `npx tsc --noEmit`.

Change dependencies with npm 11 (Node 24): it records each native package's libc in `package-lock.json`, so the Alpine image installs only the musl builds. npm 10 drops those fields.

### Adding a Page
1.  Create `app/dashboard/new-feature/page.tsx`.
2.  Ensure it uses `layouts/DashboardLayout`.
3.  Add breadcrumbs for navigation depth.
