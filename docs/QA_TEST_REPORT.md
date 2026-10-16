# QA Test Report — Full Application Pass

| | |
| --- | --- |
| **Date** | 2026-10-14 |
| **Commit tested** | `eb728a0` (`main`) |
| **Scope** | Every frontend route, every dashboard view, every global UI component, every mounted backend endpoint, the Celery prediction pipeline, the WebSocket lifecycle stream, and the existing automated test suites |
| **Companion document** | [Product Management Plan](PRODUCT_MANAGEMENT_PLAN.md), which turns these findings into a per-feature plan |
| **Fix status** | QA-001, QA-002, QA-003, QA-004, QA-005, QA-008, QA-009, QA-010, QA-020, QA-024, QA-035, QA-041, QA-047, QA-051, QA-052, QA-054 and QA-055 fixed and QA-011, QA-012, QA-033, QA-040, QA-050, QA-053 partly fixed on this branch after the test pass; see [§9 Fix status](#9-fix-status). Everything else is as tested. |

## 1. Executive summary

The Next.js app builds, type-checks, and lints cleanly, and the UI looks polished. **But the product does not work end to end as committed.**

| Area | Verdict |
| --- | --- |
| Backend API boot | ❌ **Crashes on import.** A circular import, an undefined `async_session` symbol, and a missing `sentence-transformers` dependency mean `uvicorn app.main:app` never starts. |
| Authentication | ❌ **Not real.** Login is email-only on the client, and admin access is a hardcoded email check. The UI never obtains a token, so every protected API call returns `401` with the shipped config. |
| Core workflow (forecast → critic → result) | ❌ **Never completes in the UI.** The lifecycle WebSocket crashes on connect, so the "Neural Audit" spinner runs forever. |
| Chat (4 surfaces) | ❌ **Empty replies against a real llama.cpp server**, because streaming output is parsed in the wrong wire format. |
| Default LLM | ⚠️ The compose stack builds a **canned mock**. Every forecast is `0.5` and every "strategy" is one fixed sentence. |
| Data shown in the UI | ⚠️ Most numbers on screen are hardcoded or `Math.random()`, presented as live: stat cards, ticker, portfolio, correlations, security log, notifications, data matrix. |
| Security posture | ❌ The JWT secret is forgeable, default passwords are trivial, private keys are committed, order placement has no role check, and several endpoints are unauthenticated. |
| Automated tests | ⚠️ Backend: 46 passed, 2 failed, 1 module fails to import. E2E: 4 of 6 fail (stale). No CI. |

**56 defects logged:** 14 critical (S1), 29 major (S2), 13 minor or cosmetic (S3/S4). See [§5 Defect log](#5-defect-log).

## 2. Test environment and method

### 2.1 Environment

There is no Docker daemon in the test sandbox, so the compose topology was reproduced natively, service for service:

| Service | How it ran |
| --- | --- |
| Postgres | 16.15 with pgvector 0.6.0, database `polymarket`, same credentials as compose |
| Redis | 7.0.15 |
| Backend | FastAPI on Python 3.11, `uvicorn app.main:app` |
| Worker | `celery -A app.worker.celery_app worker` |
| LLM | `text-gen-cpp-mock` (exactly what compose builds), plus a **llama.cpp wire-format emulator** that returns schema-valid JSON and streams real `data: {...}` SSE frames, to test the happy path |
| Frontend | Next.js 14.0.3 production build (`next build` then `next start`), `/api/*` rewritten to the backend |
| Browser | Chromium 141 via Playwright 1.56, at 1600×1000 desktop and 390×844 mobile |

**Hotfixes needed just to boot the API.** These were applied to a scratch copy only; the repository is unchanged:

1. Emptied `backend/app/domain/intelligence/__init__.py` to break the circular import (QA-001).
2. Added `async_session = AsyncSessionLocal` to `backend/app/db/session.py` (QA-002).
3. Installed `sentence-transformers`, which `requirements.txt` does not list (QA-002).

**Sandbox network limits.** These are not product defects, but they limited what could be observed:

- **Blocked:** DuckDuckGo/Bing search, CNBC/NYT RSS, Yahoo and Stooq quotes, Polymarket Gamma, Hugging Face model downloads, the PyTorch wheel index, WalletConnect relays, and Wikimedia.
- **Affected outputs:** `/intelligence/news` returned `[]`, `/mirror/analyze` returned `no_sources`, scanner prices used the synthetic fallback, and FinBERT did not load.
- **How these were assessed:** by code review, not live.

### 2.2 What was run

| Suite | Coverage |
| --- | --- |
| Static and build checks | `tsc --noEmit`, `next lint`, `next build`, backend `pytest tests/` |
| API smoke | Every route in `/openapi.json` (19 routes), each called with and without an admin bearer token, using bodies generated from the schema |
| API deep probes | JWT forgery, RBAC per role, trade input validation, the prediction lifecycle (HTTP + WebSocket), cache behavior, cross-user task access, rate limiting, chat edge cases, error leakage |
| Browser crawl | 7 public routes, plus all 12 sidebar destinations as both **User** and **Admin**, plus 3 standalone routes for each role. That is 38 page states, each with a screenshot, console errors, failed requests, and an inventory of controls. |
| Browser scenarios | 28 user journeys: watchlist search/filter, Neural Audit, data-matrix context menu, ticker chart, notifications, status dropdown, settings save, sidebar chat, analyst chat and persona, strategy CLI commands, Quant Engine generate/save/backtest, Mirror analyze and trade, scanner filters, correlations toggle, Security lockdown, Alpaca view, view-state persistence, accessibility basics, Agent Builder drag/save/reload, cross-page nav, logout, mobile |
| Repo E2E suite | `local_tests/test_app.py` and `test_chat_ui_e2e.py` against the live stack |
| Code audit | Line-by-line review of `frontend/app`, `frontend/components`, `frontend/lib` and `backend/app`, used to explain root causes and cover paths the sandbox could not reach |

## 3. Automated check results

| Check | Result | Notes |
| --- | --- | --- |
| `npx tsc --noEmit` | ✅ Pass | |
| `next lint` | ✅ Pass | No warnings |
| `next build` | ✅ Pass, with warnings | `pino-pretty` unresolved (WalletConnect logger); "Invalid projectId" printed 9 times; `/dashboard` first-load JS is 589 kB |
| Backend `pytest` | ⚠️ **46 passed, 2 failed, 1 error** | See below |
| Repo E2E (`local_tests`) | ❌ **2 passed, 4 failed** | The "passes" are a screenshot-only test and a test whose body is `pass`. The failures expect the dashboard at `/`, which now shows a landing page plus a login gate. |
| Backend boot (`uvicorn app.main:app`) | ❌ **ImportError** | QA-001 and QA-002 |

**Backend test failures**

- `tests/test_swarm.py` fails at collection: `ImportError: cannot import name 'GeopoliticalAgent' from 'app.domain.intelligence.swarm'`.
- `tests/test_fallback.py::test_fallback_logging_is_structured` fails with `assert 0 == 2`. No structured `fallback_attempt_*` records are emitted, and it fails in isolation too.
- `tests/test_engine.py::test_generate_forecast_parsing` is **not hermetic**. Its httpx mock never intercepts the shared client:
  - With `LLAMA_CPP_HOST` set, it calls the real LLM and fails.
  - With `LLAMA_CPP_HOST` unset, it tries a hardcoded Docker-internal LLM address (`core/ai_client.py`) and hung until the 300 s timeout.
- The run also needs `torch`, which is only installable from PyPI as the full CUDA build (about 3 GB), plus `aiosqlite`, `pytest`, and `pytest-asyncio`. None of the last three are in `requirements.txt`.

## 4. Results by surface

**Legend**

| Mark | Meaning |
| --- | --- |
| ✅ | Works as designed |
| 🟡 | Partially works |
| 🎭 | Static or mock data presented as live |
| ❌ | Broken |
| 🔒 | Gated to the hardcoded Admin email |

### 4.1 Pages (routes)

| Route | Result | Observed |
| --- | --- | --- |
| `/` Landing | 🟡 | Renders. `/grid.svg` returns 404. The status bar claims "Quantum_Encrypted" and "Global_Mesh" (static). The chat bubble appears before login. |
| `/login` | ❌ | Email only, no password. Any address containing `@` logs in. One hardcoded address is granted Admin. No backend call. |
| `/dashboard` | 🟡 | Loads. The watchlist shows "Unable to load markets" (`401`) with the default config. Every view below hangs off this page. |
| `/intelligence` | 🟡 | Renders **without login**: no auth guard, no app chrome, trade buttons exposed. No link points to it. |
| `/portfolio` | 🎭 | Renders **without login**. A $2.1M mock book. Refresh and LAYOUT do nothing. No link points to it. |
| `/agents/builder` 🔒 | 🎭 | Drag-and-drop canvas works. Nodes cannot be configured. **Everything is lost on reload.** Save Draft and Deploy do nothing. Sidebar links always land on Markets. |
| Unknown route | 🟡 | Default Next.js 404, unstyled. |

### 4.2 Dashboard views

| View | Result | Observed |
| --- | --- | --- |
| **Live Markets: Watchlist** | ❌ with default config, ✅ with demo auth | `GET /api/markets` returns 401. With `ALLOW_DEMO_AUTH=true`, 6 static commodities load. Search and category filters work. |
| **Live Markets: Neural Audit** | ❌ | `POST /prediction/predict` returns 200, then the WebSocket opens, then the backend raises `TypeError` (main.py:121). The UI showed "ESTABLISHING PEER HANDSHAKE… SCANNING" for **60+ seconds** and never reached a result. See screenshot 02. |
| Live Markets: Macro State, Signals, Depth chart | 🎭 | Static arrays. The world map is an external Wikimedia SVG. |
| Live Markets: Data Matrix | 🎭 | 8 hardcoded commodities on a 1 s random walk. Right-click "Trade Now" shows a toast "Routing NGAS order to nearest dark pool" **with no request made**. |
| Portfolio | 🎭 | Fully hardcoded. It silently becomes the Alpaca view once an Alpaca key is saved. |
| Alpaca Markets | 🟡 | Error state: "configure them in SYSTEM_CONFIG". That is the title of the unlabeled gear-icon dialog, which is hard to find; the sidebar "Config" item opens a placeholder. Calls `localhost:8000` directly. |
| Strategies (CLI) 🔒 | 🟡 | `/help`, `/list` (hardcoded), `/status` (hardcoded) and `/deploy` (always fails) all respond. Free text gives **"No response received."** (chat bug QA-009). Input is disabled for about 2.4 s by a boot animation on every visit. |
| Correlations 🔒 | 🎭 | Static crypto and politics matrix, off-wedge for a commodities product. Most cells have no color (dynamic Tailwind classes). See screenshot 07. |
| Quant Engine 🔒 | ❌ | "Generate" puts **non-code LLM prose into the code editor** with no validation. Save and Backtest do nothing. Python is highlighted as JavaScript. |
| Intelligence Mirror 🔒 | 🟡 | Competitors load (2 hardcoded firms). Analyze works, with sources blocked in the sandbox. On empty sources it shows a fabricated fallback card. **INITIATE_BUY shows "Mirror Trade Initialized"** while the backend only returns an unsigned placeholder payload. |
| Analyst Chat | ❌ | `POST /chat/stream` returns 200, but the **assistant bubble is empty**. The persona toggle has no backend effect. See screenshot 03. |
| Alpha Scanner 🔒 | 🟡 | **Default filters returned 0 assets on first load** (they do about 60% of the time, because the synthetic metrics move with the clock; QA-038). Relaxing the filters gives 14 assets. Metrics are synthetic sin/cos of time. Calls `localhost:8000` directly. |
| Security 🔒 | 🎭 | Static services and audit log. LOCKDOWN_MODE does nothing. The backend security router is not mounted. |
| Config | ❌ | Shows "ACCESS_RESTRICTED // MODULE_DECRYPTION_IN_PROGRESS" **to admins too**. There is no functionality. See screenshot 06. |

### 4.3 Global components

| Component | Result | Observed |
| --- | --- | --- |
| Sidebar navigation | 🟡 | Works with a mouse. **0 keyboard-focusable items** (`div onClick`). Six of the seven locked items still navigate, to a placeholder; the locked Agent Builder item does nothing. "Documentation" is dead. The view is not in the URL, so reload resets to Markets. |
| Ticker + chart modal | 🎭 | Static prices (BTC $42,105). The modal shows `Math.random()` data labeled "LIVE_CHART". Items are click-only `div`s, not keyboard-reachable (the tape pauses on hover). |
| Stat cards | 🎭 | All hardcoded. Compute Health is **permanently red "CRITICAL LAG DETECTED"** because 88.5 < 90. |
| System status dropdown | 🟡 | Polls `/health` every 15 s, but shows **SYSTEM_OPTIMAL even when `/health` says `degraded`**. **Renders under the stat cards.** |
| Notification center | 🎭 | 4 hardcoded alerts, including a fake "Critical Margin Alert". **The popover renders under the stat cards, so it is unreadable.** See screenshot 04. |
| Settings modal | 🟡 | Saves to localStorage. The llama.cpp URL and Gemini key are saved but never used. No save confirmation; the dialog stays open. Secrets are stored in plaintext. |
| Sidebar chat (global) | ❌ | `POST /api/chat` returns 200 with an **empty reply bubble**. The close button overlaps Send. Visible on landing and login. |
| Wallet connect | ❌ | Wallet connectors open relay WebSockets on **every page**; with the relays blocked in the sandbox, each page threw uncaught errors. The `projectId` is a placeholder (RainbowKit substitutes its shared example ID). The wallet is never used by any feature. |
| Mobile (390 px) | ❌ | The fixed 256 px sidebar takes about 2/3 of the screen and content is clipped. Not usable. |

### 4.4 Backend API (19 mounted routes, plus the WebSocket)

| Route | No token | Admin token | Notes |
| --- | --- | --- | --- |
| `POST /auth/token` | 200 | 200 | All 4 default users log in. A wrong password gives 401. |
| `GET /markets` | 401 | 200 | Static list of 6 items |
| `POST /prediction/predict`, `POST /predict` | 401 | 200 | Rate limit is 429 after 6 per minute **per IP** |
| `GET /prediction/task/{id}`, `GET /task/{id}` | 401 | 200 | **An unknown ID returns `processing` forever.** Any user can read any task. |
| `POST /trade/execute` | 401 | 200 | Analyst gets 403 (correct). Side `HODL` and quantity `-5` are **accepted**. The payload is a placeholder. |
| `POST /chat` | 401 | 200 | Empty `response` with real llama.cpp framing |
| `POST /chat/stream` | 401 | 200 | `done: "I couldn't generate a response."` with real llama.cpp framing |
| `GET /intelligence/news` | **200** | 200 | No auth. `[]` in the sandbox (RSS blocked). |
| `GET /intelligence/status` | **200** | 200 | `model_loaded: false` (Hugging Face blocked) |
| `POST /strategy/generate` | **200** | 200 | No auth. Returns LLM prose as `code`. |
| `GET /mirror/competitors` | **200** | 200 | No auth. Hardcoded. |
| `POST /mirror/analyze/{id}` | **200** | 200 | No auth. Accepts any `target_id`, including nonexistent ones. |
| `GET /api/v1/scanner/assets` | **200** | 200 | No auth. Synthetic metrics. |
| `POST /tools/call` | 401 | 404 for an unknown connector | **An analyst can reach `place_market_order`**; it was blocked only because no Alpaca credentials were configured. |
| `POST /demo/analyze` | **200** | 200 | No auth. Returns `status: success` even when the payload contains an error. |
| `POST /demo/ingest_news` | **200** | 200 | **Unauthenticated database write** |
| `GET /health` | 200 | 200 | `degraded` whenever `GEMINI_API_KEY` is unset |
| `WS /ws/lifecycle/{id}` | – | – | **Crashes on every connection** |
| `/security/*` | – | – | **Not mounted** (absent from OpenAPI) |

### 4.5 Prediction pipeline, measured

| Configuration | Time | Result |
| --- | --- | --- |
| Bundled mock LLM (shipped default) | **16–17 s** per task, mostly retry back-off on failed LLM calls | `initial_forecast = adjusted_forecast = 0.5`. Every swarm `reasoning` is `"Error: Expecting value: line 1 column 1 (char 0)"`. Critique is `"Critic unavailable: [Errno -2] Name or service not known"`. Task status is still **`completed`**. |
| llama.cpp-format emulator returning valid JSON | **About 1 s** | `0.58 → 0.61` after the critic, using the Ollama path. `adversarial_score`, `logical_fallacies` and `counter_arguments` are always empty. Swarm labels are mismatched ("mirror" is rendered as "Geopolitical Impact"). |
| Same question asked twice | – | Not cached. A new task runs each time, because the cache is never written. |
| 5 consecutive tasks per worker | – | No "event loop is closed" errors. The suspected httpx event-loop reuse bug was **not reproduced**. |

## 5. Defect log

**Severity scale**

| Level | Meaning |
| --- | --- |
| **S1** | Blocks the core product or is a security exposure |
| **S2** | Major feature broken or misleading |
| **S3** | Minor |
| **S4** | Cosmetic |

**Evidence codes**

| Code | Meaning |
| --- | --- |
| **L** | Reproduced live |
| **C** | Confirmed by code review |

### S1: Critical

| ID | Area | Defect | Evidence | Root cause |
| --- | --- | --- | --- | --- |
| QA-001 | Backend | API process fails to start: circular import | L | `app/main.py:19` imports `app/intelligence/api/news.py`, whose line 4 imports `app.domain.intelligence.feed_manager`. That triggers `app/domain/intelligence/__init__.py:1`, which runs `router.py:1` and imports back into `news.py`. Introduced in `ca2a97f`. |
| QA-002 | Backend | API import chain needs an undefined `async_session` and an undeclared `sentence-transformers` | L/C | `app/agents/news_agent.py:4,6` and `app/agents/quant_agent.py:7`, reached via `app/routers/demo.py`. `async_session` was never defined (since `9dd918c`). |
| QA-003 | Auth (frontend) | Login is email-only, client-side. Admin is a hardcoded email. Any user can self-promote by editing localStorage. | L | `frontend/lib/auth/AuthContext.tsx:40-48`, `app/login/page.tsx:14-26` |
| QA-004 | Auth (integration) | The UI never sends a token, so every protected endpoint returns 401 with the shipped config | L | No call to `/auth/token` anywhere in `frontend/` |
| QA-005 | Security | JWT forgeable with the hardcoded default secret. A forged admin token was accepted (200). | L | `backend/app/core/security.py:10`; `.env.example` ships a placeholder secret |
| QA-006 | Security | 4 hardcoded users with trivial passwords. No lockout or throttling on login. | L | `backend/app/services/user_service.py` |
| QA-007 | Security | Private keys and logs committed: TLS key, NPM JWT RSA key, NPM SQLite DB, access logs, `backend_logs.txt`, public server IP | L | `nginx/certs/server.key`, `nginx/data/*`, `nginx/conf.d/default.conf`, `backend_logs.txt` |
| QA-008 | Forecast workflow | Neural Audit never completes in the UI. The WebSocket handler crashes. | L | `backend/app/main.py:121`: `await` on redis-py's synchronous `pubsub.subscribe()` |
| QA-009 | Chat | All chat surfaces return empty output against a real llama.cpp server | L | `backend/app/core/ai_client.py:141-151` parses `data: …` SSE lines with `json.loads` |
| QA-010 | LLM runtime | Compose serves a canned mock, not the downloaded `lfm-thinking` model. Outputs are meaningless. | L | `docker-compose.yml` builds `text-gen-cpp-mock`; `text-gen-cpp-mock/main.py:24` |
| QA-011 | Trading | `/tools/call` lets **any** authenticated role place Alpaca market orders with the server's credentials. No audit. | L | `backend/app/routers/tools.py` (no role check); `connectors/alpaca.py:13-15` (falls back to env credentials) |
| QA-012 | Security | Unauthenticated database write and compute endpoints | L | `/demo/ingest_news`, `/demo/analyze`, `/strategy/generate`, `/mirror/analyze`, `/intelligence/news`, scanner |
| QA-024 | Critic | The Gemini critic path can expose the server's Gemini API key to users and logs through error text. It also calls the legacy `gemini-pro` endpoint and ignores the model the critic requests. Exploit specifics are withheld from this public document pending decision D-9. | L/C | `core/ai_client.py` (Gemini provider); `intelligence/domain/critic.py` (error handling) |
| QA-051 | Infra | Compose publishes Postgres (trivial default password) and Redis (no auth) on all host interfaces, plus the app ports, which bypass nginx/TLS. Backend runs `--reload`; backend and worker bind-mount the source. | C | `docker-compose.yml` (`ports:` on db, redis, backend, frontend, text-gen-cpp; backend command and volumes) |

### S2: Major

| ID | Area | Defect | Evidence | Root cause / location |
| --- | --- | --- | --- | --- |
| QA-013 | Trading UI | False-success toasts: "Mirror Trade Initialized" and "Routing … to nearest dark pool". No order exists. | L | `components/intelligence/DecisionProtocol.tsx`; `components/dashboard/data-matrix-feed.tsx` (toast only); `services/execution.py:55-60` (placeholder calldata) |
| QA-014 | Trading API | No validation: side `HODL` and negative quantity accepted | L | `app/models.py` TradeRequest; `routers/trade.py` |
| QA-015 | Forecast | Failures are returned as `completed`. Celery `autoretry_for` never fires. | L | `intelligence/application/engine.py:94-103`; `worker.py:47-49` |
| QA-017 | Forecast | Unknown or expired task ID reports `processing` forever | L | `routers/prediction.py:58-62` |
| QA-018 | Forecast | No ownership check: any user can read any task result | L | `routers/prediction.py` |
| QA-019 | Platform | Rate limit keyed on client IP. Behind nginx this becomes a site-wide 6/min limit. Redis errors produce 500s. | L/C | `app/limiter.py:31-43` |
| QA-020 | Frontend | `http://localhost:8000` is hardcoded in `alpha-scanner.tsx` and is the effective fallback in 3 more components, so all 4 break for any non-local user. | L | `alpha-scanner.tsx:46` (literal URL); `StrategyBuilder.tsx:30`, `DecisionProtocol.tsx:30`, `alpaca-dashboard.tsx:43,56` (`process.env.NEXT_PUBLIC_API_URL \|\| 'http://localhost:8000'`). `NEXT_PUBLIC_API_URL` is set only at runtime (`docker-compose.yml:81`), not at build time (`frontend/Dockerfile:14`), so Next.js never inlines it and the browser uses the fallback. |
| QA-021 | Infra | Scanner unreachable through nginx: the `/api/v1` prefix collides with the `/api/` strip | C | `routers/scanner.py:13`; `nginx/conf.d/default.conf` |
| QA-022 | Data | No schema bootstrap: no Alembic revisions, no startup `create_all`, and `init_db.py` doesn't create the `vector` extension | L/C | `backend/migrations/` (no `versions/`); `init_db.py` |
| QA-023 | Security | Security router (API keys, IP allowlist, audit log) not mounted. Audit logging is never invoked. | L | `app/main.py` (router not included); `core/audit.py` (called only from the unmounted security router, so no event is ever written) |
| QA-026 | Forecast | Swarm sections mislabeled ("mirror" rendered as "Geopolitical Impact", and so on) | L | `intelligence/domain/swarm.py:120-126` |
| QA-027 | Data integrity | Synthetic "physical intelligence" attributed to real vendors (Orbital Insight, Vortexa, …) and returned as sources | L | `intelligence/infrastructure/physical_data.py:27-98` |
| QA-028 | Health | UI shows SYSTEM_OPTIMAL when `/health` says `degraded`. Health is `degraded` whenever Gemini is unset. | L | `system-status-dropdown.tsx:57`; `main.py:113` |
| QA-029 | UI | Notification popover and status dropdown render beneath the stat cards | L | z-index or stacking-context conflict between the animated header and the stat-card grid (`app/dashboard/page.tsx`, `notification-center.tsx`, `system-status-dropdown.tsx`) |
| QA-030 | UI | Compute Health card permanently shows "CRITICAL LAG DETECTED" | L | `stat-cards.tsx:26` (hardcoded 88.5 < 90) |
| QA-031 | Strategy | Generated "code" is not validated; prose lands in the editor. Save and Backtest do nothing. | L | `strategy/service.py:18-19`; `StrategyBuilder.tsx:102-107` |
| QA-032 | Agent Builder | No persistence or backend. Graph lost on reload. Save Draft and Deploy do nothing. | L | `app/agents/builder/page.tsx:59-64` |
| QA-033 | Platform | Import-time model downloads (FinBERT, bge-m3) plus hard `torch`/`transformers`/`sentence_transformers` imports. Slow cold start. Offline, both loads fail silently and the API still boots with degraded output: every sentiment is neutral and every embedding is the constant `[0.01]*1024`, so RAG retrieval is meaningless. | L | `domain/intelligence/sentiment.py:2-3,26-33,45`; `agents/news_agent.py:4,16-20,32-34` (instantiated at import via `routers/demo.py:9`) |
| QA-034 | Quality | Test suites stale or non-hermetic. No CI. | L | §3 |
| QA-035 | Auth | `/intelligence` and `/portfolio` routes have no auth guard | L | `app/intelligence/page.tsx`, `app/portfolio/page.tsx` |
| QA-036 | Chat | Persona selector has no effect | C | `persona` is never read in `backend/app` |
| QA-037 | Chat | Backend replaces client history with the user's 10 most recent stored messages (shared across all chat surfaces) and ignores `context`. Only the last 5 messages reach the prompt. | C | `services/chat.py:38-41` (`/chat`) and `services/chat.py:81-84` (`/chat/stream`); `intelligence/application/forecasting.py:119-143` (`history[-5:]` at :135) |
| QA-038 | Scanner | Default filters (premium ≥ 2, accuracy ≥ 90) usually return 0 results (about 60% of the time): the metrics are synthetic time-based sine waves that move almost in phase across assets. A negative premium filter is never sent. Negatives render as "+$-x". | L | `alpha-scanner.tsx:29-30,39,207`; `routers/scanner.py:139-142` |
| QA-039 | Correlations | Heatmap colors missing for every cell with magnitude above 0.20 (dynamic Tailwind classes are never generated). Only weak cells (magnitude ≤ 0.20) get the `/20` tint, so the visual emphasis is inverted. Data is a static mock matrix labeled "UPDATED HOURLY" and is off-wedge. | L | `correlations-view.tsx:10-18,41-51,79-86` |
| QA-040 | Settings | llama.cpp URL and Gemini key are saved but never used. No save feedback. Secrets (Gemini key, Alpaca key and secret) stored in plaintext localStorage. | L | `settings-modal.tsx:44-51`; `lib/llm-config.ts:10-13` (`getLlamaCppUrl()` is never called); `POLY_GEMINI_KEY` is read only by the modal itself (`settings-modal.tsx:38`) |
| QA-042 | Config | Config view shows "Access Restricted" placeholder to admins | L | `app/dashboard/page.tsx:164` |
| QA-043 | Navigation | Active view not in URL, so reload and back lose context. Agent Builder nav always lands on Markets. | L | `app/dashboard/page.tsx:60`; `app/agents/builder/page.tsx:34` |
| QA-044 | Sidebar chat | Close button overlaps the Send button | L | `components/layout/sidebar-chat.tsx` (fixed toggle at `bottom-6 right-6`) |
| QA-052 | Infra | nginx doesn't forward WebSocket upgrades, so behind nginx the Neural Audit lifecycle socket never connects. The backend returns 404 to the non-upgraded request, and the UI silently stops the spinner with no result, even once QA-008 is fixed. Buffering is also left on, so chat SSE arrives all at once. | C | `nginx/conf.d/default.conf:31-40` (`/api/` has no `proxy_http_version 1.1`, `Upgrade`/`Connection` headers or `proxy_buffering off`). The WS URL is built from `/api` at `components/dashboard/market-table.tsx:107`. `ws.onerror` (`:133-136`) has no fallback. |

### S3/S4: Minor and cosmetic

| ID | Area | Defect | Evidence |
| --- | --- | --- | --- |
| QA-016 | Forecast | Result cache is read but never written (`routers/prediction.py:32-41`, `:51-56`; no writer anywhere), so an identical question re-runs the full pipeline. This costs only time and LLM compute; the `cached_*` branches are dead code. | L |
| QA-025 | Critic | `adversarial_score`, `logical_fallacies` and `counter_arguments` are never populated. They always return their defaults (0.0 / []), and nothing in `frontend/` reads them. | L |
| QA-041 | Alpaca | The error says to configure keys in "SYSTEM_CONFIG" (`alpaca-dashboard.tsx:80`). That name appears only as the title of the unlabeled gear-icon dialog (`settings-modal.tsx:69`), which does hold the Alpaca key fields. The sidebar "Config" item, where users will look, opens a placeholder (QA-042). | L |
| QA-045 | Accessibility | 0 focusable nav items. 9 icon-only buttons with no accessible name. Empty `<title>` (root layout is a client component, so there is no metadata). | L |
| QA-046 | Assets | `/grid.svg` returns 404. No favicon. `public/` is empty. | L |
| QA-047 | Wallet | Wallet connectors (WalletConnect, Coinbase WalletLink) open relay WebSockets on every page load, although no feature uses the wallet (`app/layout.tsx:35`). With the relays blocked in the sandbox, every page threw 3 uncaught errors; an open network was not tested. The `projectId` is the placeholder `YOUR_PROJECT_ID` (`lib/wagmi.ts:13`), which RainbowKit warns about and silently replaces with its shared example ID. App name is "Polymarket Hedge Fund" (`lib/wagmi.ts:12`). | L/C |
| QA-048 | Ticker | Ticker prices are hardcoded (`ticker.tsx:28-55`), and items are click-only `div`s that keyboard users cannot reach (`ticker.tsx:15`). The chart modal plots `Math.random()` data labeled "LIVE_CHART" (`chart-modal.tsx:29,84`). | L/C |
| QA-049 | Responsive | Not usable at 390 px. The sidebar eats the viewport. | L |
| QA-050 | Config | `.env.example` mismatches: `ALPACA_SECRET` vs `ALPACA_SECRET_KEY`; `KALSHI_SECRET` vs `KALSHI_API_SECRET`/`KALSHI_KEY_ID`. A placeholder `GEMINI_API_KEY` makes health report Gemini configured. `ACCESS_TOKEN_EXPIRE_MINUTES` is ignored. | C |
| QA-053 | Docs | `frontend.md` lists React Query and Recharts, which are not installed. README implies `lfm-thinking` is served, but compose builds a mock. The YC plan's Q2 2026 "stabilize" outcome is unmet. | C |
| QA-054 | Critic | Critic defaults to Ollama, but compose has no Ollama service | L |
| QA-055 | Build | `pino-pretty` unresolved. 589 kB first-load JS on `/dashboard`. | L |
| QA-056 | Dependencies | `duckduckgo_search` renamed to `ddgs` (runtime warning). Requirements are unpinned. `--prerelease=allow` with `unsafe-best-match`. | L/C |

## 6. Evidence screenshots

| # | Screenshot | Shows |
| --- | --- | --- |
| 01 | [Dashboard, default config](qa/screenshots/01-dashboard-default.jpg) | "Unable to load markets" (401), permanent "CRITICAL LAG DETECTED", SYSTEM_OPTIMAL while health is degraded |
| 02 | [Neural Audit stuck](qa/screenshots/02-neural-audit-stuck.jpg) | Spinner after 60 s; the WebSocket crashed server-side |
| 03 | [Analyst Chat empty reply](qa/screenshots/03-analyst-chat-empty-reply.jpg) | Empty assistant bubble (QA-009) |
| 04 | [Notifications behind cards](qa/screenshots/04-notifications-behind-cards.jpg) | Popover rendered under stat cards (QA-029) |
| 05 | [Intelligence Mirror fallback](qa/screenshots/05-intelligence-mirror-fallback.jpg) | `no_sources`, fabricated fallback stream, trade buttons |
| 06 | [Config restricted for admin](qa/screenshots/06-config-restricted-for-admin.jpg) | Placeholder shown to admins (QA-042) |
| 07 | [Correlations missing colors](qa/screenshots/07-correlations-missing-colors.jpg) | Uncolored heatmap cells (QA-039) |
| 08 | [Quant Engine non-code output](qa/screenshots/08-quant-engine-non-code-output.jpg) | LLM prose placed in the code editor (QA-031) |

## 7. Not verified

These need the real environment:

- **Live external data**: DuckDuckGo search, RSS news, Yahoo and Stooq quotes, Polymarket and Kalshi, and FinBERT/bge-m3 model loading. The sandbox network blocks them.
- **The real `lfm-thinking` GGUF on llama.cpp.** Compose now serves it (QA-010), but the download is blocked in the sandbox. The integration was checked against `llama-server` built from the pinned tag with a small LFM2-architecture model instead; answer quality and latency of the real model are untested.
- **Gemini critic against Google's API**, which needs a real key.
- **Alpaca paper trading**, which needs real keys. The RBAC gap (QA-011) was confirmed up to the connector boundary.
- **The full Docker Compose stack plus nginx/TLS.** No Docker daemon in the sandbox. The nginx findings come from config review.

## 8. Recommended regression gates

Before the next demo or pilot, these should be automated and green in CI:

1. `uvicorn app.main:app` boots, and `GET /health` returns 200, against a fresh database with migrations applied.
2. Login with real credentials gives a token, and `/markets`, `/prediction/*` and `/chat` succeed from the UI.
3. The Neural Audit reaches a rendered result in under 30 s with a JSON-capable model, and the WebSocket emits `status` then `complete`.
4. Chat returns non-empty text against llama.cpp SSE framing. This needs a contract test using a recorded llama.cpp stream.
5. Unauthenticated calls to every non-public route return 401, and analyst/risk roles cannot reach order placement.
6. `pytest` passes with zero network access. `local_tests` E2E is updated for the login gate.

## 9. Fix status

Fixed on this branch after the test pass. Each fix was re-tested on the same stack (API, worker, browser and, for nginx, the repo's own config run natively) and went through an adversarial review whose upheld findings were also fixed.

| Defect | Status | Commit | What changed |
| --- | --- | --- | --- |
| QA-001 | Fixed | `9e55ae3` | Circular import removed; `uvicorn app.main:app` boots (about 5 s to healthy). A fresh-interpreter import test guards it. |
| QA-002 | Fixed | `9e55ae3` | Agents use `AsyncSessionLocal`; `sentence-transformers` is declared and imported lazily. |
| QA-003 | Fixed | `f62778e`, `ebec2f0` | The login page signs in with a username and password against `/auth/token`, and the user and role shown come from `/auth/me` (from the token itself only while the backend is unreachable). The backend checks the token on every call, so editing browser storage gains no access. The four development accounts still have public default passwords and there is no lockout (QA-006). The token is kept in `localStorage`. |
| QA-004 | Fixed | `f62778e`, `ebec2f0` | Every HTTP call from the UI sends the token; a 401 signs the user out, while a backend that is down or failing does not. Other tabs follow sign-in, sign-out and user switches. The lifecycle WebSocket still takes no token. |
| QA-005 | Fixed | `f62778e`, `ebec2f0` | There is no built-in signing key any more: an unset or public placeholder `SECRET_KEY` is replaced by a random one (sign-ins then end on restart), `.env.example` ships it empty, and `./run.sh` writes a private key into `.env`, also fixing an existing `.env` that has the placeholder. Tokens signed with the old default key are refused. |
| QA-020 | Fixed | `f62778e`, `ebec2f0` | All four components call the backend through the `/api` proxy (`API_URL`) instead of `http://localhost:8000`. The Docker build sets the proxy target to the backend's compose address, since `next build` fixes it into the image. |
| QA-035 | Fixed | `64b8dd9` | `/intelligence` and `/portfolio` use the same sign-in guard as the dashboard and agent builder: a signed-out visitor, or one whose token the backend rejects, goes to `/login` before any page content shows or any backend call is made. `/intelligence` is admin-only, like the dashboard's Intelligence view, and other roles go to `/dashboard`. The `/mirror` endpoints behind the Intelligence page also require a signed-in user now (`d67f361`, QA-012). |
| QA-033 | Partly fixed | `9e55ae3` | FinBERT and bge-m3 load on first use, off the event loop, not at import. Offline, sentiment is still neutral and the demo embedder still falls back to a constant vector. |
| QA-009 | Fixed | `f4db43f` | The llama.cpp stream parser follows llama-server's SSE format (checked against llama.cpp source); mid-stream model errors reach the UI as errors; SSE output is valid JSON for any token. All four chat surfaces return replies. |
| QA-008 | Fixed | `1c64685` | The lifecycle socket no longer crashes; it reports `complete` only once the result is readable, reports crashed or revoked tasks as `failed`, and releases its Redis subscription on disconnect, timeout or Redis outage. The Neural Audit renders a result in about 1 s with a JSON-capable model. |
| QA-052 | Fixed | `1c64685`, `21f891f` | nginx forwards WebSocket upgrades on `/api/ws/`. The chat stream sends `X-Accel-Buffering: no`, so nginx passes tokens through as they arrive (checked through the repo's nginx config: 0.5 s apart with the header, all at the end without it). |
| QA-010 | Fixed | `21f891f`, `87b21b9` | Compose runs llama.cpp's `llama-server` (pinned `server-b11243`) on the downloaded LFM2.5-1.2B-Thinking GGUF; the canned mock moved to `docker-compose.mock-llm.yml`. The backend uses the server's chat route, so the model's chat template applies, removes `<think>` reasoning from answers, caps thinking at half of `n_predict`, and sends a JSON schema with every JSON request. Verified against `llama-server` built from the same tag, with a small LFM2-architecture GGUF and both template variants: chat, chat stream, strategy and a full forecast. The real 730 MB GGUF could not be downloaded in the sandbox. |
| QA-054 | Fixed | `21f891f`, `87b21b9` | The critic runs on the local model with a JSON schema when no Gemini key is set (an old placeholder key counts as unset) and when Gemini fails, instead of calling a nonexistent Ollama. Its score is clamped to 0–1. |
| QA-051 | Fixed | `21f891f`, `94e7794`, `620f357`, `402fc08` | Postgres and Redis are no longer published on the host. The model server, backend and frontend are published on `127.0.0.1` only, so nginx (80/443) is the only service other machines can reach; the app reaches everything on the compose network. The backend runs without `--reload`, and the backend and worker run the code built into their image instead of mounting the source. The default database password and password-less Redis remain, now reachable only on the compose network. |
| QA-024 | Fixed | `7c49faf` | The Gemini key is sent in a request header instead of the URL, so it no longer appears in logs or error text, and the critic's user-visible failure text names only the error type. Calls go to the requested model or `GEMINI_MODEL` (default `gemini-flash-latest`) instead of the retired `gemini-pro`, and JSON calls request a JSON response. The settings dialog no longer collects a Gemini key in the browser and clears any stored copy. Rotate any Gemini key configured before this change. |
| QA-040 | Partly fixed | `7c49faf`, `be73a3f` | No secrets are kept in browser storage any more: the Gemini and Alpaca key fields are gone from the settings dialog, which clears copies stored by earlier versions; the keys are read only from the server's environment. The unused llama.cpp URL setting and the missing save feedback remain. |
| QA-041 | Fixed | `be73a3f` | The Alpaca view asks the server whether it is configured and, if not, says which server settings to add, instead of pointing to the settings dialog. |
| QA-047 | Fixed | `8f7f518` | The wallet stack (wagmi, viem, RainbowKit) and the three Connect Wallet buttons are removed, as plan GC-08 decided: no feature used them, and wagmi 1 does not support React 19. Page loads open no wallet connections, and the browser crawl of every page and view shows no page errors (3 per page load before). |
| QA-055 | Fixed | `8f7f518` | The `pino-pretty` warning came from the WalletConnect logger and is gone with the wallet stack. `/dashboard` transfers 236 kB of JavaScript on load, down from 820 kB (both measured in the browser, compressed, cache disabled; Next 16 no longer prints first-load sizes). |
| QA-012 | Partly fixed | `d67f361` | Every `/mirror` route (`GET /mirror/competitors`, `POST /mirror/analyze/{id}`) requires a signed-in user and answers 401 without a valid token; the requirement is on the router, so routes added later are covered too. `/demo/ingest_news`, `/demo/analyze`, `/strategy/generate`, `/intelligence/news` and the scanner still answer without a token. |
| QA-011 | Partly fixed | `0605196` | Only the admin and trader roles can place Alpaca orders through `/tools/call` (deny-by-default: only the read-only account and positions tools are open to every signed-in user); others get 403 before Alpaca is contacted. Order attempts are logged with user and role, but there is no stored audit trail. The UI now signs in for real (QA-003); keep `ALLOW_DEMO_AUTH` off, since with it on anonymous callers are admins. |
| QA-050 | Partly fixed | `21f891f`, `87b21b9`, `be73a3f`, `f62778e` | `.env.example` no longer ships a placeholder `GEMINI_API_KEY`, and the old placeholder no longer counts as a configured key; `LLAMA_CPP_HOST` points at the model server. The Alpaca names match the code (`ALPACA_SECRET_KEY`, plus `ALPACA_BASE_URL`), and the old `ALPACA_SECRET` name is still accepted. `ACCESS_TOKEN_EXPIRE_MINUTES` sets the sign-in session length. The Kalshi mismatch remains. |
| QA-053 | Partly fixed | `21f891f`, `87b21b9` | README and architecture docs describe the real model server and the mock override. The `frontend.md` and YC-plan points remain. |

The frontend was also upgraded after the test pass (`8f7f518`): Next.js 14.0.3 to 16.4.1 and React 18 to 19, on Node 24 LTS in all three Dockerfile stages (Node 18 and 20 are end of life), with an ESLint 9 flat config because `next lint` no longer exists. `npm run lint` passes with no warnings: the 10 mount-time effects that the new `react-hooks/set-state-in-effect` rule flagged were refactored afterwards, and the rule is an error again. `npm audit` on the frontend went from 47 vulnerabilities (1 critical, 28 high) to 10 (7 high, 3 moderate), all in build-time tools (Tailwind CSS 3 and the Next ESLint plugin), for which no fixed releases exist yet. A browser crawl of every page and dashboard view, and the sign-in checks, gave the same results as on Next.js 14, apart from the removed wallet button.

Regression gates 3 and 4 in §8 are now covered by automated tests (`tests/test_lifecycle_ws.py`, `tests/test_llama_cpp_stream.py`). Sign-in itself, the first half of gate 2, is covered by `tests/test_auth_session.py`; gates 1, 2, 5 and 6 remain open.
