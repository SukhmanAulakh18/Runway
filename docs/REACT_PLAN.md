# Runway React frontend: plan and rules

> **Status (Sat Nov 7, late): built.** `api.py` + `web/` (Vite, React 19, TanStack Query, Recharts; no Tailwind/shadcn).
> `api.py` calls `ui.context.build_context()`, the same function Streamlit uses, so both frontends show identical numbers.
> Screens: 01 Who's at risk · 02 Know the customer · 03 Stress test · 04 Make a plan · 05 Why trust it.
> Contract tests: `pytest -q tests/test_api.py` (answer key 3.4 / 4.0 / 3.4, 93172 Dec 2024, 404/422, watchlist 14/50).
>
> ```bash
> cd web && npm install && npm run build && cd ..   # once, or after any web/ change
> uvicorn api:app --port 8000                        # one server: API + dashboard at http://localhost:8000
> # live-reload while editing the UI: `cd web && npm run dev` (http://localhost:5173, proxies /api to :8000)
> ```

The **engine stays in Python**. React only draws. `api.py` (FastAPI) sits between them.
**Streamlit stays as the backup demo** until React passes the midnight checkpoint.

```
data/*.csv → engine.py (all maths) → api.py (JSON) → React app (web/) → judge
                                   ↘ Streamlit app (backup)
```

## Hard rules (same as CLAUDE.md, plus three)
1. React never calculates money. If a screen needs a number, ask P1 for an engine function, then an API field.
2. `api.py` never calculates either. It filters by date, calls engine, serialises.
3. The standard runway on screen must match the README answer key: 20111 → **3.4 / 4.0 / 3.4** for the three README twists.
4. **Midnight go/no-go.** React must run the full live twist (account input → twist card → both runways → plan) on 5 accounts with no errors. If not, demo Streamlit and show React as "advisor UI preview".

## Run it
```bash
# backend (repo root)
pip install -r requirements.txt
uvicorn api:app --reload --port 8000        # docs: http://localhost:8000/docs

# frontend (new folder web/ in the repo)
npm create vite@latest web -- --template react-ts
cd web && npm i
npm i @tanstack/react-query recharts framer-motion clsx lucide-react cmdk
npx shadcn@latest init                      # Tailwind + shadcn/ui components
npx openapi-typescript ../openapi.json -o src/api.d.ts   # typed API, no guessing field names
```
In `web/vite.config.ts` add `server: { proxy: { "/api": "http://localhost:8000" } }`.

## API (full spec in openapi.json, live docs at /docs)
| Method | Path | Gives | Screen |
|---|---|---|---|
| GET | `/api/health` | ok, AI backend | header |
| GET | `/api/accounts` | all account ids | search / Cmd+K |
| GET | `/api/customer/{id}?asof=YYYY-MM` | judges' numbers, our numbers, trough, loan, flags data, monthly history, Kalman, what happened next | Know |
| POST | `/api/shock/{id}` `{scenario, asof}` | standard + realistic runway, why they differ, Monte Carlo bands, survival %, judge check | Shock |
| POST | `/api/plan/{id}` `{scenario, asof, max_cut_share, pessimistic}` | milestones, backup levers, optimiser cut schedule | Plan |
| GET | `/api/watchlist?asof=&early_only=true&limit=50` | ranked accounts + reasons + Time Machine reveal | Watchlist |
| POST | `/api/portfolio` `{scenario}` | % of all customers still above zero per month | Bank view |
| POST | `/api/twist` `{text}` | parsed shock settings + "AI"/"rules" | Shock |
| POST | `/api/write-plan` `{facts}` | verified plan text | Plan |
| GET | `/api/evidence` | every finding | Why trust it |

`asof` cuts the data at that month for **every** number (fixes the Time Machine lookahead in the Streamlit version). Use `2023-12`, `2024-12`, or omit for today.

## Screens and the "fancy" that also scores points
| Screen | Must have | Fancy (only after must-have works) |
|---|---|---|
| Shell | account search, Today / Dec 2024 / Dec 2023 switch, **Demo mode** button (Dec 2024 + 93172) | Cmd+K palette to jump to any account; smooth page transitions |
| Know | one-sentence summary, 3 cards (standard, realistic, trough), judges' numbers table | count-up numbers; balance chart with the dip shaded between average and lowest; Time Machine "what happened next" reveal animation |
| Shock | twist-card box → chips to confirm → both runways side by side; presets; sliders | runway numbers animate when the shock changes; Monte Carlo fan chart (p10–p90 band, median line, overdraft line, "EI ends" marker) drawing in left to right; "chance they make 6 months" as a gauge |
| Plan | milestones with progress, backup levers ranked, optimiser result sentence | progress rings; cut-schedule bars under the protected path; "Download plan" |
| Watchlist | top 50 table, reasons, click → customer | sparkline of each account's balance; reveal column flips to yes/no in Time Machine mode |
| Bank view | standard vs realistic curves | shade the gap between them and label it "customers the standard formula misses" |
| Why trust it | 3-year backtest bars, overdraft → default chart, limits | scroll story: one finding per section |

Design: orange `#e86f00` = ours, slate `#8a94a6` = standard. One accent. Big serif numerals only for the two runways. Every chart title states the takeaway. Sentence case.

## Who does what
| Person | Owns |
|---|---|
| P1 | `engine.py`, `api.py` (any new field), reviews |
| React A | shell, routing, API client + types, Know, Demo mode |
| React B | Shock (twist card, chips, sliders, runway cards, fan chart) |
| React C | Plan, Watchlist, Bank view, Why trust it |
| Streamlit owner | keeps Streamlit working as the backup; the Kalman fix; screenshots |

## Timeline
| By | Done |
|---|---|
| 5:00 PM | **Claim Google Cloud credits** (5th floor, C506, closes 5 PM) |
| 7:00 PM | API running for everyone; React shell + Know shows real data |
| 8:00 PM | Devpost draft + Tangerine track (hard deadline) |
| 10:00 PM | Shock tab end to end; numbers match 3.4 / 4.0 / 3.4 |
| **12:00 AM** | **Go/no-go checkpoint** (rule 4) |
| 2:00 AM | Feature freeze. Plan, Watchlist, Evidence done or cut |
| 9:00 AM | Deploy to Cloud Run (one container: FastAPI serves the built React files); test the link logged out |
| 11:00 AM | Submit |

## Claude Code prompt for each React engineer (start of session)
```
Read CLAUDE.md and REACT_PLAN.md. I own <files>. The backend is api.py; types are in web/src/api.d.ts
(generated from openapi.json). React never calculates money: display API fields only, format with $ and commas.
Build <screen> per the "Must have" column first. Use TanStack Query for API calls, shadcn/ui components,
Recharts for charts, Framer Motion only for number and chart transitions. Plan first, list files, wait for go.
```
