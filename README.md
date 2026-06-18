# Smart Grid Operations Dashboard

A React dashboard for a smart grid load balancing & forecasting system: real-time
substation monitoring, demand forecasting, alerting, and manual load-balancing controls.

It runs standalone right now against realistic mock data, and is structured so that
pointing it at your real API later takes one environment variable change — no
component code needs to change.

---

## 1. Run it locally

```bash
npm install
cp .env.example .env
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). You'll see live-updating
substation loads, a 24h trend chart, a forecasting page, alerts, and manual controls —
all backed by an in-memory mock "backend" in `src/services/mockData.js` that ticks every
3 seconds and behaves like a real grid (loads drift, thresholds trigger alerts, control
actions actually move load between substations).

## 2. Project structure

```
src/
  services/
    api.js          # the ONLY file that calls the grid network — defines the full API contract
    mockData.js      # mock grid backend implementing that exact contract
    authApi.js        # the ONLY file that calls auth endpoints — defines the auth contract
    mockAuth.js         # mock auth backend (persists to localStorage, not a real implementation)
  context/
    AuthContext.jsx     # user session state, available anywhere via useAuth()
  hooks/
    useLiveGrid.js   # single shared subscription to live node/alert state
  components/        # Sidebar, Header, StatCard, StatusBadge, GridPulseStrip,
                       # DashboardLayout (sidebar+header shell), ProtectedRoute (auth guard)
  pages/
    Home.jsx            # public landing page
    Login.jsx             # sign in
    Register.jsx           # create account
    Overview.jsx      # monitoring: KPIs, topology strip, load trend, substation table
    Forecasting.jsx    # forecast chart with confidence band + accuracy stats
    Alerts.jsx         # active/resolved alerts, acknowledge action
    Controls.jsx        # shift/shed load, auto-rebalance, enable/disable substations, action log
```

### Routes

| Path | Access | Page |
|---|---|---|
| `/` | public | Home / landing |
| `/login` | public | Sign in |
| `/register` | public | Create account |
| `/dashboard` | protected | Overview |
| `/dashboard/forecasting` | protected | Forecasting |
| `/dashboard/alerts` | protected | Alerts |
| `/dashboard/controls` | protected | Controls |

`ProtectedRoute` redirects unauthenticated visitors to `/login` and sends them back to
whichever dashboard page they originally asked for once they sign in.

**Demo login:** `demo@gridops.io` / `demo1234` (seeded automatically), or just register
a new account — both work immediately since auth is mocked in `localStorage` for now.

Every page receives data through props from `App.jsx`, which itself only talks to
`src/services/api.js` and `src/services/authApi.js`. That's the seam: build your backend
to match the contracts documented at the top of those two files, flip one flag, and the
whole UI — including login/register — is live.

## 3. Connecting your real APIs

In `.env`:

```
VITE_USE_MOCK=false
VITE_API_BASE_URL=https://your-api.example.com
```

That covers both the grid API and the auth API — `authApi.js` follows the exact same
`USE_MOCK` switch as `api.js`. The auth contract (register/login/logout/me) is documented
in full at the top of `authApi.js`. Important: the mock auth stores plaintext passwords in
localStorage purely so the demo works without a backend — your real backend must hash
passwords and should use httpOnly cookies or short-lived JWTs instead of a token sitting
in localStorage.

## 4. Suggested order for building the backend

0. **Auth** (`/api/v1/auth/register`, `/login`, `/logout`, `/me`) — do this first if you
   want real accounts instead of the localStorage-based demo. Hash passwords, issue a
   JWT or session cookie, and the Login/Register pages need zero changes.
1. **`GET /api/v1/grid/nodes`** and **`GET /api/v1/grid/summary`** — get the Overview
   page showing real data first; it's the highest-value screen and the easiest to
   verify visually.
2. **`GET /api/v1/grid/load-history`** — powers the 24h trend chart. Start by just
   querying your time-series store (InfluxDB/TimescaleDB are common choices for this).
3. **`POST /api/v1/grid/nodes/:id/toggle`** and **`POST /api/v1/grid/balance`** — wire up
   Controls once you have real switching/dispatch logic to call into.
4. **`GET /api/v1/alerts`** + **`POST /api/v1/alerts/:id/acknowledge`** — this can start
   as simple threshold checks (load/capacity > 0.9) computed on read; move to a proper
   rules engine or anomaly-detection model later.
5. **`GET /api/v1/forecast`** — this is the hard part. A reasonable path:
   - Start with a naive seasonal baseline (same hour last week) just to unblock the UI.
   - Swap in a real model (Prophet, LSTM, or gradient-boosted trees on lag features)
     once you have enough historical load data.
   - Return `lower_bound_kw`/`upper_bound_kw` from your model's prediction intervals —
     the chart already renders the confidence band.
6. **WebSocket `/ws/live`** last — it's a pure optimization over polling
   `getNodes()`/`getSummary()` every few seconds, and the frontend already works either way.

## 5. Backend tech notes (your choice, just match the contract)

- **Python**: FastAPI is a strong fit — `websockets` support is built in, and pairs
  naturally with `pandas`/`scikit-learn`/`Prophet` for the forecasting endpoint.
- **Node**: Express or Fastify + `ws` for the WebSocket, if you want one language across
  stack.
- Either way, keep the forecasting model as a separate service/module from the
  request-handling code — you'll want to retrain and redeploy it independently of the
  API.

## 6. Build for production

```bash
npm run build      # outputs to dist/
npm run preview    # sanity-check the production build locally
```

`dist/` is static — deploy it to Netlify, Vercel, S3+CloudFront, or behind whatever
reverse proxy serves your API.

## 7. What's mocked vs. real right now

The mock backend (`mockData.js`) simulates: 8 substations across 4 regions, a daily
load curve with noise, threshold-based alert generation, and control actions that
actually shift numbers between nodes so the UI feels responsive. None of it persists —
refreshing the page resets state. This is intentional: it's a frontend scaffold, not a
substitute for your forecasting model or real telemetry.
