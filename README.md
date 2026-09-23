# StudioLedger — AI Finance for Freelance Artists

A portfolio project: a full-stack finance coach for freelance artists who juggle **commissions, Etsy/Patreon sales, and content**. Log transactions and commissions; an LLM auto-categorizes entries, computes your **effective hourly rate**, flags cash-flow risk, and answers natural-language questions about your real numbers.

**Stack:** FastAPI · SQLModel · SQLite · React (Vite) · Recharts · OpenAI-compatible LLM (NVIDIA endpoint)

## Architecture

```
┌──────────────┐   /api (Vite proxy)   ┌──────────────────────┐
│  React SPA   │ ────────────────────► │  FastAPI              │
│  Dashboard   │                       │  /transactions        │
│  Transactions│                       │  /commissions         │
│  Commissions │                       │  /dashboard/summary   │
│  Chat        │                       │  /dashboard/insights  │
└──────────────┘                       │  /cashflow/radar      │
                                       │  /chat                │
                                       │        │              │
                                       │  stats.py (pure      │
                                       │  python math)         │
                                       │        │              │
                                       │  SQLite               │
                                       │  services/llm.py ───► NVIDIA LLM
                                       └──────────────────────┘
```

Key design choices:

- **All money math is plain Python.** Net income, hourly rate, burn rate, and the 30-day cash-flow forecast are computed deterministically. The LLM only *narrates* numbers — so the app stays correct even if the model is down.
- **LLM provider is swappable.** The OpenAI SDK is pointed at any OpenAI-compatible endpoint via 3 env vars; `FallbackClient` degrades to keyword heuristics on any API error.
- **Single-user, no auth** — kept deliberately out of scope (see next steps).

## Getting started

### 1. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # add your LLM_API_KEY
python seed.py         # optional: load the demo dataset
uvicorn app.main:app --reload
```

Open the auto-generated API docs at <http://localhost:8000/docs>.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173
```

Vite proxies `/api/*` to `localhost:8000`, so the two run together with zero config. The LLM defaults to the **NVIDIA** endpoint (`https://integrate.api.nvidia.com/v1`) with the **`openai/gpt-oss-20b`** model — change these in `backend/.env` if you use a different provider.

### 3. Tests

```bash
cd backend
pytest                # 31 tests, offline (LLM mocked)
ruff check . && ruff format --check .
```

## Feature tour

- **Auto-categorization** — adding a transaction without a source/category asks the LLM to tag it (badge shown in the table).
- **Effective $/hr** — log hours per commission; the app divides paid income by hours. The dashboard surfaces your rate for pricing decisions.
- **Net vs. gross** — Etsy/PayPal `fee_amount` is subtracted, so "net" reflects what you actually keep.
- **Cash-flow radar** — balance + committed (agreed/in-progress) commissions vs. your 30-day burn, with a healthy/moderate/low flag and an AI narrative.
- **AI chat** — POST a question; the backend bundles the computed metrics and asks the LLM to answer strictly from those figures.

## API

Interactive docs at `/docs`. Main routes:

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/transactions` | List (filters: source, category, type, date range) / create (auto-categorizes) |
| PATCH/DELETE | `/transactions/{id}` | Edit / delete |
| GET/POST | `/commissions` | Log commission hours / list all |
| GET | `/dashboard/summary` | Balance, per-source net, trend, top merchants, fees, $/hr |
| POST | `/dashboard/insights` | LLM narrative over the summary |
| GET | `/cashflow/radar` | 30-day forecast metrics |
| POST | `/cashflow/radar/insights` | LLM cash-flow narrative |
| POST | `/chat` | `{"question": "..."}` → computed answer |

## "Next steps" (good interview material — deliberately not built)

- Multi-user auth (the roadmap one: sessions, per-user data)
- Bank/Plaid sync instead of manual entry
- Tax-ready reporting (self-employment, deductible supplies)
- Invoice generation + payment link per commission
- Code-split the frontend (Recharts makes the bundle ~600 kB)

## Notables

- `pytest` suite uses a deterministic `FakeLLM` — fast, offline, no tokens spent.
- CI-ready: `ruff` lint + `pytest` both pass from the repo root.
- Deploy targets: Render (backend) + any static host (frontend, served behind one `/api` reverse proxy).