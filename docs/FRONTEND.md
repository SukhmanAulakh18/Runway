# FRONTEND.md: how the React app connects to the logic

This is the guide for whoever (or whichever Claude Code session) builds the React app in `web/`.
It says what to call, what comes back, and how to show it. Read `docs/REACT_PLAN.md` for the stack,
the screens and the timeline; this file is the wiring.

```
data/*.csv ──► engine.py (all maths) ──► api.py (JSON, no maths) ──► web/ (React, display only)
```

> **Status (Nov 7):** the engine is the focus right now. `api.py` and `openapi.json` are drafted and tested
> (16 contract tests pass on the real data, including the 3.4 / 4.0 / 3.4 answer key) but are **not in the repo
> yet**. Sukhman has the draft. Step 0 of frontend work is to add them back (plus `fastapi`, `uvicorn`, `httpx`
> in `requirements.txt` and `tests/test_api.py`), add the two fields in section 8 marked "engine ready", and regenerate
> `openapi.json`. Everything below describes that API.

## 1. Rules (break one and the numbers on screen stop matching the judges')

1. **React never calculates money.** No sums, ratios, percentages of money, rounding of runways or "months left" in the browser. If a screen needs a number the API doesn't give, ask P1 for an engine function plus an API field. Formatting is fine (`$12,345`, `3.4 months`, `55%`).
2. **Show runway labels, not raw numbers.** `runway: 120` is a cap that means "no shortfall". Always show `label` (`"3.4 months"`, `"no shortfall (120+)"`, `"0 (buffer wiped out)"`). Use `runway` only to sort, animate or colour.
3. **Every call carries the same `asof`** (Time Machine). Omit it for today; `"2024-12"` or `"2023-12"` to rewind. The API cuts the data for every number, so never mix a today response with a Dec 2024 one on one screen.
4. **The standard runway for account 20111 must read 3.4 / 4.0 / 3.4** for the three README twists (job loss EI 55%; furnace = 1 month of spending; job loss + bills 15%). Check this before every demo.
5. **Wording:** "money in" / "money out" (not income / spending, except when quoting the judges' formula); "unlabelled outflows (purpose unknown)"; "no activity after YYYY-MM" (not "closed"); "household bills" (not "rent"). Sentence case. Orange `#e86f00` = ours (realistic), slate `#8a94a6` = standard.
6. **Don't claim "the trough beats the raw lowest balance"** (it didn't survive our own correction). `evidence.trough.head_to_head_2025` exists, but don't present it as a win.
7. **Two different "chances", never mix them up.** `overdraft_risk.p_12m` is a *calibrated forecast* ("X% chance of a first overdraft in the next 12 months if nothing changes", validated out of time). `simulation.p_survive_6` under a shock is a *scenario result*: write "X of 10 simulated futures last 6 months", never "X% chance". The raw simulation is about 8× too pessimistic as a forecast (see `evidence.sim_calibration`).

## 2. Run it

```bash
# backend, repo root (needs the Tangerine CSVs in ./data or RUNWAY_DATA=/path)
pip install -r requirements.txt
uvicorn api:app --reload --port 8000        # live docs: http://localhost:8000/docs
```

```bash
# frontend
cd web && npm run dev                       # vite, http://localhost:5173
```

`web/vite.config.ts`:
```ts
export default defineConfig({ plugins: [react()], server: { proxy: { "/api": "http://localhost:8000" } } })
```
Call relative paths (`/api/...`) everywhere. In production FastAPI serves the built files, so the same paths work.

`npx openapi-typescript ../openapi.json -o src/api.d.ts` types the **requests** (scenario fields, query params).
The API has no response models, so responses come out as `unknown`. Use the interfaces in section 5 instead
(copy them into `web/src/types.ts`).

## 3. App state: three things drive everything

| State | Type | Default | Set by |
|---|---|---|---|
| `acct` | `number` | `20111` | search box / Cmd+K / watchlist row click / Demo mode |
| `asof` | `"2024-12" \| "2023-12" \| null` | `null` (today, Dec 2025) | Today / Dec 2024 / Dec 2023 switch |
| `scenario` | `Scenario` (section 5) | all defaults = no shock | presets, twist card, sliders |

Put them in the URL (`/customer/20111?asof=2024-12`) so a refresh or shared link keeps the view.
**Demo mode** = `acct = 93172`, `asof = "2024-12"`, open Know.

TanStack Query keys: `["customer", acct, asof]`, `["shock", acct, asof, scenario]`,
`["plan", acct, asof, scenario, maxCutShare, pessimistic]`, `["watchlist", asof, earlyOnly, limit]`,
`["portfolio", asof, scenario]`, `["evidence"]`, `["accounts"]`. Use `placeholderData: keepPreviousData`
on shock/plan so slider drags don't flash empty cards. Debounce sliders about 250 ms.

## 4. Endpoints

| Method + path | Body / query | Returns | Rough speed* |
|---|---|---|---|
| `GET /api/health` | | `{ok, ai, accounts}` | instant |
| `GET /api/accounts` | | `number[]` sorted ids (4,500) | instant |
| `GET /api/customer/{acct}` | `?asof=` | `Customer` | ~0.2 s (first call per `asof` builds a table, ~1-2 s) |
| `POST /api/shock/{acct}` | `{scenario, asof}` | `ShockResult` | ~50 ms |
| `POST /api/plan/{acct}` | `{scenario, asof, max_cut_share=0.5, pessimistic=true}` | `PlanResult` | ~0.4 s |
| `POST /api/write-plan` | the `facts` object from `/api/plan`, unchanged | `{text, source}` | 0.01 s offline, 1-3 s with Gemini |
| `POST /api/twist` | `{text}` | `{settings: Scenario-subset, source: "AI" \| "rules"}` | 0.01 s offline, 1-3 s with Gemini |
| `GET /api/watchlist` | `?asof=&early_only=true&limit=50` | `Watchlist` | first call per `asof` ~3-5 s, then cached |
| `POST /api/portfolio` | `{scenario, asof}` | `PortfolioPoint[]` | ~1 s (all accounts) |
| `GET /api/evidence` | | `Evidence` (from `evidence.json`) | instant |

*Rough guide only: simulate (~10 ms) and optimiser (~0.3 s) are measured in HANDOFF; the rest are estimates. Time them on the real data.

**Errors** come as `{detail: string}`:
- `404` account not found, or **no data up to `asof`** (e.g. an account opened in 2025 viewed in Dec 2024 mode). Show `detail` and offer "switch to Today".
- `422` bad input: `asof` not `YYYY-MM` within 2020-01..2025-12, bad scenario field, `facts` not from `/api/plan`.

Prewarm on app load (fire and forget): `/api/watchlist?asof=2024-12` and `/api/customer/93172?asof=2024-12`, so Demo mode is instant.

## 5. Types (copy into `web/src/types.ts`)

Numbers are dollars per month unless the name says otherwise. Any `number` field can be `null` when the
engine had nothing to compute (NaN never reaches the browser).

```ts
export type Asof = "2024-12" | "2023-12" | null;

// Request: every field optional; omitted = default (no shock).
export interface Scenario {
  job_loss?: boolean;              // default false
  ei_rate?: number;                // 0.55
  ei_months?: number;              // 6 (EI stops after this; standard formula pays forever)
  ei_cap?: boolean;                // true: 2026 max $729/week
  income_cut?: number;             // 0..1, pay cut without job loss
  bills_increase_pct?: number;     // 0.15 = household bills +15%
  spending_increase?: number;      // $/month, negative = a cut
  one_off_cost?: number;           // $ one time (repair)
  one_off_months_of_spending?: number; // 1.0 = "a full month of typical spending"
  return_to_work_month?: number | null; // simulation only
  employment_share?: number;       // 1.0
}

export interface Runway {          // standard (judges') runway
  runway: number;                  // months, 1 decimal, 120 = cap. Display `label`.
  label: string;
  income_after: number; spending_after: number; one_off: number;
  buffer_left: number; monthly_gap: number;
}
export interface RealisticRunway {
  runway: number; label: string;
  income_after: number; spending_after: number; one_off: number;
  usable_buffer: number;           // buffer minus one-off minus typical in-month dip
  monthly_gap: number;
  ei_monthly: number; ei_capped: boolean;
  gap_after_ei: number | null;     // gap once EI stops (job loss only)
}
export interface Profile {         // judges' numbers (README definitions)
  account_id: number;
  income: number;                  // I, median money in
  fixed_costs: number;             // F
  spending: number;                // S, median money out
  buffer: number;                  // B, mean avg daily balance, last 6 months
  household_bills: number;         // H
  loan_payment: number;            // P
  months_of_data: number;
  breakdown: Record<string, number>; // medians per category (cash_deposits, transfers_in, pension_in, ...)
}
export interface Realistic {       // our numbers (last 12 months)
  account_id: number; income: number; protected_income: number; earned_income: number;
  spending: number; essential: number; flexible: number;   // flexible = unlabelled outflows
  transfers_out_other: number; loan_payments: number; household_bills: number;
  buffer: number; dip: number; window_months: number;
}
export interface Trough {
  ltr: number;                     // lowest balance / average balance, last 6 months (show as %)
  min_balance: number; avg_balance: number;
  pct_rank: number | null;         // 0 = most fragile; null when too new to score
  bottom_10: boolean;              // riskiest 10%
  neg_days_recent: number; scorable: boolean; n_months: number;
}
export interface Loan {
  loan_start: string; amount: number; monthly_payment: number; duration_months: number;
  status: "A" | "B" | "C" | "D"; status_meaning: string; defaulted: boolean;
  months_before_loan: number; overdrawn_before_loan: boolean;
  pre_loan_ltr: number | null; pre_loan_min_balance: number | null;
  payment_to_money_in: number | null; ever_overdrawn: boolean;
}
export interface MonthRow {
  month: string;                   // "YYYY-MM"
  money_in: number; money_out: number; avg_daily_balance: number; min_balance: number;
  month_end_balance: number; days_below_zero: number;
  cash_deposits: number; transfers_in: number; pension_in: number; interest_in: number;
  household_bills: number; insurance: number; loan_payments: number;
  cash_withdrawals_genuine: number; card_withdrawals: number; transfers_out_other: number; bank_fees: number;
}
export interface Customer {
  account_id: number; asof: string | null;
  owner_age: number | null; joint: boolean;
  profile: Profile;
  standard_runway: Runway;         // no shock
  realistic: Realistic;
  realistic_runway: RealisticRunway; // no shock
  trough: Trough | null;
  loan: Loan | null;
  ever_overdrawn: boolean;
  last_activity: string;           // "YYYY-MM" -> "no activity after ..." if < asof (or < 2025-12)
  history: MonthRow[];             // only months <= asof
  kalman: { month: string[]; net: number[]; level: number[]; sd: number[];
            q: number; obs_sd: number; drift_sd: number | null; has_trend: boolean; band_from: number };
  overdraft_risk: { p_12m: number; p_raw: number; validated_population: boolean }; // add to api (section 8)
  what_happened_next?: { month: string; days_below_zero: number; min_balance: number; avg_daily_balance: number }[]; // only when asof set
}
export interface Simulation {      // Monte Carlo, 2,000 paths, 24 months
  months: number[];                // 1..24
  p10: number[]; p50: number[]; p90: number[]; // balance bands
  dip: number;                     // overdraft line = typical in-month dip
  start: number;
  p_survive_6: number; p_survive_12: number; // 0..1
  median_months_to_zero: number | null;
  insufficient_history: boolean;   // < 18 months: show a caution
  ee: number[]; pfe95: number[];   // expected / 95th pct exposure below zero
  n_paths: number; history_months: number;
}
export interface ShockResult {
  scenario: Required<Scenario>;    // what the engine actually used (echo it as chips)
  standard: Runway;
  realistic: RealisticRunway;
  why_different: string[];         // ready-to-show sentences
  simulation: Simulation;
  judge_check: { I: number; S: number; B: number; H: number };
}
export interface Milestone { name: string; target: number; need: number; done: boolean;
  months_steady: number | null; months_stretch: number | null }
export interface Lever { action: string; how: string; monthly_saving: number; runway: number; gain: number | null }
export interface Cushion { buffer: number; alert_level: number; top_up_now: number; last_balance: number; as_of: string;
  dip_day: number | null; dip_day_share: number | null; dip_day_reliable: boolean }
// optimiser also has share_of_futures_protected: number | null (round 3)
export interface PlanResult {
  cushion: Cushion;              // headline action (engine.cushion); add dip_table in the API for dip_day
  goal: { have: number; monthly_gap_on_ei: number; monthly_surplus: number;
          steady_saving: number; stretch_saving: number; milestones: Milestone[];
          benchmark_3mo_spending: number; deficit_to_close: number };
  backup: { base_runway: number; levers: Lever[] };   // gain null = reaches the 120 cap
  optimiser: { base_months: number; protected_months: number; horizon: number;
               cuts: number[]; total: number; avg_monthly_cut: number; max_monthly_cut: number;
               path: number[]; protected_path: number[]; dip: number; outcome: string };
  facts: Record<string, unknown>;  // opaque: POST it to /api/write-plan as is
}
export interface WatchRow {
  account_id: number; I: number; S: number; B: number; H: number;
  min_balance: number; avg_balance: number; neg_days_recent: number; n_months: number;
  ltr: number; scorable: boolean; ltr_pct_rank: number | null;
  realistic_runway_ei: number; answer_key_runway_ei: number;  // job loss on EI, months
  reasons: string;                 // "; "-separated -> split into chips
  last_activity: string; ever_negative: boolean | null;
  overdraft_next_12m?: boolean | null; // Time Machine reveal (asof only)
}
export interface Watchlist { asof: string | null; n_in_view: number; rows: WatchRow[];
  reveal?: { top_hit: number; base_rate: number } } // asof only: how many of the shown rows went overdrawn next year
export interface PortfolioPoint { month: number; standard: number; realistic: number } // share 0..1 still above zero
```

## 6. Screen by screen: which call, which field

### Shell
- On load: `GET /api/health` (show `ai` as a small "AI: offline / Gemini ..." tag), `GET /api/accounts` for search / Cmd+K.
- Time Machine switch sets `asof`; every query re-runs.

### Know the customer: `GET /api/customer/{acct}?asof=`
- Header: `Customer {account_id}`, `owner_age`, "joint" if `joint`.
- Three cards: standard = `standard_runway.label` (slate), realistic = `realistic_runway.label` (orange),
  trough = `trough.ltr` as % with "riskiest 10%" badge if `trough.bottom_10`, "too new to score" if `!trough.scorable`.
- Judges' numbers table: `profile.income / spending / buffer / household_bills / fixed_costs / loan_payment` (label rows I, S, B, H, F, P).
- Balance chart: `history[].avg_daily_balance` line and `history[].min_balance` line; shade between them (the dip). Mark `days_below_zero > 0` months red.
- Loan box (if `loan`): amount, status meaning, "granted while already overdrawn" if `loan.overdrawn_before_loan`.
- Time Machine reveal (if `what_happened_next`): months after `asof`, red where `days_below_zero > 0`.
- Risk card: `overdraft_risk.p_12m` as "X% chance of a first overdraft in the next 12 months". Show it only when `overdraft_risk.validated_population` is true; otherwise "already overdrawn before / too new to forecast".
- Kalman chart (optional): draw the band from index `kalman.band_from`; if `!kalman.has_trend`, caption "No trend: month-to-month swings are noise" (true for about half of accounts). Or leave it out.
- Warning chips: these are in the Streamlit `ui/context.py` flags but **not in the API yet**. Until P1 adds a `flags` field, show only ones that are plain field checks:
  `loan?.overdrawn_before_loan`, `ever_overdrawn`, `trough?.bottom_10`, `profile.household_bills === 0`, `joint`, `last_activity < (asof ?? "2025-12")`. Don't build the money comparisons in React; ask for `flags`.

### Take a shock: `POST /api/twist` then `POST /api/shock/{acct}`
1. Twist card box → `POST /api/twist {text}` → `settings`.
2. Show `settings` as editable chips ("job loss", "EI 55% for 6 months", "bills +15%"...) plus `source` ("read by AI" / "read by rules").
3. On confirm: `scenario = settings` (it drops straight in, same field names) → `POST /api/shock/{acct} {scenario, asof}`.
4. Show `standard.label` and `realistic.label` side by side, `why_different[]` as bullets under them.
5. Fan chart: x = `simulation.months`, band `p10..p90`, line `p50`, horizontal line at `simulation.dip` ("overdraft line"), vertical marker at `scenario.ei_months` if `scenario.job_loss` ("EI ends").
6. Gauge: `simulation.p_survive_6` labelled "share of 2,000 simulated futures that last 6 months" (rule 7: not "chance").
7. Judge check: `judge_check.I/S/B/H` in small print.

Presets (no API call needed to build them):
```ts
const PRESETS = {
  "Job loss, EI 55%":         { job_loss: true },
  "Furnace (1 month)":        { one_off_months_of_spending: 1.0 },
  "Job loss + bills 15%":     { job_loss: true, bills_increase_pct: 0.15 },
};
```

### Make a plan: `POST /api/plan/{acct}` then `POST /api/write-plan`
- **Headline (first thing on the tab): `plan.cushion`.** "Set overdraft protection or an auto-transfer of $`buffer`. Alert them when the balance drops below $`alert_level`." If `top_up_now > 0`: "Move $`top_up_now` to chequing now." If `dip_day_reliable`: "Their balance usually bottoms out around day `dip_day`." Bank line from `evidence.impact["2024-12"]`: "A buffer like this covered 79% of caught first overdrafts; 97% of it was never used." The job-loss sections below come second.
- Milestones: `goal.milestones[]` with `done`, `need`, `months_stretch ?? months_steady` ("about N months"). Progress ring = `goal.have` against `target` is a display ratio; prefer showing `need` as text and, if you draw a ring, ask P1 for a `progress` field.
- Backup levers: `backup.levers[]` (already in engine order); show `action`, `how`, `runway` months, `+gain` (or "120+" when `gain` is null).
- Optimiser: bars `optimiser.cuts[]` under the lines `optimiser.path` (without changes, slate dashed) and `optimiser.protected_path` (with cuts, orange), line at `optimiser.dip`.
  Sentence (same three cases as `ui/pages/plan.py`):
  - `protected_months > base_months`: "Without changes they stay out of overdraft for `base_months` months in a `outcome`. With the optimised cuts: `protected_months` months, averaging $`avg_monthly_cut`/month."
  - else if `base_months >= horizon`: "No cuts needed: they stay out of overdraft for all `horizon` months in a `outcome`."
  - else: "In a `outcome`, cuts of up to $`max_monthly_cut`/month can't protect month `base_months + 1`. They need a bridge first: claim EI immediately, ask the lender about a deferral, or arrange overdraft protection." (`base_months + 1` is a month index, not money.)
- "Write the plan" button → `POST /api/write-plan` with `plan.facts` → show `text`, small "written by `source`".
- Controls: `max_cut_share` slider (0.1-1.0, default 0.5), `pessimistic` toggle ("bad case" / "typical").

### Watchlist: `GET /api/watchlist?asof=&early_only=true&limit=50`
- Table of `rows`: account, `ltr` as %, `realistic_runway_ei`, `answer_key_runway_ei`, `reasons.split("; ")` as chips. Row click → `acct = row.account_id`, go to Know.
- `early_only=true` hides people already overdrawn (the point is early warning). Toggle to show all.
- Time Machine mode: column "went overdrawn next 12 months" = `overdraft_next_12m`; header line from `reveal`: "`top_hit` of these `rows.length` went overdrawn in the next year, vs `base_rate` (as %) of everyone".

### Bank view: `POST /api/portfolio {scenario, asof}`
- Two lines over `month` (0..24): `standard` (slate) and `realistic` (orange), y as %. Shade the gap: "customers the standard formula misses".

### Why trust it: `GET /api/evidence`
- `trough.by_year[]`: bars of `low10_rate` vs `rest_rate` per `predicted_year`, label `risk_ratio`× and `auc`.
- `confounders.adjusted.odds_ratio` + `or_ci95`; `multiple_testing.survive` of `tests`.
- `loans`: overdrawn → default numbers (`pre_loan_overdrawn`, `pre_loan_overdrawn_defaulted`, ...).
- Limits (from HANDOFF): 1990s Czech data re-dated (not Tangerine customers); money in is not pay (mostly cash); status D is partly "in debt" by definition; early-warning signal, not causal.

## 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4)

For 5 accounts (20111, 93172 + 3 random), in Today **and** Dec 2024:
- [ ] Know loads, no console errors.
- [ ] Twist card "laid off, EI 55% for 6 months, bills up 15%" → chips → both runways.
- [ ] 20111 standard runway reads 3.4 / 4.0 / 3.4 for the three presets (Today).
- [ ] 93172 in Dec 2024 reads "no shortfall (120+)" standard and shows the riskiest-10% badge.
- [ ] Plan shows milestones, levers, optimiser; "Write the plan" returns text.
- [ ] An account with no data before 2024-12 shows the 404 message, not a blank screen.

Backend tests that guard this contract: `pytest -q tests/test_api.py`.

## 8. Not in the API yet (ask P1, don't build in React)

| Want | Needs |
|---|---|
| Calibrated risk card | **engine ready:** `engine.overdraft_risk(acct, dd)` → add as `overdraft_risk` on `/api/customer` |
| Kalman "no trend" caption | **engine ready:** `has_trend`, `band_from` are already in `net_flow_filter` (so in `kalman`) |
| Warning chips with money comparisons ("less than one month saved", "medians say ... averages say ...") | `flags: string[]` on `/api/customer` (move the list from `ui/context.py` into engine) |
| Simulation as the headline, deterministic as "simple estimate" | handoff #4: same window for both in engine |
| Milestone progress ring % | a `progress` field per milestone |
| Sparklines in the watchlist | a compact balance series per row (or fetch `/api/customer` per visible row, lazily) |

## 8b. New backend pieces (round 3) the UI should use

| Use | Instead of |
|---|---|
| `ai.parse_twist_checked(text)` → `{settings, source, disagree, chips}`: show `chips` to confirm; highlight `disagree` fields in amber ("AI and rules read this differently, check it") | `ai.parse_twist` + hand-made chip text |
| `ai.plan_facts(plan, key_res, real_res, sim, opt, risk)` then `ai.write_plan(facts)` | the facts dict built inside `ui/pages/plan.py` (it still sends `chance_6_months_pct`) |
| `optimiser.share_of_futures_protected` ("protects 93% of simulated futures") | assuming "bad case" = 90% |

## 9. Paste-ready Claude Code prompts (Streamlit now; same rules apply to React)

**P3, Plan tab leads with the cushion:**
```
Read CLAUDE.md. In ui/pages/plan.py only: make the first block of the tab a card from c.cushion (it also has
dip_day / dip_day_reliable). Text: "Set overdraft protection or an auto-transfer of $buffer. Alert them when
the balance drops below $alert_level." Add "Move $top_up_now to chequing now." only if top_up_now > 0, and "Their balance usually bottoms out around day
{dip_day}." only if dip_day_reliable. Under it, one
caption from EV["impact"]["2024-12"]: "In 2025 a buffer like this fully covered {covered_in_full} of {caught} caught
first overdrafts; ${drawn_total} of ${limits_total} was ever used." Format $ with commas. No maths. Move the job-loss
milestones below it. Run pytest -q -m ui.
```

**P3, "chance" wording:**
```
Read CLAUDE.md and docs/CTO_REVIEW.md finding #6. In ui/pages/shock.py replace "Chance they make it 6 months: X%"
with "{round(p*10)} of 10 simulated futures last 6 months", and the 12-month one the same way. Don't use the word
"chance" for simulation results anywhere. Run pytest -q -m ui.
```

**P2, Know tab risk card (`c.risk` and `c.cushion` are already in the context):**
```
Read CLAUDE.md. In ui/pages/know.py add a card: "{p_12m:.1%} chance of a first overdraft in the next 12 months if
nothing changes" from c.risk, shown only if c.risk["validated_population"], else "Already overdrawn before or too new
to forecast". Caption: "Calibrated on 2024, checked on 2025". Remove the Kalman chart. Run pytest -q -m ui.
```
