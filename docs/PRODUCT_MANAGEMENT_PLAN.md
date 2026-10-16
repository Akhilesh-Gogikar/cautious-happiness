# Product Management Plan: Every Page and Feature

| | |
| --- | --- |
| **Date** | 2026-10-14 |
| **Baseline** | Commit `eb728a0`, tested end to end. See the [QA Test Report](QA_TEST_REPORT.md). Defect IDs `QA-xxx` refer to that report. |
| **Builds on** | [YC-Style Product Development Plan](YC_PRODUCT_DEVELOPMENT_PLAN.md) (strategy, ICP, metrics) and [Product Framework](PRODUCT_FRAMEWORK.md) (workflow) |
| **Audience** | Founders, engineers, design, and anyone deciding what to build, fix, hide, or cut next |

---

## 1. How to read this plan

Every page, dashboard view, global component, backend capability, and platform concern in the current app has its own **feature card** (§5). So does each capability a pilot needs that doesn't exist yet (status `—` in §3). Each card states:

| Card field | What it captures |
| --- | --- |
| **Job** | Who the feature is for and why it exists |
| **Today** | What testing showed it actually does, with `QA-xxx` references |
| **Decision** | One of the decision types below |
| **Requirements** | Numbered, testable acceptance criteria |
| **Metric** | How we know it is working |
| **Priority / Phase / Size** | When and how big |

**Decision types**

| Decision | Meaning |
| --- | --- |
| **Fix** | Right feature, broken implementation. Repair in place. |
| **Rebuild** | Right job, wrong foundation. Replace the implementation. |
| **Wire** | UI is fine; connect it to real data or a real backend. |
| **Merge** | Duplicates another surface; fold it in. |
| **Hide** | Valid later, not now. Put it behind a feature flag and remove it from nav. |
| **Cut** | Off-strategy or misleading. Delete. |

**Priority**

| Level | Meaning |
| --- | --- |
| **P0** | Blocks the product or is a security exposure. Do now. |
| **P1** | Required for a credible pilot. |
| **P2** | Pilot polish and expansion. |
| **P3** | After pilots pull the product forward. |

**Size** assumes one engineer: **S** ≤ 2 days, **M** 3–5 days, **L** 1–3 weeks, **XL** > 3 weeks.

**Phases** (detailed in §6)

| Phase | Name | Weeks | Dates |
| --- | --- | --- | --- |
| **0** | Boot, secure, connect | 1–2 | 2026-10-14 → 10-28 |
| **1** | Make the audited loop real | 3–8 | 10-29 → 12-09 |
| **2** | Pilot-ready | 9–16 | 12-10 → 2027-02-03 |
| **3** | Expand after pull | — | 2027-02 onward |

---

## 2. Product direction (unchanged, re-anchored)

The YC plan already chose the wedge, and this plan keeps it:

> **Alpha Insights is an audit layer for commodity intelligence.** It turns noisy narrative, market and competitor signals into **critic-reviewed, archived decision memos** for hedge-fund risk and trading teams.
>
> **Core loop:** signal → sources → forecast → critic review → archived decision memo

**Primary personas** (from the YC plan): Head of Risk, Commodity PM/Trader, Quant Researcher, Ops/Security Lead.

**What testing changed about the plan.** The YC plan's Q2 2026 outcome, "a real user can complete the audited workflow without hitting avoidable demo breakage", **has not been met** as of 2026-10-14:

- The API does not boot (QA-001, QA-002).
- Login is not real (QA-003, QA-004).
- The core loop never renders a result (QA-008).
- Chat returns nothing against a real model (QA-009).
- The default stack serves a canned mock LLM (QA-010).

So the roadmap is **re-baselined**. Phase 0 must finish before any pilot conversation that includes a live demo.

**Three product principles** apply to every card below:

1. **Nothing fake that looks real.** Every on-screen number is live, or visibly labeled `DEMO`. This makes the existing backlog item MGMT-002 ("narrative honesty") a UI requirement, not just a docs requirement.
2. **Every generative feature has a Critic.** This is already a rule in [AGENTS.md](AGENTS.md#3-rules-of-engagement). Today, Chat, Strategy generation and Mirror analysis have no validator.
3. **Privacy and auditability first.** Secrets stay server-side, every sensitive action is audited, and no execution happens without explicit confirmation.

---

## 3. Current-state scorecard (all features)

**Status legend**

| Mark | Meaning |
| --- | --- |
| ✅ | Works |
| 🟡 | Partial |
| 🎭 | Mock presented as live |
| ❌ | Broken |
| ⛔ | Security risk |
| — | Doesn't exist yet |

**Wedge fit:** ★★★ core loop · ★★ supports pilot · ★ nice-to-have · ✗ off-strategy

### 3.1 Pages (routes)

| ID | Page | Status | Wedge fit | Decision | Priority | Phase | Size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PG-01 | `/` Landing | 🟡 | ★ | Fix | P2 | 1 | S |
| PG-02 | `/login` and session | ❌⛔ | ★★★ | Rebuild | **P0** | 0 | M |
| PG-03 | `/dashboard` shell | 🟡 | ★★★ | Fix | P1 | 1 | M |
| PG-04 | `/intelligence` (standalone) | 🟡⛔ | ★★ | Merge | P1 | 0 | S |
| PG-05 | `/portfolio` (standalone) | 🎭⛔ | ✗ | Cut | P1 | 0 | S |
| PG-06 | `/agents/builder` | 🎭 | ✗ (now) | Hide | P2 | 1 | S |
| PG-07 | 404, error and loading pages | 🟡 | ★★ | Fix | P1 | 1 | S |
| PG-08 | Onboarding and first run | — | ★★ | Fix | P2 | 2 | S |

### 3.2 Dashboard views

| ID | View | Status | Wedge fit | Decision | Priority | Phase | Size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VW-01a | Live Markets: Watchlist | ❌ (401) | ★★★ | Wire | **P0** | 0–1 | M |
| VW-01b | Live Markets: Neural Audit (run a forecast) | ❌ | ★★★ | Fix | **P0** | 0 | M |
| VW-01c | Live Markets: Result panel → Decision memo | 🟡 | ★★★ | Rebuild | P1 | 1–3 | L |
| VW-01d | Live Markets: "Discuss findings" chat | ❌ | ★★ | Merge | P1 | 1 | S |
| VW-01e | Live Markets: Macro State, Signals, Depth chart | 🎭 | ★ | Hide, then Wire | P1 | 1 | S |
| VW-01f | Live Markets: Data Matrix | 🎭 | ★ | Hide, then Wire | P1 | 1 | S |
| VW-02 | Portfolio | 🎭 | ✗ (now) | Merge into Positions | P2 | 2 | M |
| VW-03 | Alpaca Markets | 🟡⛔ | ★ | Merge into Positions | P2 | 2 | M |
| VW-04 | Strategies (CLI) | 🟡 | ✗ (now) | Merge into Strategy Lab, then Hide | P2 | 1 | S |
| VW-05 | Correlations | 🎭 | ✗ | Hide, then Rebuild | P3 | 3 | M |
| VW-06 | Quant Engine | ❌ | ✗ (now) | Merge into Strategy Lab, then Hide | P2 | 1 | S |
| VW-07 | Intelligence Mirror | 🟡 | ★★★ | Fix and Wire | P1 | 1–2 | L |
| VW-08 | Analyst Chat | ❌ | ★★ | Fix and Merge | **P0** | 0–1 | M |
| VW-09 | Alpha Scanner | 🎭 | ★ | Hide, then Rebuild | P2 | 2 | M |
| VW-10 | Security | 🎭 | ★★ | Rebuild | P1 | 1 | M |
| VW-11 | Config | ❌ | ★★ | Rebuild | P2 | 2 | M |
| VW-12 | Asset detail | — | ★★ | Fix | P2 | 2 | M |
| VW-13 | Track record and calibration | — | ★★ | Fix | P2 | 2 | M |

### 3.3 Global components

| ID | Component | Status | Wedge fit | Decision | Priority | Phase | Size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GC-01 | Sidebar navigation and role gating | 🟡 | ★★ | Fix | P1 | 1 | M |
| GC-02 | Ticker tape and chart modal | 🎭 | ★ | Hide, then Wire | P2 | 1 | S |
| GC-03 | Stat cards | 🎭 | ★★ | Rebuild | P1 | 1 | S |
| GC-04 | System status dropdown | 🟡 | ★★ | Fix | P1 | 1 | S |
| GC-05 | Notification center | 🎭 | ★★ | Rebuild | P2 | 2 | M |
| GC-06 | Settings modal | 🟡⛔ | ★★ | Rebuild | P1 | 1 | M |
| GC-07 | Sidebar chat (global copilot) | ❌ | ★★ | Fix and Merge | **P0** | 0–1 | S |
| GC-08 | Wallet connect (RainbowKit/wagmi) | ❌ | ✗ | Cut (done) | P1 | 1 | S |

### 3.4 Backend capabilities

| ID | Capability | Status | Wedge fit | Decision | Priority | Phase | Size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SV-01 | Authentication and identity | ⛔ | ★★★ | Rebuild | **P0** | 0–2 | L |
| SV-02 | RBAC, API keys, IP allowlist, audit log | ❌⛔ | ★★★ | Fix | **P0** | 0–1 | M |
| SV-03 | Markets data service | 🎭 | ★★★ | Wire | P1 | 1 | L |
| SV-04 | Forecast pipeline (Celery, swarm, lifecycle WebSocket) | ❌ | ★★★ | Fix | **P0** | 0–1 | L |
| SV-05 | Critic verification | 🟡 | ★★★ | Fix | **P0** | 0–1 | M |
| SV-06 | Chat service | ❌ | ★★ | Fix | **P0** | 0–2 | M |
| SV-07 | Mirror service | 🟡 | ★★★ | Fix | P1 | 1 | M |
| SV-08 | News and sentiment (FinBERT) | 🟡 | ★★ | Fix and Wire | P2 | 2 | M |
| SV-09 | Scanner service | 🎭 | ★ | Rebuild | P2 | 2 | M |
| SV-10 | Strategy generation and sandbox backtest | ❌⛔ | ✗ (now) | Hide | P3 | 3 | XL |
| SV-11 | Trade execution and Kelly sizing | 🎭⛔ | ✗ (now) | Hide | **P0** (gate) / P3 (build) | 0 / 3 | S / XL |
| SV-12 | Connectors (Polymarket, Kalshi, Alpaca, MCP) | 🟡 | ★★ | Fix and Cut | P1 | 1–2 | M |
| SV-13 | Tools API (`/tools/call`) | ⛔ | ★ | Fix | **P0** | 0 | S |
| SV-14 | Demo multi-agent RAG (`/demo/*`) | ❌⛔ | ★★ | Rebuild as document ingestion | P2 | 2 | L |
| SV-15 | Cognitive replay (`rs_engine`) | 🟡 (unused) | ★★ | Hide, then Wire | P3 | 3 | M |
| SV-16 | Health, logging, telemetry | 🟡 | ★★ | Fix | P1 | 1–2 | M |
| SV-17 | Rate limiting and caching | 🟡 | ★★ | Fix | P1 | 1 | S |
| SV-18 | Workspaces and tenancy | — | ★★ | Rebuild | P1 | 1–2 | M |
| SV-19 | Source retrieval and provenance | 🟡 | ★★★ | Rebuild | P1 | 1 | M |
| SV-20 | Physical-market data feeds | 🎭 | ★★ | Wire | P2 | 2 | L |
| SV-21 | Prompt registry | — | ★★ | Fix | P1 | 1 | S |
| SV-22 | Public API (compat routes, versioning, scoped keys, docs) | 🟡 | ★ | Fix and Cut | P1 (cut compat) / P2 | 0 / 2 | S |

### 3.5 Platform

| ID | Area | Status | Wedge fit | Decision | Priority | Phase | Size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PL-01 | Runtime and deployment (compose, LLM, nginx) | ❌ | ★★★ | Fix | **P0** | 0–2 | M |
| PL-02 | Secrets, repository visibility and security hygiene | ⛔ | ★★★ | Fix | **P0** | 0–2 | S |
| PL-03 | Data layer and migrations | ❌ | ★★★ | Fix | **P0** | 0 | M |
| PL-04 | QA automation and CI | ❌ | ★★★ | Fix | **P0** | 0 | M |
| PL-05 | Docs and narrative honesty | 🟡 | ★★ | Fix | P1 | 1–2 | S |
| PL-06 | Design system, accessibility, responsive | 🟡 | ★★ | Fix | P2 | 2 | M |
| PL-07 | Dependency hygiene | 🟡 | ★★ | Fix | **P0** (Next.js/Node upgrade) / P1 | 0–1 | S |
| PL-08 | Feature flags and pilot mode | — | ★★★ | Fix | **P0** | 0 | S–M |
| PL-09 | Scheduler and background jobs | — | ★★ | Fix | P1 | 1 | S |
| PL-10 | Environments, release and live-deployment lockdown | ⛔ | ★★★ | Fix | **P0** (lockdown) / P1 | 0 / 1 | S / M |
| PL-11 | Repo hygiene (ad-hoc scripts, vendored installer, artifacts) | 🟡 | ★ | Cut | P2 | 1 | S |
| PL-12 | Demo workspace and seed data | — | ★★ | Fix | P2 | 1–2 | S |

**Net effect on the navigation for a pilot build**

| | Items |
| --- | --- |
| **Visible** | Markets (watchlist + run forecast), Runs and Memos (new), Track record (new, VW-13, Phase 2), Intelligence Mirror, Analyst Chat, Security and Audit, Settings (with Account) |
| **Reached from other views** | Asset detail (new, VW-12, Phase 2), opened from Markets, Mirror and (when enabled) Scanner rows |
| **Hidden behind flags** | Strategy Lab, Agent Builder, Scanner, Correlations, Positions |
| **Deleted** | Wallet connect, standalone `/portfolio`, fake trade buttons |

---

## 4. Cross-cutting requirements

These apply to every card below and are not repeated in each one.

| # | Requirement | Applies to |
| --- | --- | --- |
| X-1 | **Demo-data policy.** Any value not from a live source shows a `DEMO` badge. A `PILOT_MODE=true` flag (PL-08) hides every demo-only surface. | All UI |
| X-2 | **Every API call sends the session token.** One fetch client handles auth, base URL, retries (idempotent GETs only) and 401 → re-login. No hardcoded hosts. | All frontend calls (QA-004, QA-020) |
| X-3 | **Every non-public endpoint requires auth.** Public endpoints are limited to `/health`, `/auth/*`, and docs in dev only. | All backend routes (QA-012) |
| X-4 | **Every sensitive action writes an audit event:** login, forecast run, critic override, memo export, settings change, key creation, any order. | Backend |
| X-5 | **Every generative output passes a validator** (Critic or schema check) before it is shown as authoritative. | Forecast, Chat, Mirror, Strategy |
| X-6 | **Every async UI action has loading, success, empty, error and timeout states**, and never claims success the backend didn't confirm. | All views (QA-013) |
| X-7 | **Every view is URL-addressable** (`/dashboard/<view>`), keyboard-operable, and titled. | All views (QA-043, QA-045) |

---

## 5. Feature cards

### 5.1 Pages

#### PG-01: Landing page (`/`)
- **Job:** Explain the product in one screen and route visitors to sign in. *Persona:* buyer / first-time visitor.
- **Today:**
  - Renders well.
  - Copy promises "AI-Native Superintelligence" and static claims like "Security: Quantum_Encrypted" and "Network: Global_Mesh".
  - `/grid.svg` returns 404 (QA-046).
  - The global chat bubble appears before login, and calls an authenticated API.
- **Decision:** Fix.
- **Requirements:**
  1. Rewrite the hero around the wedge: "Critic-reviewed commodity intelligence with an audit trail."
  2. Remove the fabricated status bar, or drive it from `/health`.
  3. Add `public/grid.svg` and a favicon.
  4. Don't mount `SidebarChat` on public routes.
  5. Add `<title>` and meta description. This needs the root layout split into a server layout plus client providers.
- **Metric:** Visitor-to-login click-through, tracked with privacy-safe analytics.
- **Priority / Phase / Size:** P2 · 1 · S

#### PG-02: Login and session (`/login`)
- **Job:** Authenticate a known user, establish a role, and gate the app. *Persona:* every user; the Ops/Security Lead is the approver.
- **Today:**
  - Email-only login on the client, with no password and no backend call. Any well-formed email address is accepted. The only checks are the browser's `type="email"` validation and an `includes('@')` test.
  - Admin is granted when the email matches **one hardcoded address**. Anyone can self-promote by editing `localStorage` (QA-003).
  - No token is requested, so every protected API returns 401 (QA-004).
  - The frontend roles `Admin`/`User` don't match the backend roles `admin`/`trader`/`analyst`/`risk_manager`.
- **Decision:** Rebuild, in three steps.
  - **Phase 0:** Username and password form → `POST /auth/token` (form-encoded). Store the token in memory plus an httpOnly cookie via a Next route handler. Add `GET /auth/me` to return `{username, role}`. Delete the email-based role logic and the `toggleRole` demo switch. Ship it on the upgraded Next.js (PL-07 #5).
  - **Phase 1:** Users in Postgres (SV-01), password reset, logout that revokes the token, a session-expiry UX, and redirecting signed-in users away from `/login`.
  - **Phase 2:** OIDC SSO (Okta / Azure AD) for pilot customers.
- **Requirements:**
  1. Wrong credentials show an inline error. Five failures lock the account for 15 minutes.
  2. A role from `/auth/me` drives every UI gate. No role logic based on email.
  3. A 401 from any API sends the user back to `/login` with a return URL.
  4. Login, logout and failed login are audited (X-4).
- **Metric:** 0 protected API calls returning 401 for a signed-in user; login success rate; time to first forecast after login.
- **Priority / Phase / Size:** **P0** · 0 (basic) → 1 → 2 (SSO) · M

#### PG-03: Dashboard shell (`/dashboard`)
- **Job:** The single workspace: navigation, health, and the active view. *Persona:* PM/Trader, Head of Risk.
- **Today:**
  - Loads, but the view state is local only, so reload resets to Markets (QA-043).
  - Fixed-height views double-scroll.
  - Header badges are static ("v4.2.0_STABLE", "SECURITY: MAXIMUM").
  - Header popovers render under the stat cards (QA-029).
  - Unusable at 390 px wide (QA-049).
- **Decision:** Fix.
- **Requirements:**
  1. Routes become `/dashboard/[view]`, with deep links and working back/forward.
  2. Use one layout grid with a single scroll container; views fill the remaining height.
  3. Header shows the real app version (stamped by the build, PL-10 #5), real health (GC-04), the user menu (name, role, logout), and notifications.
  4. Define a z-index scale (overlay > popover > header > content) and apply it.
  5. Below `lg`, the sidebar collapses to a drawer.
- **Metric:** 0 layout or overlap bugs in the visual regression suite; views reachable by URL = 100%.
- **Priority / Phase / Size:** P1 · 1 · M

#### PG-04: `/intelligence` (standalone page)
- **Job:** None distinct. It duplicates the Intelligence Mirror view.
- **Today:**
  - **No auth guard:** trade buttons are reachable logged out (QA-035). Fixed in `64b8dd9`: signed-out visitors go to `/login`, non-admins to `/dashboard` (UI only; the `/mirror` API is still open, QA-012).
  - No app chrome, and no link points to it.
- **Decision:** Merge. Redirect to `/dashboard/intelligence` behind auth once PG-03 ships the `/dashboard/[view]` routes (Phase 1). Until then, redirect to `/dashboard`.
- **Requirements:**
  1. Logged-out access goes to `/login`. **Done** in `64b8dd9` (QA-035); the page is admin-only, like the dashboard view.
  2. The old URL issues a 308 to the new one.
- **Priority / Phase / Size:** P1 · 0 · S

#### PG-05: `/portfolio` (standalone page)
- **Job:** None distinct. It duplicates the Portfolio view, with mock data.
- **Today:**
  - **No auth guard** (QA-035). Fixed in `64b8dd9`: signed-out visitors go to `/login`.
  - $2.1M mock book.
  - Refresh and LAYOUT buttons do nothing.
  - The "Return to terminal" link goes to the landing page.
- **Decision:** Cut. Redirect to `/dashboard/positions` once VW-02/03 ship; until then redirect to `/dashboard`.
- **Priority / Phase / Size:** P1 · 0 · S

#### PG-06: Agent Builder (`/agents/builder`)
- **Job (future):** Let a quant compose multi-step agent workflows: trigger, LLM, tool, condition, action.
- **Today:**
  - Visual canvas only. Nodes can't be configured.
  - The graph is lost on reload. Save Draft and Deploy do nothing (QA-032).
  - Its sidebar links always land on Markets.
  - Non-admins briefly see it before the redirect. Fixed in `64b8dd9`: they see the loading spinner until the redirect to `/dashboard`.
- **Decision:** Hide. Out of MVP scope per the YC plan ("full trade execution automation"). Keep the code behind `FEATURE_AGENT_BUILDER` (PL-08).
- **Requirements to un-hide (Phase 3):**
  1. Graph is persisted per user, with versions (`agent_graphs` table).
  2. Each node type has a config panel and a schema.
  3. A backend executes the graph, with dry-run mode, step logs, and Critic gating on any action node.
  4. Deploying requires the admin role, writes an audit event, and has a kill switch.
- **Metric (when live):** Graphs saved per week; dry-run success rate.
- **Priority / Phase / Size:** P2 to hide (S) · build P3 · XL

#### PG-07: Not-found, error and loading pages
- **Job:** Contain failures, so one bad record or route never takes down the whole workspace. *Persona:* every user.
- **Today:**
  - Default unstyled Next.js 404.
  - There is no `error.tsx`, `global-error.tsx` or `loading.tsx` anywhere in `app/`. Any render exception, such as the VW-01a null-category crash, replaces the whole dashboard with Next's generic "Application error: a client-side exception has occurred" screen.
- **Decision:** Fix. Raised from P3 to P1: one bad backend record can take down the whole workspace in front of a pilot.
- **Requirements:**
  1. A branded `app/not-found.tsx` with a link back to the dashboard.
  2. `app/error.tsx` and `app/global-error.tsx` show a safe message, a request ID and a retry (X-6).
  3. Each dashboard view has its own error boundary, so a failing view leaves the shell and navigation working.
  4. Each route has a `loading.tsx`.
- **Priority / Phase / Size:** P1 · 1 · S

#### PG-08: Onboarding and first run
- **Job:** Get a new user from first login to a first useful brief in ≤ 10 minutes (§7), and to a first audited run within 7 days (the YC plan's activation metric). *Persona:* every new pilot user.
- **Today:**
  - No first-run flow exists. Empty states are generic.
  - No card owns empty states, a sample question, a guided first run, or the path from invite to first login.
- **Decision:** Fix (new).
- **Requirements:**
  1. New workspaces start with a seeded example watchlist.
  2. A "Run your first audited forecast" call to action, with a sample question, shows until the user's first run completes.
  3. Contextual tips appear on the first visit to each core view. Dismissals are remembered per user.
  4. Accepting an invite (SV-18 #3) leads straight to first login and this flow.
- **Metric:** Time to first useful brief ≤ 10 min; % of new users with an audited run within 7 days.
- **Priority / Phase / Size:** P2 · 2 · S

### 5.2 Dashboard views

#### VW-01a: Live Markets, Watchlist
- **Job:** Pick the commodity or market to analyze. *Persona:* PM/Trader.
- **Today:**
  - `GET /markets` returns 401 from the UI (QA-004).
  - With demo auth, it shows 6 **static** backend items whose `last_price` looks like a probability.
  - Search and category filters work.
  - OVERSOLD/OVERBOUGHT labels are inverted.
  - A null `category` crashes the view once a category filter (ENERGY/METALS/AGRI) is selected (`m.category.toUpperCase()`, `market-table.tsx:81`). The ALL view and search are unaffected, and today's static list always sends a category.
- **Decision:** Wire.
- **Requirements:**
  1. Data comes from SV-03 (real markets plus prices) with `source`, `as_of` and units.
  2. Auto-refresh every 60 s, with a stale-data indicator after 5 minutes.
  3. Users can pin and unpin items; the watchlist is persisted per user.
  4. "Enter a custom question" opens a free-text forecast. The YC MVP scope says "user selects **or enters** a commodity theme".
  5. Remove or correct the OVERSOLD/OVERBOUGHT labels.
- **Metric:** Watchlist load success ≥ 99.5%; p95 load < 1 s.
- **Priority / Phase / Size:** **P0** (auth wiring, Phase 0) · real data P1 (Phase 1) · M

#### VW-01b: Live Markets, Neural Audit (run a forecast)
- **Job:** Start the core loop for the selected question and watch it progress. *Persona:* PM/Trader, Head of Risk.
- **Today:** This is the most important broken feature.
  - The predict call succeeds, but the lifecycle WebSocket crashes on connect (QA-008), so the UI spins forever.
  - A cached-result branch would also spin forever.
  - The success toast can race ahead of the result.
  - A pipeline error renders as an ordinary result: "0%" confidence with the critique "Error", because `run_analysis` catches every exception (`engine.py:94-103`).
  - With the shipped mock LLM every run returns 0.5 (QA-010). Failures are reported as `completed` (QA-015).
- **Decision:** Fix.
- **Requirements:**
  1. The WebSocket uses async Redis pub/sub and emits the SV-04 statuses `queued → running → complete|failed`. `running` events carry the stage (`searching`, `forecasting`, `critiquing`). nginx forwards upgrade headers (PL-01).
  2. A polling fallback runs every 2 s if the WebSocket fails. The client times out at 120 s with a retry option.
  3. Task status has a true `failed` state carrying an error code. The UI shows an actionable error, never a fake "0%" result.
  4. A cached result renders immediately.
  5. The run button is disabled while a run is in flight. Navigating away doesn't orphan the subscription.
  6. Name the button for what it does, e.g. "Run audited forecast".
- **Metric:**
  - Run completion rate ≥ 95%
  - p95 time to result ≤ 30 s on the reference local model
  - 0 runs stuck > 120 s
- **Priority / Phase / Size:** **P0** · 0 · M

#### VW-01c: Live Markets, Result panel → Decision memo
- **Job:** Present the forecast, the Critic's review, and the evidence, then **archive it as a decision memo**. This is the product's core artifact. *Persona:* Head of Risk (auditor), PM/Trader.
- **Today:**
  - Shows confidence (`adjusted_forecast`) and critique text.
  - "Severity" is hardcoded HIGH.
  - Sources, swarm components, risk factors and the initial-vs-adjusted delta are not shown.
  - Adversarial fields are never populated (QA-025). Swarm labels are mismatched (QA-026).
  - Nothing is persisted or exportable.
- **Decision:** Rebuild into a **Run detail / Memo** surface.
- **Requirements:**
  1. Show the initial forecast, the critic-adjusted forecast, the delta, the Critic score, and the verdict (pass / flag / veto).
  2. Each claim has a citation to a source with URL, publisher and timestamp. Synthetic sources are labeled `SYNTHETIC` (QA-027).
  3. Show risk factors, counter-arguments, and logical fallacies from the Critic (SV-05).
  4. A user can accept or override the Critic with a required rationale; the override is audited.
  5. Each run is persisted in a `forecast_runs` table: inputs, model and version, prompts hash, sources, outputs, critic output, user, timestamps.
  6. A **Runs** list shows history with filters (asset, date, verdict, user).
  7. **Export the memo** as PDF or Markdown with a provenance footer (run ID, model, data as-of).
  8. Record the outcome at resolution, which feeds the Brier score (SV-04 #8) and the track record (VW-13).
  9. **P2:** Memo templates, refined with pilot usage (the YC plan's "refine brief templates").
  10. **P3:** Share a memo with workspace members (SV-18), with reviewer comments and sign-off. Every share and sign-off is audited (X-4).
  11. **P3 option:** Read-only, slippage-aware sizing guidance from the Kelly engine (`services/kelly.py`) in the memo, if D-9 keeps it in scope. No order actions (D-2).
- **Metric:**
  - Memos exported per active user per week
  - Citation coverage ≥ 90% of claims
  - Critic override rate
  - Time to first useful brief
- **Priority / Phase / Size:** P1 · 1 · L; templates (#9) P2 · 2 · S; sharing and sign-off (#10) P3 · 3 · M

#### VW-01d: "Discuss findings" chat panel
- **Job:** Ask follow-up questions about a specific run.
- **Today:**
  - Sends run context to `/chat`, but the backend ignores `context` (QA-037).
  - Replies are empty against a real model (QA-009).
  - `**markdown**` renders raw.
- **Decision:** Merge into the single chat service and UI (VW-08), opened with `run_id` context.
- **Requirements:**
  1. The backend loads the run's sources and outputs as grounding.
  2. Answers cite run sources.
  3. Markdown is rendered.
- **Priority / Phase / Size:** P1 · 1 · S

#### VW-01e: Macro State, Proprietary Signals, Depth chart
- **Job (claimed):** Ambient macro context and "intelligence broadcasts".
- **Today:**
  - 100% static: SPX, VIX and similar values, and three canned signals with fixed timestamps ("2m ago", "14m ago", "1h ago").
  - The depth chart is a static SVG labeled "POLY".
  - Signal cards look clickable but aren't. The world map loads from Wikimedia.
- **Decision:** Hide in pilot mode (X-1). Later, **Wire**:
  - Macro State uses SV-03 price data.
  - Signals become a feed of real run and critic events (critic vetoes, large forecast deltas).
  - Depth chart uses a real order book where one exists (Polymarket CLOB).
- **Priority / Phase / Size:** P1 (hide) · 1 · S; wiring P2 · M

#### VW-01f: Data Matrix
- **Job (claimed):** A dense, sortable commodity grid with quick actions.
- **Today:**
  - 8 hardcoded rows on a 1 s random walk.
  - Context-menu actions only show toasts, including a **false "Routing … to nearest dark pool"** (QA-013).
  - Sparklines re-mount every second.
- **Decision:** Hide now. Later, Wire to SV-03 prices.
- **Requirements (when wired):** Real prices with as-of time. Context menu: "Run forecast", "Add to watchlist", "Open in Mirror". **No trade actions.**
- **Priority / Phase / Size:** P1 (hide, remove the fake trade) · 1 · S

#### VW-02: Portfolio
- **Job (future):** Exposure context for the Head of Risk: positions, P&L, concentration.
- **Today:**
  - Fully hardcoded $2.1M book; time-range tabs do nothing.
  - It **silently turns into the Alpaca view** once an Alpaca key exists.
  - Donut and legend percentages disagree.
- **Decision:** Merge with VW-03 into a single **Positions** view. Hide until a real source is connected.
- **Requirements:**
  1. Read-only positions from connected brokers (Alpaca first; IBKR later) via server-side credentials (GC-06).
  2. Every figure carries a source and as-of time.
  3. Show the exposure of each position to assets that have recent runs: "you hold X; latest audited view is Y".
- **Metric:** % of pilot accounts with a connected position source.
- **Priority / Phase / Size:** P2 · 2 · M

#### VW-03: Alpaca Markets
- **Job:** Show brokerage account and positions.
- **Today:**
  - Calls `localhost:8000` directly (QA-020).
  - Credentials are sent from browser localStorage.
  - Returns 401 without demo auth.
  - The error says "configure them in SYSTEM_CONFIG". That is the title of the gear-icon settings modal, but nothing on screen leads there, and the sidebar "Config" item opens a GLOBAL_CONFIG placeholder instead (QA-041).
  - "Paper_Trading" is hardcoded.
- **Decision:** Merge into Positions (VW-02).
- **Requirements:**
  1. Credentials are stored server-side, encrypted, per workspace.
  2. The view is read-only.
  3. The paper/live badge comes from the backend.
  4. Errors link to the actual settings location.
- **Priority / Phase / Size:** P2 · 2 · M

#### VW-04: Strategies (Strategy CLI)
- **Job (future):** Conversational strategy authoring.
- **Today:**
  - `/list` and `/status` print hardcoded data. `/deploy` always fails.
  - Free text returns "No response received." (QA-009).
  - A 2.4 s boot animation blocks input on every visit.
- **Decision:** Merge with Quant Engine into **Strategy Lab**, then Hide (out of MVP).
- **Requirements to un-hide:** Same as VW-06.
- **Priority / Phase / Size:** P2 (hide) · 1 · S

#### VW-05: Correlations
- **Job (claimed):** A cross-asset dependency matrix.
- **Today:**
  - Static matrix of crypto and US politics assets (BTC, TRUMP, BIDEN, FED). This is off-wedge for commodities.
  - Most heatmap colors don't render (QA-039).
  - Badges claim "AI TARGETED / UPDATED HOURLY".
  - An unused duplicate component exists (`correlation-heatmap.tsx`).
- **Decision:** Hide now. Rebuild in Phase 3 as **commodity correlations computed from real price history** (rolling 30/90-day windows), with significance shading.
- **Priority / Phase / Size:** P3 · 3 · M

#### VW-06: Quant Engine (Strategy Builder)
- **Job (future):** Natural language → strategy code → backtest.
- **Today:**
  - LLM prose lands in the code editor with no validation (QA-031).
  - Save and Backtest do nothing.
  - Python is highlighted as JavaScript.
  - The UI sends a hardcoded `model: 'lfm-40b'`, but the backend ignores it and always calls the configured llama.cpp `/completion` endpoint (`strategy/service.py:33-44`), so model selection is dead code.
  - The endpoint is unauthenticated (QA-012).
  - A file-based strategy package format already exists: `strategies/template/strategy_config.yaml`, an example `strategies/moving_average_cross/` package, and `backend/scripts/scaffold_strategy.py`. The scaffold script and the example backtest hardcode one machine's absolute path, and the scaffold needs `pyyaml` and `backtrader`, which aren't in requirements.
- **Decision:** Merge into **Strategy Lab**, then Hide. Out of MVP; build in Phase 3.
- **Requirements to un-hide (Phase 3):**
  1. Generated code is AST-validated against a strategy interface; invalid output shows the Critic's errors. Adopt `strategy_config.yaml` as the interface spec (and fix its hardcoded paths), or delete the `strategies/` package and the scaffold script.
  2. Strategies are persisted and versioned per user.
  3. Backtest runs in a **hardened sandbox** (SV-10): non-root, no network, CPU/memory/time limits. Results use the `BacktestResult` schema.
  4. Code generation goes through the Critic (X-5).
- **Priority / Phase / Size:** P2 (hide and remove dead buttons) · 1 · S; strategy package decision P3 · 3 · S; build P3 · XL

#### VW-07: Intelligence Mirror
- **Job:** Show what competitor algorithms and crowds are "reading" (crowd sentiment and conviction), so the fund can anticipate narrative-driven dislocations. This is the vision document's flagship. *Persona:* Head of Risk, PM/Trader.
- **Today:**
  - Two **hardcoded** real firm names as "competitors".
  - Analyze runs search + LLM (sources were blocked in the sandbox). On empty results the UI shows a **fabricated fallback** source card.
  - Results aren't persisted.
  - The Decision Protocol's BUY/SELL buttons give a **false "Mirror Trade Initialized"** (QA-013). The target asset is hardcoded WTI/BRENT.
  - No auth on the backend (QA-012).
- **Decision:** Fix and Wire. Re-scope "competitors" as **tracked narrative sources**.
- **Requirements:**
  1. **Tracked targets** have full create/read/update/delete: name, description, source domains, keywords, linked assets. Seed examples are generic, not real firm names.
  2. Analyze pulls from real sources (search plus RSS plus customer-provided documents via SV-14). Each source is stored with provenance.
  3. Output: sentiment score, crowd conviction, key narratives, a divergence vs. our latest audited forecast for the linked asset, and a Critic review (X-5).
  4. **Remove BUY/SELL.** Replace with "Run audited forecast on <asset> with this narrative context". This links Mirror into the core loop.
  5. Persist each snapshot. Show a time series of sentiment and conviction per target.
  6. Never fabricate a fallback source. An empty state says "No sources found" and suggests widening domains.
  7. **P2:** The divergence panel merges the unused `NarrativeDivergence` component, without its OVERHYPED (SHORT) / UNDERVALUED (LONG) verdict (D-2). Once SV-20 lands, it also compares against the physical feed.
- **Metric:** Snapshots per week; % of snapshots with ≥ 3 sources; forecasts started from Mirror.
- **Priority / Phase / Size:** P1 · 1 · L; `NarrativeDivergence` panel (#7) P2 · 1–2 · S

#### VW-08: Analyst Chat
- **Job:** Ask questions about markets, runs and memos with grounded answers. *Persona:* PM/Trader, Quant Researcher.
- **Today:**
  - Streaming request returns 200, but the **bubble is empty** against real llama.cpp (QA-009). With the mock, every answer is the same sentence.
  - The persona toggle does nothing (QA-036). History is not shown after a view switch.
  - Markdown is not rendered.
  - **Four separate chat surfaces exist:** Analyst Chat, sidebar chat, Discuss-findings panel, and Strategy CLI.
- **Decision:** Fix (P0 parser) and Merge (one chat).
- **Requirements:**
  1. The SSE parser handles llama.cpp `data:` framing. Covered by a contract test using a recorded stream.
  2. **One chat service and one UI component**, used in the full-page view and the slide-over. Context is `{route, run_id?, asset?}`.
  3. Persona maps to a server-side system prompt.
  4. Conversations are persisted with list, rename and delete.
  5. Markdown and citations are rendered. Stop and regenerate buttons. An error shows a retry, not an empty bubble.
  6. Answers that state facts carry citations; uncited claims are flagged by a lightweight validator (X-5).
- **Metric:** Non-empty response rate ≥ 99%; p95 time to first token ≤ 3 s; thumbs-up rate.
- **Priority / Phase / Size:** **P0** (parser) · 0 · S; consolidation P1 · 1 · M

#### VW-09: Alpha Scanner
- **Job (claimed):** Filter assets by "physical premium" and "mirror accuracy".
- **Today:**
  - Prices try Yahoo, then Stooq, then a synthetic fallback, with **no flag saying which**.
  - Every metric (premium, mirror accuracy, signal) is **a sine/cosine of the clock**.
  - Default filters (premium ≥ 2, accuracy ≥ 90) return **0 results** about 60% of the time. The metrics oscillate with the clock, so the count changes from minute to minute (QA-038).
  - Calls `localhost:8000/api/v1/...`, which is also unreachable through nginx (QA-020, QA-021).
- **Decision:** Hide now. In Phase 2, Rebuild on real inputs:
  - Premium = physical benchmark minus futures, from a licensed or customer-provided feed.
  - Mirror accuracy = the historical hit rate of Mirror snapshots versus outcomes.
- **Requirements (when rebuilt):**
  1. Each metric has a defined formula and data source, shown in a tooltip.
  2. A price source and as-of time appear on every row.
  3. Defaults return results.
  4. Clicking a row opens the asset with a "Run forecast" action.
- **Priority / Phase / Size:** P2 · 2 · M

#### VW-10: Security
- **Job:** Let the Ops/Security Lead manage access and review the audit trail. This is a pilot requirement.
- **Today:**
  - Static service list and audit log.
  - LOCKDOWN_MODE does nothing.
  - The backend security router (API keys, IP allowlist, audit logs) **exists but is not mounted** (QA-023).
- **Decision:** Rebuild on the real router.
- **Requirements:**
  1. **API keys:** create, list, revoke, with expiry enforced and last-used tracked.
  2. **IP allowlist:** applies to all auth methods and respects `X-Forwarded-For` from trusted proxies.
  3. **Audit log viewer:** filter by user, action and date; export to CSV; covers all X-4 events.
  4. **Users and roles admin** (with SV-01).
  5. **Lockdown:** a real emergency switch that disables generation and any connectors, with an audit entry.
- **Metric:** 100% of sensitive actions present in the audit log (verified by test); time to revoke a key < 1 minute.
- **Priority / Phase / Size:** P1 · 1 · M

#### VW-11: Config
- **Job:** Workspace configuration.
- **Today:**
  - An "ACCESS_RESTRICTED / MODULE_DECRYPTION_IN_PROGRESS" placeholder, **shown to admins too** (QA-042).
  - The real settings live in the gear modal (GC-06).
  - No surface exists for self-service account management. Logout lives only inside the gear modal.
- **Decision:** Rebuild as **Settings**, merging the gear modal.
- **Requirements:**
  1. Settings has four sections:
     - Workspace: name, timezone, default assets, and the trusted-source allowlist (SV-19).
     - Models: active local model, critic provider, and per-feature overrides. Server-side, admin only.
     - Integrations: Alpaca, data feeds, with server-side encrypted credentials and a "Test connection" button.
     - Account: profile, change password, my API keys, and active sessions with revoke.
  2. Every change is audited.
  3. Non-admins see a read-only view, except their own Account section, which they can edit.
- **Priority / Phase / Size:** P2 · 2 · M

#### VW-12: Asset detail (`/dashboard/assets/[id]`)
- **Job:** One page per commodity that brings together prices, news, recent runs and memos, the Mirror view and positions. *Persona:* PM/Trader, Head of Risk.
- **Today:**
  - Doesn't exist. SV-08 #5 (news panel), VW-09 #4 ("opens the asset"), VW-01f ("Open in Mirror") and VW-02 #3 (exposure to assets with runs) all send users to it, but no card, route or nav entry owns it.
- **Decision:** Fix (a new view built from existing components).
- **Requirements:**
  1. The route is `/dashboard/assets/[id]` (X-7).
  2. Price series with source and as-of time (SV-03).
  3. Latest runs and memos for the asset (VW-01c), with a "Run audited forecast" action.
  4. A news panel using the existing `NewsFeed` component (SV-08 #5).
  5. The latest Mirror snapshot and its divergence panel (VW-07 #7).
  6. Positions in the asset, when a position source is connected (VW-02).
- **Priority / Phase / Size:** P2 · 2 · M

#### VW-13: Track record and calibration
- **Job:** Show how accurate past forecasts were, so the Head of Risk has a measured reason to trust new ones. *Persona:* Head of Risk, Quant Researcher.
- **Today:**
  - Doesn't exist. VW-01c #8 (record the outcome), SV-04 #8 (Brier), GC-03 (the Brier card links to "the underlying list") and the Phase 2 exit gate ("Brier reported weekly") all assume it.
  - No card says who resolves outcomes (manual entry or market resolution), or whether calibration feeds back into forecasts.
  - The patent's "Calibration Check" (`Patent.md`, detailed description §1: dampen over-confident probabilities using historical Brier scores) has no card.
- **Decision:** Fix (new).
- **Requirements:**
  1. A resolution queue lists runs whose question has resolved or is due. Outcomes come from market resolution where one exists, otherwise from manual entry by a `risk_manager`. Every entry is audited (X-4).
  2. Brier score and a reliability diagram per category and per model.
  3. Critic-override outcomes: how often the override turned out right.
  4. **Phase 3:** per-category calibration dampening, per `Patent.md` §1.
- **Metric:** % of resolvable runs with a recorded outcome; weekly Brier trend per category.
- **Priority / Phase / Size:** P2 · 2 · M; dampening (#4) P3 · 3

### 5.3 Global components

#### GC-01: Sidebar navigation and role gating
- **Today:**
  - Nav items are `div`s, so 0 are keyboard-focusable (QA-045).
  - Six of the seven "locked" items still navigate, to a placeholder. The locked Agent Builder item does nothing.
  - "Documentation" is dead.
  - "API_LATENCY 12ms" is static.
  - No user identity or logout.
- **Decision:** Fix.
- **Requirements:**
  1. Items are `<Link>`s to `/dashboard/<view>` with `aria-current`.
  2. Items the role cannot use are **hidden**, not teased. Feature-flagged items are hidden (PL-08).
  3. A user block shows name, role and logout.
  4. Latency is real (from GC-04) or removed.
  5. Documentation links to the user-facing methodology and help (PL-05 #2). Until that ships in Phase 2, the link is hidden.
- **Priority / Phase / Size:** P1 · 1 · M

#### GC-02: Ticker tape and chart modal
- **Today:**
  - Static prices (BTC $42,105, etc.) in a continuously scrolling marquee. It pauses on hover (`ticker.tsx:98`) but ignores `prefers-reduced-motion`. Items are click-only `div`s that keyboard users cannot reach (QA-048).
  - The chart modal shows `Math.random()` data labeled "LIVE_CHART".
- **Decision:** Hide in pilot mode. Later, Wire to SV-03 prices for the user's watchlist, with a real intraday series in the modal.
- **Requirements (when wired):** Keep pause on hover; respect `prefers-reduced-motion`; show source and as-of in the modal.
- **Priority / Phase / Size:** P2 · 1 (hide) / 2 (wire) · S

#### GC-03: Stat cards
- **Today:**
  - Four hardcoded KPIs.
  - "Compute Health 88.5%" is **permanently red with "CRITICAL LAG DETECTED"** (QA-030).
  - Trend chips are static.
- **Decision:** Rebuild as **real product KPIs**:
  - Runs today, with completion rate
  - Critic pass / flag / veto split
  - p95 run latency
  - Rolling 30-day Brier score (once outcomes exist)
- **Requirements:**
  1. Each card links to the underlying list.
  2. Threshold colors come from defined SLOs.
  3. A card with no data shows "—", never a made-up value.
- **Priority / Phase / Size:** P1 · 1 · S

#### GC-04: System status dropdown
- **Today:**
  - Polls `/health` every 15 s, but shows "SYSTEM_OPTIMAL" even when the backend says `degraded` (QA-028).
  - Down dependencies get a red dot, but their OFFLINE / DEGRADED / DISCONNECTED label stays green.
  - "NEURAL_ENGINE_ACTIVE" and the latency numbers are static.
  - Renders under the stat cards (QA-029).
- **Decision:** Fix.
- **Requirements:**
  1. Overall state is derived from the backend's `status`. Each dependency is marked **required** (DB, Redis, worker, LLM) or **optional** (Gemini, data feeds).
  2. Real per-dependency latency is measured by `/health`.
  3. A "checking…" state shows before the first poll.
  4. Correct z-index.
- **Priority / Phase / Size:** P1 · 1 · S

#### GC-05: Notification center
- **Today:** 4 hardcoded alerts, including a fake "Critical Margin Alert". Read state isn't persisted. "View Archive" does nothing. The popover is unreadable (QA-029).
- **Decision:** Rebuild on real events.
- **Requirements:**
  1. A backend `notifications` table, filled by events: run complete or failed, critic veto, Mirror divergence above threshold, system degraded, key expiring.
  2. Read, dismiss and archive are persisted per user.
  3. Delivered over the existing WebSocket. Optional email/Slack later.
- **Priority / Phase / Size:** P2 · 2 · M

#### GC-06: Settings modal (gear)
- **Today:**
  - Stores Alpaca keys and a Gemini key in **plaintext localStorage**.
  - The llama.cpp URL and Gemini key are never used.
  - Model selection is read by only 3 components (Analyst Chat, the Discuss-findings panel, and the status dropdown label), and only Analyst Chat's `/chat/stream` actually uses it; `/chat` overrides it with `lfm-thinking`, and forecasts never send it.
  - No save feedback (QA-040).
  - The "Demo Controls" role switch is tied to a hardcoded email.
- **Decision:** Rebuild. Move everything server-side (VW-11). The gear keeps **personal preferences only**: theme density, default persona, notification preferences.
- **Requirements:**
  1. No secrets in the browser.
  2. Saving shows a toast and closes the dialog.
  3. Delete the role-toggle demo control.
- **Priority / Phase / Size:** P1 · 1 · M

#### GC-07: Sidebar chat (global copilot)
- **Today:**
  - Empty reply bubble (QA-009).
  - Its close button overlaps the Send button (QA-044).
  - Shown on landing and login.
  - Fixed 400 px width.
- **Decision:** Fix (parser, P0) and Merge into the single chat component (VW-08). Show it only when authenticated, with the current route and selected asset as context.
- **Priority / Phase / Size:** **P0** (parser) · 0 · S; merge P1 · 1 · S

#### GC-08: Wallet connect
- **Today:**
  - The WalletConnect `projectId` is a placeholder (RainbowKit swaps in its shared example ID), and the wallet connectors open relay WebSockets on every page, which threw **uncaught errors on every page** when the relays were unreachable (QA-047).
  - No feature uses the wallet.
  - The app name is "Polymarket Hedge Fund".
  - Wallet libraries are a large share of the 589 kB dashboard bundle.
- **Decision:** Cut. Browser-wallet signing doesn't fit a privacy-first institutional ICP, and trade execution is out of MVP scope. Remove `wagmi`, `viem` and `@rainbow-me/rainbowkit`.
- **Metric:** 0 console errors on page load; dashboard first-load JS reduced. Target < 350 kB.
- **Status:** Done in `8f7f518`. The wallet stack is removed; page loads open no wallet connections, and `/dashboard` transfers 236 kB of JavaScript (820 kB before, measured the same way).
- **Priority / Phase / Size:** P1 · 1 · S

### 5.4 Backend capabilities

#### SV-01: Authentication and identity
- **Today:**
  - 4 in-memory users with trivial passwords (QA-006).
  - JWT signed with a **hardcoded default secret**; forged admin tokens are accepted (QA-005).
  - `ACCESS_TOKEN_EXPIRE_MINUTES` is ignored.
  - No refresh, revocation, lockout, or `/auth/me`.
  - `ALLOW_DEMO_AUTH` turns anonymous callers into admin, with a personal email hardcoded.
- **Decision:** Rebuild.
- **Requirements:**
  1. **P0**
     - The app refuses to start if `SECRET_KEY` is unset or a known placeholder.
     - Add `GET /auth/me`.
     - Read the token TTL from env.
     - Remove the default users from code; seed one admin from env on first boot.
     - `ALLOW_DEMO_AUTH` is allowed only when `ENV=dev` and maps to a non-admin `demo` role.
  2. **P1:** `users` table (hashed passwords, role, disabled), refresh tokens with revocation, lockout and rate limit on `/auth/token`, password reset.
  3. **P2:** OIDC SSO; SCIM-lite provisioning for pilots.
- **Priority / Phase / Size:** **P0** · 0–2 · L

#### SV-02: RBAC, API keys, IP allowlist, audit log
- **Today:**
  - The security router is not mounted (QA-023).
  - RBAC is enforced only on `/trade/execute`. `/tools/call` (which places orders) has none (QA-011).
  - `risk_manager` is unused. Audit logging (`core/audit.py`) is called only from the unmounted security router (API-key and allowlist changes), so no audit event is ever written.
  - A `127.0.0.1` entry in a user's allowlist lets that user's API keys be used from any IP, and the allowlist is checked only for API-key auth, never for JWTs.
  - API key `expires_at` is never checked.
- **Decision:** Fix.
- **Requirements:**
  1. Mount the router and write a role × endpoint matrix as code (one dependency per route). Default: deny.

     | Role | Can |
     | --- | --- |
     | `analyst` | run forecasts, chat |
     | `trader` | everything `analyst` can, plus Mirror and positions (read-only) |
     | `risk_manager` | everything `trader` can, plus critic override, audit view |
     | `admin` | everything, plus settings, keys, users |

  2. Audit every X-4 event, in the same transaction as the action.
  3. Fix the allowlist bypass. Enforce key expiry and update `last_used_at`.
- **Metric:** RBAC test matrix 100% green. 0 sensitive actions missing from the audit log.
- **Priority / Phase / Size:** **P0** · 0–1 · M

#### SV-03: Markets data service
- **Today:**
  - `/markets` returns a static list of 6 items (cached 30 s per user).
  - `/markets` never reads the `polymarket_markets` table; only `/demo/analyze` (QuantAgent) reads it, and nothing reachable writes to it.
  - Connectors exist but aren't scheduled.
  - `ScrapingAgent` can already write Polymarket markets and order-book snapshots (`polymarket_markets`, `polymarket_orderbook`), but nothing reachable calls it.
  - A second, unvalidated generate-and-critique loop (`InsightAgent` → `CriticAgent` → `market_insights`) and `orchestrator.plan_and_execute` (hardcoded equity tickers) are never called. The README still advertises this "Critic review loop".
- **Decision:** Wire.
- **Requirements:**
  1. A scheduled ingestion job writes markets and prices into Postgres:
     - Commodity reference prices from one licensed or free source chosen with pilots.
     - Polymarket/Kalshi markets on commodity themes as **signal inputs**.
  2. `/markets` reads from the database with `source`, `as_of`, `unit` and `type` (`price` | `probability`).
  3. Every price-shaped UI element (VW-01, GC-02, VW-09) uses this one service.
  4. Reuse `ScrapingAgent` as the scheduled Polymarket ingestion job (PL-09). Keep its order-book snapshots for the VW-01e depth chart.
  5. Cut `InsightAgent`, `CriticAgent`, `plan_and_execute` and the `market_insights` table. Drop the README's "Critic review loop" claim with them (PL-05 #1).
- **Metric:** Data freshness SLO (≤ 5 min for intraday sources); ingestion job success ≥ 99%.
- **Priority / Phase / Size:** P1 · 1 · L

#### SV-04: Forecast pipeline (Celery + swarm + lifecycle WebSocket)
- **Today:**
  - **The happy path works when the model returns JSON**: about 1 s with the emulator, giving `0.58 → 0.61` after the critic.
  - The WebSocket crashes (QA-008).
  - Failures report `completed` (QA-015).
  - The cache is never written (QA-016).
  - Unknown task IDs stay `processing` forever (QA-017).
  - No ownership check (QA-018).
  - The user's model choice is ignored.
  - Physical data is synthetic but attributed to real vendors (QA-027).
  - Swarm labels are mismatched (QA-026).
  - Runs aren't persisted.
  - Every run also makes an unstructured "semantic correlations" LLM call and appends its output to the reasoning under "Secondary Correlations Discovered", with no schema, citations or Critic review. This is a patent-claimed capability (`Patent.md` §4) with no keep or cut decision.
- **Decision:** Fix.
- **Requirements:**
  1. **Lifecycle:** async Redis pub/sub WebSocket with an authenticated subscribe; statuses `queued|running|complete|failed` with error codes; Celery `autoretry` on transient errors only.
  2. **Results:** persisted to `forecast_runs` (VW-01c); cache keyed by `(question, model, data as-of)` with a TTL; GET is ownership-checked.
  3. **Inputs:**
     - Physical data either comes from a real feed or is labeled `SYNTHETIC` in both source title and URL scheme. Never use real vendor names for synthetic data.
     - Fix the `"sovbean"` typo.
  4. **Swarm:** output keys named for what they are (`geopolitical`, `supply_chain`, `derivatives`, `synthesis`); scores clamped to [0, 1].
  5. **Model routing:** honor the requested model via an allowlist; fall back explicitly and record which model actually ran.
  6. **Fallback prompt:** the JSON fallback uses a full instruction prompt, not just the bare question.
  7. **Evaluation:** the reference question set runs nightly against the configured model (PL-04).
  8. **Outcomes:** resolution capture feeds a Brier score per category (the YC plan's quality metrics), shown in VW-13.
  9. **Linked markets (P2):** either make semantic correlations a structured `linked_markets[]` field that the Critic reviews and the memo shows (VW-01c), or Cut the call until VW-05 is rebuilt.
- **Metric:** Completion rate ≥ 95%; p95 ≤ 30 s; % of runs with ≥ 3 real sources; weekly Brier score.
- **Priority / Phase / Size:** **P0** (1–2, 5) · 0; #9 P2 · 1 · S; rest P1 · 1 · L

#### SV-05: Critic verification
- **Today:**
  - Uses Gemini when a key is set, otherwise Ollama, which compose doesn't run (QA-054). So in the default stack the Critic is **always unavailable**, and users see the raw exception text.
  - The Gemini adapter uses the legacy `gemini-pro` endpoint, and its error handling can expose the server's Gemini key to users and logs (QA-024).
  - Adversarial fields are never requested (QA-025).
  - The "trusted whitelist" verification promised in ARCHITECTURE.md doesn't exist.
  - Three critic implementations exist (one live, one duplicate used only by tests, one batch agent).
- **Decision:** Fix.
- **Requirements:**
  1. **Provider:**
     - Default to a **local** critic on the llama.cpp server (privacy first).
     - Gemini is opt-in per workspace, uses a current model, and passes the key in a header.
     - Errors are mapped to safe messages; never echo raw exceptions or URLs.
  2. **Schema:** `critique`, `score`, `verdict (pass|flag|veto)`, `risk_factors[]`, `counter_arguments[]`, `logical_fallacies[]`, `unsupported_claims[]`. Enforced with JSON-schema / GBNF (backlog FEAT-008, FEAT-CRITIC-001).
  3. **Source check:** every claim is matched to a source; claims from non-allowlisted domains are flagged (the "hallucination firewall").
  4. **Veto semantics:** a vetoed run cannot be exported as a memo without a `risk_manager` override plus rationale.
  5. Delete the duplicate critics and test the live one.
- **Metric:** Critic availability ≥ 99% of runs; critic pass rate; override rate; % of unsupported claims caught on a labeled test set.
- **Priority / Phase / Size:** **P0** (1, safe errors) · 0; rest P1 · 1 · M

#### SV-06: Chat service
- **Today:**
  - The llama.cpp stream parser expects raw JSON lines, so responses are empty against a real server (QA-009).
  - SSE JSON is hand-escaped, missing control characters.
  - `context`, persona and client history are ignored.
  - The DB session is held for the whole stream.
  - The `embedding` column is never written.
- **Decision:** Fix.
- **Requirements:**
  1. Parse `data:` SSE frames, stopping on `stop: true`.
  2. Serialize SSE with `json.dumps`.
  3. Short DB transactions before and after the stream; on failure, persist an error marker and emit an `error` event.
  4. Conversations table; context grounding (VW-08); persona → system prompt.
  5. Optional embeddings for semantic history search (Phase 2).
- **Priority / Phase / Size:** **P0** (1–3) · 0 · S; rest P1 · M

#### SV-07: Mirror service
- See **VW-07** for requirements.
- **Backend specifics:**
  - Add auth.
  - Target CRUD tables: `mirror_targets`, `mirror_snapshots`.
  - Replace `duckduckgo_search` with a pinned `ddgs` package (search already runs in `asyncio.to_thread`).
  - Keep Mirror's LLM calls on the shared `ai_client` (already done via `infrastructure/llm.generate_text`, which closes the YC plan's "Unify inference access" item).
  - The Critic reviews each snapshot.
- **Priority / Phase / Size:** P1 · 1 · M

#### SV-08: News and sentiment (FinBERT)
- **Today:**
  - `/intelligence/news` is unauthenticated.
  - It parses 3 RSS feeds synchronously inside an async route; the Reuters feed is dead.
  - FinBERT (about 440 MB) loads **at import**. With no network it fails silently and every item becomes neutral 0.0.
  - The UI never calls it; `NewsFeed.tsx` and `NarrativeDivergence.tsx` are unused.
- **Decision:** Fix and Wire, **as an input to forecasts and Mirror** rather than a standalone feed.
- **Requirements:**
  1. Lazy-load the model in the worker, not the API. Bake the model into the image or a cache volume.
  2. A scheduled feed-ingestion job stores items with sentiment in `news_documents`, which already has a vector column.
  3. Choose a configurable feed list with pilots.
  4. Forecast and Mirror retrieve the relevant recent news as cited sources.
  5. Expose a news panel in the asset detail view (VW-12) using the existing `NewsFeed` component.
- **Priority / Phase / Size:** P2 · 2 · M

#### SV-09: Scanner service
- See **VW-09**.
- **Backend specifics:**
  - Move under `/scanner` so it works through nginx (QA-021).
  - Add auth.
  - Cache prices.
  - Return `price_source`.
  - Replace all time-based synthetic metrics.
- **Priority / Phase / Size:** P2 · 2 · M

#### SV-10: Strategy generation and sandbox backtest
- **Today:**
  - `/strategy/generate` is unauthenticated and returns LLM prose as code.
  - The fallback triggers on the substring "Error", which matches valid code containing `ValueError`.
  - The sandbox runs `exec()` as root with no limits and isn't wired to anything.
  - No backtest endpoint.
- **Decision:** Hide. Disable the endpoint unless `FEATURE_STRATEGY_LAB` is on (PL-08). Build in Phase 3 per VW-06, including the decision on the existing `strategies/` package format.
- **Security gate before enabling:**
  - gVisor or Firecracker isolation, or at minimum a non-root user with seccomp, no network, a read-only filesystem, and CPU/memory/time quotas.
  - An allowlist of imports.
  - Code is reviewed by the Critic.
- **Priority / Phase / Size:** P3 · 3 · XL

#### SV-11: Trade execution and Kelly sizing
- **Today:**
  - `/trade/execute` returns an **unsigned placeholder** (`data: "0x095ea7b3...BRENT...buy"`, which echoes the request's symbol and side) with the wrong `value` semantics.
  - The Alpaca branch only returns a message.
  - Side and quantity are not validated (QA-014).
  - Kelly receives no inputs and returns at most one step (10 units).
  - The UI presents all of this as executed (QA-013).
  - A CLI script, `backend/scripts/demo_llm_polymarket_alpaca.py`, places Alpaca market orders from uncritiqued LLM output when run with `--execute`. It uses the server's env credentials, with no role check, Critic or audit, outside the `FEATURE_EXECUTION` gate. Its broker endpoint comes from `ALPACA_BASE_URL`.
  - `QuantAgent` (`/demo/analyze`) generates trade recommendations with no Critic.
- **Decision:**
  - **Phase 0:** Hide. Remove all trade buttons from the UI and disable the route behind `FEATURE_EXECUTION` (PL-08). Cut the order CLI script, or at least its `--execute` path. Cut `QuantAgent` with `/demo/*` (SV-14 #5).
  - **Phase 3:** Build paper-only execution, only if pilots ask for it.
- **Requirements (Phase 3):**
  1. Enum-validated side; positive quantity; per-user and per-asset limits.
  2. A pre-trade check requires a non-vetoed run less than N hours old.
  3. Explicit confirmation dialog; idempotency key; full audit trail.
  4. Correct fractional-Kelly sizing with tests on known cases.
- **Priority / Phase / Size:** **P0** (gate) · 0 · S; cut the order CLI and `QuantAgent` P1 · 0 · S; build P3 · XL

#### SV-12: Connectors (Polymarket, Kalshi, Alpaca, MCP)
- **Today:**
  - **Polymarket:** read-only and used only by unscheduled agents; probably reads the wrong token-ID field.
  - **Kalshi:** read-only, used only in tests.
  - **Alpaca:** real SDK, but synchronous calls block the event loop, and credentials fall back to server env.
  - **MCP:** entirely simulated (`"Simulated result"`), never registered.
- **Decision:** Fix (Polymarket and Kalshi as read-only signal sources for SV-03; Alpaca as read-only positions for VW-02/03). Cut the MCP stubs until a real MCP integration is scoped.
- **Requirements:**
  1. Async calls with timeouts and retries.
  2. Per-workspace credentials (GC-06).
  3. Connector health is reported in `/health`.
- **Priority / Phase / Size:** P1 (Polymarket/Kalshi) · 1; P2 (Alpaca) · 2 · M

#### SV-13: Tools API (`/tools/call`)
- **Today:** Any authenticated role, including `analyst`, can reach `place_market_order`. Credentials come from request headers or server env. No audit, no limits (QA-011).
- **Decision:** Fix now. Restrict to read-only tools (`get_account`, `list_positions`) for `trader`+; disable `place_market_order` behind `FEATURE_EXECUTION` (PL-08); audit every call.
- **Priority / Phase / Size:** **P0** · 0 · S

#### SV-14: Demo multi-agent RAG (`/demo/analyze`, `/demo/ingest_news`)
- **Today:**
  - **Unauthenticated database write** (QA-012).
  - Loads a 2 GB embedder at import.
  - Falls back to a constant vector, which makes retrieval meaningless.
  - Returns `status: success` even when the payload is an error.
  - `run_polymarket_pipeline` references a nonexistent attribute.
- **Decision:** Rebuild as **Document ingestion**. Customers upload their own research, notes or reports, which become cited sources in forecasts and Mirror. The YC plan's Q3 goal of "customer-provided inputs" fits here.
- **Requirements:**
  1. Authenticated upload (PDF, DOCX, TXT, URL) with per-workspace isolation.
  2. Chunking and embedding in the worker. Fail loudly when there is no embedder; never use constant vectors.
  3. Retrieval used by SV-04 and SV-07, with citations.
  4. Delete endpoint and retention policy.
  5. Remove `/demo/*`, and `QuantAgent` with it (SV-11).
- **Priority / Phase / Size:** P2 · 2 · L

#### SV-15: Cognitive replay (`rs_engine`)
- **Today:** A record/replay decorator that nothing uses; save and load do nothing; global mutable mode.
- **Decision:** Hide (keep the code). Wire it in Phase 3 as **deterministic run replay for audit**: given a run ID, replay the recorded LLM and tool I/O to reproduce the memo exactly. This is a strong audit-trail differentiator for the Head of Risk persona.
- **Requirements:** Persist recordings with the run (object storage); per-run, not global, mode; stable hashing.
- **Priority / Phase / Size:** P3 · 3 · M

#### SV-16: Health, logging, telemetry
- **Today:**
  - `/health` always returns HTTP 200 and is `degraded` whenever Gemini is unset.
  - It doesn't check the worker or migrations.
  - JSON request logs exist. The only run-level events are ephemeral Redis pub/sub progress messages from the worker (`status`, `complete`, `failed`; `worker.py:22-48`). They are never logged or stored, and the WebSocket that should relay them crashes (QA-008). The YC plan's event model isn't implemented.
  - `GET /intelligence/status` (FinBERT model status) is a separate, unauthenticated endpoint.
  - No alert channel, error tracker or frontend product events exist, although several cards require alerts and §7 measures adoption from events.
- **Decision:** Fix.
- **Requirements:**
  1. Separate `/health/live` and `/health/ready`. Ready checks DB plus migrations, Redis, worker heartbeat and LLM; optional dependencies are reported but not failing.
  2. Each run emits the YC plan's canonical events (`analysis_requested`, `analysis_started`, `analysis_completed`, `analysis_failed`, `critic_completed`, `critic_overruled`, `export_created`, `share_link_created`), plus step-level events such as `sources_gathered` and `forecast_done`.
  3. Request IDs propagate from nginx to the API, the worker and the logs.
  4. Basic dashboards: run volume, failure reasons, latency percentiles.
  5. **Alerting and error tracking (P1):** failed or overdue jobs (PL-09), critic unavailability, readiness failures and fail-open rate limiting (SV-17 #3) reach an alert channel. Backend and frontend exceptions go to an error tracker.
  6. **Product events (P2):** privacy-safe frontend events feed the §7 adoption KPIs (weekly active users, activation within 7 days, memo exports).
  7. **FinBERT status (P2):** fold `/intelligence/status` into `/health/ready` as an optional dependency, then remove the endpoint.
- **Priority / Phase / Size:** P1 · 1 · M; #6 P2 · 2 · S; #7 P2 · 1 · S

#### SV-17: Rate limiting and caching
- **Today:**
  - The rate limit is keyed on client IP, so behind nginx it is a single **site-wide** bucket of 6 per minute (QA-019).
  - It only covers `/predict` and returns 500 on Redis errors.
  - Redis is used synchronously inside async code.
- **Decision:** Fix.
- **Requirements:**
  1. Per-user and per-API-key limits on every expensive route, with a sliding window.
  2. Async Redis.
  3. Fail open with an alert for reads; fail closed for login.
  4. Separate Redis databases or prefixes for Celery and the cache.
- **Priority / Phase / Size:** P1 · 1 · S

#### SV-18: Workspaces and tenancy
- **Job:** Keep each customer's users, credentials, documents and settings separate. *Persona:* Ops/Security Lead, Head of Risk.
- **Today:**
  - No workspace or organization model exists. Users are 4 in-memory records (QA-006), and no table has a workspace key.
  - VW-03 #1, VW-11, SV-12 #2, SV-14 #1, D-5 and R-1 all say "per workspace", but the PL-03 table list had no `workspaces` table.
  - No decision says whether a pilot is a single-tenant deployment per customer or a multi-tenant service (D-10).
- **Decision:** Rebuild (new).
- **Requirements:**
  1. `workspaces` and `memberships` tables (PL-03). Each user belongs to at least one workspace, and roles (SV-02) are held per membership.
  2. Every customer-data table carries `workspace_id`, and every query is scoped by it.
  3. Workspace admins invite members and manage seats (the YC plan's "seat expansion support"). Invites and role changes are audited (X-4).
  4. The deployment model follows D-10.
- **Metric:** 0 cross-workspace reads in an isolation test suite.
- **Priority / Phase / Size:** P1 · 1–2 · M

#### SV-19: Source retrieval and provenance
- **Job:** Feed the "sources" step of the core loop with dated, attributable sources from a provider an institutional buyer can rely on. *Persona:* Head of Risk, PM/Trader.
- **Today:**
  - Forecast sources are the top 10 text results from the unofficial `duckduckgo_search` package (`intelligence/infrastructure/search.py`). There is no API key, SLA, publish date, dedupe or recency filter.
  - SV-07 covers the `ddgs` rename for Mirror only. SV-05 #3 flags non-allowlisted domains, but no card owns the allowlist.
  - VW-01c #2 needs a publisher and timestamp for each citation, which these results don't carry.
- **Decision:** Rebuild.
- **Requirements:**
  1. Choose a licensed search or news API with pilots, behind one search interface used by forecasts (SV-04) and Mirror (SV-07).
  2. A normalized `Source` schema: URL, publisher, `published_at`, `retrieved_at` and a content hash. Duplicates are merged, and the recency window is configurable.
  3. A trusted-domain allowlist with full create/read/update/delete in Settings (VW-11), per workspace (SV-18). SV-05 #3 checks claims against it (the YC plan's "provenance policies and source controls").
  4. Every source used by a run is stored in `run_sources` (PL-03) with this schema.
- **Metric:** % of citations with publisher and publish date; source retrieval success rate.
- **Priority / Phase / Size:** P1 · 1 · M

#### SV-20: Physical-market data feeds
- **Job:** Give forecasts and the Mirror a real physical-market view (shipping/AIS, satellite, inventories, weather) to compare narratives against. The vision says the target fund's edge comes from understanding physical market dynamics. *Persona:* PM/Trader, Head of Risk.
- **Today:**
  - Only `MockPhysicalDataProvider` exists (`intelligence/infrastructure/physical_data.py`), and its data is synthetic (QA-027).
  - SV-04 #3 says to use a real feed or label the data `SYNTHETIC`, and R-2 notes licensing, but no card scopes choosing, integrating or pricing a feed.
  - BACKLOG STRAT-002 ("Data Integration") had no plan card.
- **Decision:** Wire.
- **Requirements:**
  1. Pick one feed with the first pilot (R-2) and integrate it behind the existing `PhysicalDataInterface`.
  2. Every data point carries a source, as-of time and unit, and is cited like any other source (SV-19).
  3. Ingestion runs as a scheduled job (PL-09).
  4. The Mirror divergence panel (VW-07 #7) compares narratives against this feed.
- **Priority / Phase / Size:** P2 · 2 · L

#### SV-21: Prompt registry
- **Job:** Make every prompt a versioned, reviewable artifact, so runs can be reproduced and eval regressions traced to a prompt change. *Persona:* engineers; Head of Risk (audit).
- **Today:**
  - Prompts are inline strings spread across forecasting, the swarm, two critic implementations, `QuantAgent`, `InsightAgent`, strategy generation and chat. This breaks AGENTS.md rule 4 ("No magic strings").
  - VW-01c #5 asks for a prompts hash per run, and SV-15 needs deterministic replay, but no card owns centralizing prompts.
- **Decision:** Fix.
- **Requirements:**
  1. Prompts live in files with an ID and a version.
  2. Each run records the IDs, versions and hash of the prompts it used on `forecast_runs` (VW-01c #5).
  3. Chat persona prompts (VW-08 #3) come from the registry.
  4. Nightly evals (SV-04 #7) report results per prompt version.
- **Priority / Phase / Size:** P1 · 1 · S

#### SV-22: Public API
- **Job:** Give the Quant Researcher a stable, versioned, documented API with scoped keys. *Persona:* Quant Researcher, Ops/Security Lead.
- **Today:**
  - `routers/prediction.py` also mounts a `compat_router` with a second `POST /predict` and `GET /task/{id}`, so every prediction route exists twice and needs RBAC and rate limits twice.
  - API-key access (`X-API-Key`) exists, but keys have no scopes and the API isn't treated as a product surface.
  - `/docs`, `/redoc` and `/openapi.json` are served in every environment, and the README links to them, although X-3 limits docs to dev.
  - The YC plan's stabilization item ("make the public contract unambiguous") has no card.
- **Decision:** Fix, and Cut the compat routes.
- **Requirements:**
  1. **P1, Phase 0:** Cut the compat routes.
  2. Version the API under `/v1`.
  3. Scoped API keys (`read`, `forecast`), managed in VW-10.
  4. Docs are served only where the environment allows. The README matches.
- **Priority / Phase / Size:** P1 (#1) · 0 · S; rest P2 · 2 · S

### 5.5 Platform

#### PL-01: Runtime and deployment
- **Today:**
  - The API doesn't boot (QA-001, QA-002).
  - Compose builds a **mock LLM** while downloading a real GGUF it never serves (QA-010).
  - No Ollama, although the Critic defaults to it.
  - nginx lacks WebSocket and SSE settings (QA-052).
  - Postgres (trivial default password), Redis (no auth), the API (8000, with a seeded admin user on a trivial default password) and the LLM (8080, no auth) are published on host ports (QA-051).
  - Backend runs with `--reload` and a bind-mounted source tree.
  - `run.sh` copies `.env.example` verbatim, so a fresh install runs with its placeholder `SECRET_KEY` and a placeholder `GEMINI_API_KEY` that makes health report Gemini as configured. It prints a stale "~5GB" download estimate and then tails logs forever.
  - `.env.example` uses the wrong variable names (`ALPACA_SECRET`, `KALSHI_SECRET`) and the wrong LLM host, and omits `ALLOW_DEMO_AUTH`, `ALPACA_BASE_URL` and `KALSHI_KEY_ID`. The README asks for `POLYMARKET_*` keys that no code reads (QA-050).
  - Two contradictory model bootstraps exist. The top-level `setup_model.sh`, `Modelfile` and `Modelfile.local` target OpenForecaster-8B on Ollama, while compose runs `backend/setup_model.sh` (LFM2.5-1.2B) into a volume still named `ollama_downloads`.
  - There is no offline profile. The build and runtime fetch fonts, models, search results and feeds from the internet. Offline, the model loads fail silently (QA-033).
- **Decision:** Fix.
- **Requirements:**
  1. **P0:** Fix the circular import and the `async_session` and `sentence-transformers` issues. CI asserts that `uvicorn app.main:app` imports cleanly.
  2. **P0:** `text-gen-cpp` runs a real llama.cpp server image mounting the downloaded GGUF. The mock moves to a `docker-compose.test.yml` profile. **P1:** Pick one reference model (D-7) and keep a single setup script. Cut `Modelfile`, `Modelfile.local`, the top-level `setup_model.sh` and the `ollama_downloads` naming.
  3. **P0:** nginx adds `Upgrade`/`Connection` headers for `/api/ws/` and `proxy_buffering off` for SSE routes.
  4. **P0:** Stop publishing Postgres, Redis, the LLM and the 8000/3000 ports on all host interfaces (remove the `ports:` entries or bind them to localhost), require a Redis password and a generated Postgres password, and drop `--reload` and source bind-mounts outside dev (QA-051). **P1:** Split `docker-compose.yml` (prod-like: no published DB/Redis/LLM ports, no reload, non-root users, healthchecks) from `docker-compose.dev.yml`.
  5. **P1:** Pin a reference hardware profile and model quantization; publish expected p95 latency.
  6. **P0:** `run.sh` generates random secrets on first run instead of copying placeholders, so SV-01's placeholder check doesn't break the one-command install. The backend validates its environment at boot with a pydantic-settings schema. `.env.example` lists exactly the variables the code reads. The README drops the `POLYMARKET_*` instructions.
  7. **P2:** An offline profile for on-prem or VPC pilots: self-hosted fonts, models baked into images or volumes, an egress allowlist, and a documented list of outbound dependencies.
- **Priority / Phase / Size:** **P0** (#1–3, #4 port lockdown, #6) · 0 · M; the compose split (#4), #5 and the single model (#2) P1 · 0–1; offline profile (#7) P2 · 2 · M

#### PL-02: Secrets, repository visibility and security hygiene
- **Today:**
  - A TLS private key, a JWT RSA private key, a SQLite database and access logs are **committed** (QA-007).
  - A public server IP is in the nginx config.
  - The repository is public. It holds the patent text (`Patent.md` and a PDF), the committed keys above and the QA report's security findings, while the README says "Proprietary & Confidential".
  - CORS is `*` with credentials.
  - The global error handler returns `str(exc)` to clients.
- **Decision:** Fix.
- **Requirements:**
  0. **P0, decide today:** repository visibility (D-9). Make the repository private, or scrub the patent text and the QA security findings from the tree and history. Align the README license line with the choice.
  1. **Rotate** every committed key and certificate. Remove `nginx/data/`, `nginx/certs/server.key` and `backend_logs.txt` from the tree **and from git history**. Add them to `.gitignore`. Rotation doesn't secure a server that is already running this code; PL-10 covers that.
  2. Enable GitHub secret scanning and push protection.
  3. CORS limited to configured origins.
  4. The error handler returns a generic message plus a request ID; details go to logs only.
  5. Write a lightweight threat model for the pilot (one page). **P2:** Extend it into a **pilot trust pack**: retention per table (chat, runs, audit log, documents), deletion on request, audit-log retention and immutability rules, a sub-processor list (including Gemini when enabled), and a DPA template.
  6. No placeholder secret survives an install: `run.sh` generates them (PL-01 #6).
- **Priority / Phase / Size:** **P0** · 0 · S; trust pack (#5) P2 · 2 · S

#### PL-03: Data layer and migrations
- **Today:** No Alembic revisions. Tables come only from a manual `init_db.py`, which fails on a fresh database without `CREATE EXTENSION vector`. No users, runs or conversations tables.
- **Decision:** Fix.
- **Requirements:**
  1. Write a baseline Alembic migration that includes `CREATE EXTENSION IF NOT EXISTS vector`. Migrations run automatically in an init container.
  2. New tables:
     - `users`
     - `workspaces` and `memberships` (SV-18)
     - `forecast_runs`
     - `run_sources`
     - `memos`
     - `conversations`
     - `mirror_targets`
     - `mirror_snapshots`
     - `notifications`
     - `outcomes`
  3. Backup and restore runbook.
- **Priority / Phase / Size:** **P0** (baseline) · 0; new tables per feature, P1 · M

#### PL-04: QA automation and CI
- **Today:**
  - Backend: 46 passed, 2 failed, 1 module fails to import. Tests hit the network. Test dependencies (`pytest`, `pytest-asyncio`, `aiosqlite`) are missing from requirements, and `torch` is a heavy mandatory install.
  - E2E: 4 of 6 failing, stale since the login gate.
  - No CI at all.
- **Decision:** Fix.
- **Requirements:**
  1. GitHub Actions on every PR: frontend `tsc`, lint and build; backend `pytest` with **no network**, using `requirements-dev.txt` and with ML dependencies mocked or made optional; an import-smoke test of `app.main`.
  2. A contract test for llama.cpp streaming using a recorded fixture (guards QA-009).
  3. A compose-based E2E smoke test: login → watchlist → run forecast → result rendered → memo exported. Plus the RBAC matrix test (SV-02).
  4. Visual regression snapshots for each view (catches QA-029-type bugs).
  5. The regression gates in [QA report §8](QA_TEST_REPORT.md#8-recommended-regression-gates) are mandatory before any pilot demo.
- **Priority / Phase / Size:** **P0** · 0 · M

#### PL-05: Docs and narrative honesty
- **Today:**
  - The README implies `lfm-thinking` is served.
  - `frontend.md` lists React Query and Recharts, which aren't installed.
  - ARCHITECTURE.md describes a whitelist Critic that doesn't exist.
  - The YC plan's Q2 status is outdated.
  - The README advertises a "Critic review loop" over stored market insights that nothing runs (SV-03).
  - Only developer docs exist. No user-facing guide explains the critic score, the verdicts, swarm components, scanner formulas, or what `DEMO` means.
  - The patent text claims automated prediction-market execution, slippage-aware Kelly sizing and a trusted-whitelist critic, while D-1 and D-2 make the product commodities-first with no execution. A third-party arXiv paper is committed as a PDF.
- **Decision:** Fix. Update the docs as each P0 or P1 lands. Add a "What's real vs. demo" table to the README (MGMT-002). Treat this plan and the QA report as living documents, refreshed after each phase.
- **Requirements:**
  1. Drop the README's "Critic review loop" claim.
  2. **P2:** A methodology page and in-app help explain the critic score, the verdicts (pass / flag / veto), swarm components, scanner formulas and the `DEMO` label. GC-01 #5 and the VW-09 tooltips link to it.
  3. **P2:** Record the product/IP divergence decided in D-9. Replace the committed arXiv PDF with a citation.
- **Priority / Phase / Size:** P1 · 1 · S; methodology and help (#2) P2 · 2 · S; IP alignment (#3) P2 · 1 · S

#### PL-06: Design system, accessibility, responsive
- **Today:**
  - The Data Noir look is strong.
  - Accessibility basics fail: non-focusable nav, 9 unlabeled icon buttons, empty `<title>` (QA-045).
  - Dynamic Tailwind classes silently drop colors (QA-039).
  - No z-index scale (QA-029).
  - Not responsive (QA-049).
  - Two UI primitives, `components/ui/switch.tsx` and `components/ui/tooltip.tsx`, are imported nowhere.
- **Decision:** Fix.
- **Requirements:**
  1. WCAG 2.1 AA for keyboard, focus and names; axe checks in CI.
  2. Design tokens for z-index, semantic colors (profit/loss/critic verdict), and a `DEMO` badge.
  3. No dynamic class strings; use a safelist or style maps.
  4. Responsive down to 1024 px (desktop-first ICP), with a read-only mobile layout for memos.
  5. Honor `prefers-reduced-motion` (ticker, scanlines, pulses).
  6. **P3:** Adopt the unused `switch` and `tooltip` primitives for VW-11 toggles and VW-09 metric tooltips, or delete them.
- **Priority / Phase / Size:** P2 · 2 · M; #6 P3 · 2 · S

#### PL-07: Dependency hygiene
- **Today:**
  - Python dependencies are unpinned.
  - `--prerelease=allow` with `unsafe-best-match` is set.
  - `torch` and `transformers` are hard imports in the API.
  - `duckduckgo_search` has been renamed to `ddgs`.
  - Several packages are unused: `py-clob-client`, `langchain-community`, `google-genai`, `psycopg2-binary`, `pydantic-settings`.
  - The frontend carries the wallet stack.
  - The frontend runs Next.js 14.0.3 on Node 18, which is end of life. 14.0.3 predates the fix for the middleware authorization-bypass advisory (fixed in 14.2.25). `eslint-config-next` (^14.2.35) doesn't match it.
- **Decision:** Fix.
- **Requirements:**
  1. A Python lock file (`uv lock`) that the backend Dockerfile installs from. The frontend already commits `package-lock.json` and builds with `npm ci`; keep it that way.
  2. Move ML dependencies to a worker-only extra.
  3. Remove unused packages.
  4. Turn on Renovate or Dependabot.
  5. **P0, before PG-02 Phase 0 ships:** Upgrade to Next.js ≥ 14.2.25 (or 15.x) and Node 20 or 22 LTS in all three Dockerfile stages, so the new auth gating doesn't rest on an affected release. **Done** in `8f7f518`: Next.js 16.4.1 and React 19 on Node 24 LTS (Node 20 reached end of life in April 2026).
- **Priority / Phase / Size:** **P0** (#5) · 0 · S; rest P1 · 1 · S

#### PL-08: Feature flags and pilot mode
- **Job:** One server-side switchboard that hides demo-only and unsafe surfaces, so every Hide decision in this plan has something to run on. *Persona:* Ops/Security Lead; founders running demos.
- **Today:**
  - No flag system exists. Nothing in `backend/` or `frontend/` reads `PILOT_MODE` or any `FEATURE_*` variable.
  - X-1, PG-06 (`FEATURE_AGENT_BUILDER`), SV-10 (`FEATURE_STRATEGY_LAB`), SV-11 and SV-13 (`FEATURE_EXECUTION`) and the "Hidden behind flags" row in §3 all depend on one.
- **Decision:** Fix (new build).
- **Requirements:**
  1. Flags come from env, with optional DB overrides that only an admin can set. `PILOT_MODE=true` turns on every pilot default.
  2. `GET /config/flags` returns the flags the frontend needs.
  3. The sidebar hides flagged items (GC-01 #2), and flagged routes show the not-found page (PG-07).
  4. A backend router behind an off flag returns 404. `FEATURE_EXECUTION` is off by default.
  5. Flag changes are audited (X-4).
- **Metric:** 0 flagged surfaces reachable with the flag off, checked by the E2E suite (PL-04).
- **Priority / Phase / Size:** **P0** · 0 · S–M

#### PL-09: Scheduler and background jobs
- **Job:** Run the recurring work that several cards assume: ingestion, evaluations, outcome capture and alerts. *Persona:* engineers; indirectly, every user who needs fresh data.
- **Today:**
  - No scheduler exists. The Celery worker has no beat schedule, and compose has no beat service.
  - `ScrapingAgent.start()` has its own sleep loop that nothing calls.
  - SV-03 #1, SV-08 #2, SV-04 #7 (nightly evals), SV-20, GC-05 ("key expiring" alerts) and outcome capture (VW-13) all assume scheduled jobs. They share this one missing platform piece.
- **Decision:** Fix.
- **Requirements:**
  1. A `celery-beat` service (or equivalent) in compose, with one job registry in code.
  2. Each job records its last run, duration and result. Job health is part of `/health/ready` (SV-16 #1).
  3. A failed or overdue job raises an alert (SV-16 #5).
- **Metric:** Scheduled job success ≥ 99%.
- **Priority / Phase / Size:** P1 · 1 · S

#### PL-10: Environments, release and live-deployment lockdown
- **Job:** Know every place this code runs, keep each one locked down, and ship changes through known environments with a way back. *Persona:* Ops/Security Lead.
- **Today:**
  - The committed nginx config names a public server, and the committed logs show requests from outside hosts. No card or runbook says what runs on that server now, who owns it, or whether it has the Phase 0 fixes.
  - Rotating keys in git (PL-02) doesn't secure a server that is already running this code with its old secrets.
  - There is one environment: no dev/staging/prod split, no continuous delivery, no build-stamped version (PG-03 #3 needs one) and no rollback.
- **Decision:** Fix.
- **Requirements:**
  1. **P0:** Inventory every running deployment of this code, starting with the server named in the committed nginx config. Record its owner, version and the secrets it holds.
  2. **P0:** Decommission each deployment, or lock it down: rotated secrets (PL-02), no published database, Redis or LLM ports, and the Phase 0 security fixes deployed. Review its logs for unexpected access and record the result.
  3. **P1:** Dev, staging and prod environments with separate secrets and data.
  4. **P1:** Continuous delivery from CI (PL-04) to staging, with a manual promotion to prod.
  5. **P1:** The build stamps a version that `/health` and the header (PG-03 #3) show.
  6. **P1:** A documented rollback, rehearsed once per phase.
- **Metric:** 100% of known deployments inventoried and on the current release.
- **Priority / Phase / Size:** **P0** (#1–2) · 0 · S; environments and release (#3–6) P1 · 1 · M

#### PL-11: Repo hygiene
- **Job:** Make the tree tell the truth about what is tested and what runs. *Persona:* engineers and coding agents.
- **Today:**
  - `backend/` holds ad-hoc scripts that look like tests but aren't: `debug_auth.py`, three `debug_engine*.py` variants (two import a class that no longer exists), `init_db2.py` (hardcoded credentials), `test_llm_call.py`, `test_pipeline.py`, `verify_alpha.py`, `verify_chat.py`, `verify_rbac.py` and `run_tests.sh`.
  - Top-level `test_llm.py` and `verify_concurrency.py` target a stale model service.
  - `local_tests/test_llm_resilience.py` imports the backend from the wrong directory and never runs; `local_tests/verify_trade_api.py` does nothing.
  - A vendored 22 KB `get-docker.sh` installer and build artifacts (`frontend/tsconfig.tsbuildinfo`, `local_tests/local_tests/screenshots/`) are committed.
  - PL-04 covers only pytest and the `local_tests` E2E, and PL-03 mentions only `init_db.py`.
- **Decision:** Cut.
- **Requirements:**
  1. Port `verify_rbac.py` into the PL-04 RBAC matrix test. Port `verify_concurrency.py` and `tests/test_concurrency_bench.py` into a load-test harness for the PL-01 #5 latency targets.
  2. Delete the other ad-hoc scripts and `get-docker.sh`.
  3. Git-ignore build artifacts and test screenshots.
- **Priority / Phase / Size:** P2 · 1 · S

#### PL-12: Demo workspace
- **Job:** Give founder-led demos a repeatable, honestly labeled dataset once pilot mode hides the mock surfaces. *Persona:* founders and sales.
- **Today:**
  - Demo polish rests on the mock surfaces that X-1 and PL-08 hide, and on `/demo/*`, which SV-14 removes.
  - Nothing provides a seeded, labeled demo dataset or a demo script. BACKLOG STRAT-001 ("Prototype Demo") had no plan card.
- **Decision:** Fix (new).
- **Requirements:**
  1. A seed script creates a demo workspace with labeled demo runs, memos and Mirror snapshots. Every item carries the `DEMO` badge (X-1, D-4).
  2. A reset command restores the seeded state.
  3. The demo workspace is isolated from pilot data (SV-18).
- **Priority / Phase / Size:** P2 · 1–2 · S

---

## 6. Roadmap

### Phase 0: Boot, secure, connect (Weeks 1–2, by 2026-10-28)

**Outcome:** The stack boots from a clean clone. A real user logs in with a password, runs a forecast, sees the result, and chats against a real local model. Nothing is exposed.

| Workstream | Cards |
| --- | --- |
| Boot and runtime | PL-01 (#1–3, #4 port lockdown, #6 installer secrets and env contract), PL-03 (baseline migration), PL-07 (#5 Next.js and Node upgrade, before real login) |
| Security stop-gaps | PL-02 (incl. #0 repository visibility, D-9), PL-10 (#1–2 live-deployment inventory and lockdown), PL-08 (feature flags), SV-01 (P0 items), SV-02 (mount router + deny-by-default), SV-13, SV-11 (gate; cut the order CLI and `QuantAgent`), SV-22 (#1 cut compat routes), X-3 auth on all routes |
| Real login | PG-02 (Phase 0 scope), X-2 shared fetch client, PG-04, PG-05 |
| Core loop works | VW-01b, SV-04 (#1–2, #5), SV-05 (#1), VW-08 / SV-06 / GC-07 (parser) |
| Safety net | PL-04 (CI + import smoke + llama.cpp contract test + E2E smoke) |

**Exit gate:** The regression gates in the QA report (§8) are green in CI. Zero S1 defects open.

### Phase 1: Make the audited loop real (Weeks 3–8, by 2026-12-09)

**Outcome:** The core loop (signal → sources → forecast → critic → memo) is real, persisted, cited and exportable. Every visible number is live or labeled.

| Workstream | Cards |
| --- | --- |
| Decision memo | VW-01c (runs, memo export, override), SV-04 (#3–4, #6, #9 linked markets or cut), SV-05 (#2–5), SV-21 (prompt registry) |
| Real data | SV-03 (incl. `ScrapingAgent` as the Polymarket job; cut the unused insight pipeline), VW-01a (live), SV-12 (Polymarket/Kalshi read-only), SV-19 (source retrieval and provenance), PL-09 (scheduler) |
| Mirror into the loop | VW-07, SV-07 |
| Honest UI | X-1 pilot mode on the PL-08 flags; hide VW-01e/f, VW-04/05/06, PG-06, GC-02; cut GC-08; rebuild GC-03; fix GC-04; PL-12 (labeled demo workspace) |
| Workspace basics | PG-03 (URL routing, layout), PG-07 (error and loading pages), GC-01, GC-06, VW-10 (security + audit), SV-01 P1 items, SV-16 (incl. #5 alerting), SV-17, SV-18 (workspaces; continues in Phase 2) |
| Release | PL-10 (#3–6 environments, continuous delivery, build version, rollback), PL-01 (#2 single reference model and setup script) |
| One chat | VW-08 / VW-01d / GC-07 merge |
| Hygiene | PL-05, PL-07, PL-11 (repo hygiene) |

**Exit gate:**
- 3 internal dry-run "pilot days" with no S1 or S2 defects found.
- Run completion ≥ 95%.
- Citation coverage ≥ 90%.

### Phase 2: Pilot-ready (Weeks 9–16, by 2027-02-03)

**Outcome:** 2–3 design-partner pilots can run the workflow weekly, with SSO, auditability, customer documents, and measured forecast quality.

| Workstream | Cards |
| --- | --- |
| Enterprise access | SV-01 (SSO), SV-18 (invites and seats), VW-11 (Settings, incl. Account), GC-05 (notifications) |
| Customer inputs | SV-14 (document ingestion), SV-08 (news as sources), SV-20 (first physical-market feed) |
| Evaluation | SV-04 (#7–8: nightly evals, outcomes, Brier), VW-13 (track record and calibration) |
| Context surfaces | VW-02/03 (Positions, read-only), VW-12 (asset detail), VW-09 (scanner on real metrics, if pilots want it) |
| Activation | PG-08 (onboarding and first run), SV-16 #6 (product events), PL-05 #2 (methodology and help) |
| Trust | PL-02 #5 (pilot trust pack), PL-01 #7 (offline profile), SV-22 (#2–4 public API) |
| Quality | PL-06 (accessibility and responsive), PG-01 |

**Exit gate:**
- Weekly active pilot users ≥ 3 per account.
- ≥ 1 exported memo per user per week.
- Brier reported weekly.
- Security questionnaire answered with no blockers.

### Phase 3: Expand after pull (2027-02 onward)

Build these only if pilots ask for them:

- Strategy Lab (VW-04 + VW-06 + SV-10)
- Agent Builder (PG-06)
- Correlations on real data (VW-05)
- Paper execution with risk controls (SV-11)
- Deterministic run replay (SV-15)
- Memo sharing, reviewer comments and sign-off (VW-01c #10)
- Per-category calibration dampening (VW-13 #4)

---

## 7. KPIs

| Category | KPI | Target (end of Phase 1 → Phase 2) | Source |
| --- | --- | --- | --- |
| Reliability | Clean-clone boot in CI | 100% | PL-04 |
| Reliability | Forecast run completion rate | ≥ 95% → ≥ 98% | SV-16 events |
| Reliability | p95 time to forecast result | ≤ 30 s → ≤ 20 s | SV-16 |
| Reliability | Chat non-empty response rate | ≥ 99% | SV-06 |
| Truthfulness | Visible UI values that are live or labeled `DEMO` | 100% | X-1 audit |
| Truthfulness | Claims with a citation | ≥ 90% → ≥ 95% | VW-01c |
| Truthfulness | Runs with a Critic review | 100% | SV-05 |
| Quality | Brier score by category (tracked weekly) | baseline → improving | SV-04 #8 |
| Quality | Critic override rate | tracked; investigate if > 20% | VW-01c |
| Security | Non-public endpoints without auth | 0 | PL-04 RBAC test |
| Security | Secrets in the repo (scanner findings) | 0 | PL-02 |
| Security | Sensitive actions missing from the audit log | 0 | SV-02 test |
| Adoption (pilot) | Weekly active users per pilot account | ≥ 3 | SV-16 #6 events |
| Adoption (pilot) | Memos exported per active user per week | ≥ 1 | SV-16 #6 events |
| Adoption (pilot) | Time to first useful brief (new user) | ≤ 10 min | SV-16 #6 events + interviews (PG-08) |

---

## 8. Definition of done (any feature card)

1. The acceptance criteria in its card pass, covered by automated tests: unit tests plus at least one E2E path.
2. Auth and role checks are in place (X-3), and sensitive actions are audited (X-4).
3. Loading, empty, error and timeout states exist (X-6). No false-success messaging.
4. The data shown is live, or labeled `DEMO` (X-1).
5. Generative output is validated (X-5).
6. Accessible by keyboard with labeled controls; URL-addressable (X-7).
7. Docs are updated (PL-05) and the backlog item is closed.

---

## 9. Risks and open decisions

| # | Decision needed | Recommendation | Why |
| --- | --- | --- | --- |
| D-1 | Is the product **commodities intelligence** or a **prediction-market terminal**? | Commodities wedge. Prediction markets are a *signal input* only. | Matches the vision doc and the YC plan. Removes off-wedge surfaces (crypto/politics correlations, wallet). |
| D-2 | Keep trade execution in the UI? | **No** until Phase 3, and paper-only then. | Current UI claims trades that don't happen (QA-013). Execution is out of MVP scope per the YC plan. |
| D-3 | Keep wallet connect? | **Cut.** | Unused, error-prone, adds bundle size, and doesn't fit the ICP. |
| D-4 | Mock data: hide or label? | `PILOT_MODE` hides; demo mode labels. | Preserves demo polish without misleading pilots. |
| D-5 | Critic provider default | **Local**, with Gemini opt-in per workspace. | Privacy-first principle (CONTRIBUTING.md). Removes the dependency on an external key. |
| D-6 | Auth approach | Backend JWT now; OIDC for pilots. | Fastest path to unblock Phase 0 without throwaway work. |
| D-7 | Reference model and hardware | Choose one GGUF and quantization plus a CPU/GPU profile; publish SLOs against it. Keep one setup script and cut the stale Ollama files (PL-01 #2). | Latency and quality targets are meaningless without a reference. The repo points at two models today: OpenForecaster-8B (top-level `setup_model.sh`, `Modelfile*`) and LFM2.5-1.2B (`backend/setup_model.sh`, used by compose). |
| D-8 | Real competitor names in Mirror seeds | Replace with generic examples; customers configure their own. | Avoids implying data relationships or claims about named firms. |
| D-9 | Repository visibility and IP alignment. The repository is public and holds the patent text, the committed keys and the QA report's security findings. Is the patent application filed, and what should be public? | Decide in Phase 0, before anything else is pushed: make the repository private, or scrub the patent text and the security findings from the tree and history (PL-02 #0). Keep IP text out of public repositories. Record where the product deliberately diverges from the patent claims (execution, Kelly sizing, whitelist critic), and whether Kelly survives as read-only sizing guidance (VW-01c #11, PL-05 #3). | Publishing a patent application before it is filed can destroy novelty outside the US grace period. Public security findings raise the risk to any deployment still running this code (PL-10). The README says "Proprietary & Confidential", which contradicts a public repository. |
| D-10 | Single-tenant deployment per customer, or a multi-tenant service? | Decide before SV-18 starts in Phase 1. Scope every customer-data table by `workspace_id` either way. | The choice changes auth, migrations and deployment design. Per-workspace credentials (VW-03, SV-12), document isolation (SV-14) and running 2–3 design partners at once (Phase 2) all depend on it. |

| # | Risk | Mitigation |
| --- | --- | --- |
| R-1 | Local model quality is too low for credible forecasts | Nightly eval set (SV-04 #7); Critic gating; allow a stronger model per workspace. |
| R-2 | Data licensing for physical-commodity feeds | Start with customer-provided documents (SV-14) and free reference prices; license one feed with the first paying pilot. |
| R-3 | Rotating committed keys breaks the existing server | Coordinated rotation runbook in PL-02, run together with the live-deployment inventory and lockdown in PL-10; do it in Phase 0 before any external demo. |
| R-4 | Scope creep back into execution or agents | Phase 3 items require pilot evidence (an interview quote plus a usage signal) before work starts. |

---

## 10. Backlog mapping

New epics are added to [BACKLOG.md](../BACKLOG.md) under **QA-2026-10**. How existing items relate:

| Existing item | Relationship |
| --- | --- |
| FEAT-002 / FEAT-CRITIC-001 / FEAT-008 (Critic, structured parsing) | Absorbed into **SV-05** |
| FEAT-005 (real-time state sync) | Absorbed into **X-1**, **SV-03**, **GC-03** |
| FEAT-009 (WebSocket lifecycle stream) | Code exists but crashes. Absorbed into **VW-01b / SV-04** (P0). |
| INFRA-002 (Docker orchestration) | Absorbed into **PL-01** |
| INFRA-005 (tiered model fallback) | Absorbed into **SV-04 #5** |
| INFRA-OBS-001 (structured telemetry) | Absorbed into **SV-16** |
| DEBT-ARCH-001 (unified intelligence domain) | Required to fix QA-001 properly. Absorbed into **PL-01 #1** (P0). |
| FEAT-001 (Intelligence Mirror) | Absorbed into **VW-07 / SV-07** |
| FEAT-004 (Data Noir UI) | Absorbed into **PL-06** |
| DEBT-002 / DEBT-003 (code editor, strategy class name) | Deferred with **VW-06 / SV-10** (Phase 3) |
| INFRA-001 (nginx SSL) | Absorbed into **PL-01 / PL-02** (rotate certs, WebSocket/SSE config) |
| MGMT-002 (narrative honesty) | Extended to the UI via **X-1** and **PL-05** |
| STRAT-001 (Prototype Demo) | Absorbed into **PL-12** (labeled demo workspace), built on the **PL-08** flags |
| STRAT-002 (Data Integration: physical-market sources) | Absorbed into **SV-20** (P2) |
| FEAT-003 (OpenForecaster integration via Ollama) | Superseded. Compose downloads an LFM model for llama.cpp, while stale top-level files still target OpenForecaster-8B on Ollama. The model choice moves to **D-7** and **PL-01 #2**, which cut the stale files. |
