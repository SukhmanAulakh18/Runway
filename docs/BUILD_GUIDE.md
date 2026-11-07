# Runway build guide: every part, step by step, with Claude Code

> **In this repo the base is already built.** Use this guide as the detailed spec for the maths (engine owners) and as background. Two differences from what follows: the app is split into `ui/pages/` (one file per tab, see `docs/ARCHITECTURE.md`), and there is no `reference/` folder because the working code is the repo itself. For tasks, use `docs/TASKS.md`.

Sheridan Datathon 2026 · Tangerine track · about 200 participants

This guide lets you build Runway one module at a time with Claude Code. Each module has:

1. what it does and why it scores points
2. the exact spec (function names, inputs, outputs)
3. the algorithm and stats, in plain English and formulas
4. edge cases
5. the tests that define "done" (in `tests/test_acceptance.py`, with numbers already verified on the real data)
6. a prompt to paste into Claude Code

Read Part A once, then build Part B in order.

---

## Contents

- Part A. Strategy and setup
  - A1. How we win against ~200 people
  - A2. What we're building (architecture)
  - A3. Tech stack and why
  - A4. How to work with Claude Code
  - A5. Build order and time budget
- Part B. The modules
  - M0 Project setup
  - M1 Data loading and audit
  - M2 Answer-key engine (the judges' formula)
  - M3 Realistic runway
  - M4 Liquidity Trough Ratio, watchlist, Time Machine
  - M4b Credit view and bank view
  - M5 Kalman filter
  - M6 Monte Carlo simulation and exposure profile
  - M7 Optimised cut schedule (linear programming)
  - M8 Plan generator
  - M9 Evidence engine (backtests, bootstrap, BH, confounders)
  - M10 AI layer (Gemini, offline parser, number verifier)
  - M11 Streamlit app
  - M12 Differentiators if you're ahead
- Part C. Reference
  - C1. Stats and algorithms cheat sheet
  - C2. Integration contract
  - C3. Submission checklist
  - C4. Demo script, live-twist runbook, Q&A
  - C5. What can go wrong, and the fallback

---

# Part A. Strategy and setup

## A1. How we win against ~200 people

**How we're judged**
- **Weights:** Discovery 35%, Data Use 25%, Communication 25%, Impact 15%. The event says you're judged "on the strength of your insight and how well you communicate it, not on how much you built."
- **The Tangerine table, about 5 minutes:**
  - 1 min: pitch the engine and the biggest finding
  - 3 min: live twist. A judge picks an `account_id`, reads a twist card, and you run it live.
  - 1 min: questions
- **Judges** come from banks and big tech (Scotiabank, RBC, CIBC, Sun Life, OpenAI, Meta, IBM and others). Expect sharp questions on leakage, sample size and causation.

**What most teams will do:** rebuild the three required parts, add a chatbot that does the maths, show one runway number, and say "AI-powered".

**What wins, and what we have:**

| Score | What judges want | What we bring |
|---|---|---|
| Discovery 35% | Something non-obvious, backed by evidence | The **Liquidity Trough Ratio**: customers who look healthy on average but dip near zero. Flagged accounts had **14.6×** the risk of a first overdraft; the result repeats in 2023, 2024 and 2025. **And overdraft → default:** all 76 borrowers ever overdrawn defaulted, 27 loans went to people already overdrawn (all defaulted), and the trough measured *before* a loan predicts default (19.5% vs 3.2%). Plus the formula's blind spots: EI never ends, retirees get "laid off", the EI cap. |
| Data Use 25% | Cleaned, questioned, honest about limits | Out-of-time tests, bootstrap confidence intervals, a trap we caught (new accounts fake a trough), the judges' formula reproduced exactly, and limits stated up front. |
| Communication 25% | Story clear in the first minute | Open with account 93172 in the Time Machine. Two numbers side by side, with a plain "why they differ". A smooth live twist. |
| Impact 15% | Useful to a real user | An advisor workflow (watchlist → customer → shock → plan), and an optimised plan with real dollar amounts. |

**Three rules that decide the result**
1. **The live twist must never break.** Exact answer-key numbers, a twist reader that works offline, and sliders as a fallback.
2. **Lead with the finding, not the tech.** Judges rotate between tables.
3. **Every number has to be defensible.** Tests, intervals and stated limits.

## A2. What we're building (architecture)

```
Tangerine CSVs (./data)
      │
      ▼
engine.py  ── all maths ─────────────────────────────────────────────┐
  M1 load + audit                                                     │
  M2 answer-key runway (judges' exact formula)                        │
  M3 realistic runway (EI cap, pension kept, dip-aware)               │
  M4 trough ratio + watchlist + Time Machine                          │
  M5 Kalman filter (signal vs noise)                                  │
  M6 Monte Carlo (block bootstrap) + exposure profile                 │
  M7 optimiser (linear programming)                                   │
  M8 plan (goal milestones + backup levers)                           │
      │                         │                                     │
      ▼                         ▼                                     │
evidence.py (M9)          ai.py (M10)                                 │
backtests, CIs,           twist-card reader,                          │
→ evidence.json           plan writer, number check                   │
      │                         │                                     │
      └────────────┬────────────┘                                     │
                   ▼                                                  │
             app.py (M11) Streamlit: Watchlist · Know · Shock · Plan · Why trust it
```

**The golden rule: `app.py` never computes money.** One formula, one place, one test.

## A3. Tech stack and why

| Need | Tool | Why this one |
|---|---|---|
| Language | Python 3.11+ | All the maths libraries; fast to write |
| Tables | pandas, NumPy | Per-account group-bys over 185k monthly rows are instant |
| Optimisation | SciPy `linprog` (HiGHS) | Exact, fast linear programming; no extra install |
| Model testing | scikit-learn `roc_auc_score` | Standard, trusted AUC |
| Stats extras | statsmodels | Logistic regression for the confounder check; BH correction |
| Signal filtering | Our own Kalman filter (NumPy) | ~30 lines; shows understanding; no black box |
| App | Streamlit + Plotly | Web app in pure Python, interactive charts |
| AI | Google Gemini via `google-genai` (Vertex AI or API key) | Structured JSON output; Google Cloud credits cover it |
| Tests | pytest + Streamlit `AppTest` | Proves numbers; smoke-tests the UI headless |
| Repo | GitHub | Required for submission |

`requirements.txt`:
```
pandas>=2.2
numpy>=1.26
scipy>=1.11
scikit-learn>=1.4
statsmodels>=0.14
streamlit>=1.40
plotly>=5.20
google-genai>=1.0
pytest>=8
```

**Deliberately not used:**
- **XGBoost or other black-box models:** a simple ratio beat the runways, and bankers trust explainable signals.
- **Bloom filters, Kafka, Kubernetes:** not needed at this size; they're your "how would it scale?" answer.
- **Multi-agent frameworks:** more to break live.

## A4. How to work with Claude Code

**Setup, once:**
1. Create the repo folder. Put `CLAUDE.md`, `BUILD_GUIDE.md`, `pytest.ini`, `requirements.txt` and `tests/` in it.
2. Put the Tangerine CSVs in `./data`, and add `data/` to `.gitignore`.
3. Run `claude` in the repo folder. Claude Code reads `CLAUDE.md` automatically at the start of each session.

**For each module:**
1. Start fresh (`/clear`) so the context only holds this module.
2. Paste the module's prompt from this guide.
3. Let Claude Code plan first, then implement. Read the plan: does it follow the spec? Plan mode (Shift+Tab) is useful for this.
4. Run `pytest -q`. The module's tests must pass, and the earlier modules' tests must still pass.
5. Read the diff. Make sure it didn't edit a test to pass, add formulas to `app.py`, or commit data.
6. Commit: `git commit -m "M3 realistic runway: tests pass"`.
7. Write one sentence in `findings_log.md`: what it does and what could make it wrong. This becomes your Q&A prep.

**Check the kit first (2 minutes):** with the CSVs in `./data`, run `pytest -q -o pythonpath=reference`. All 29 tests should pass against the reference, which proves the tests and your data folder are right. Then run `pytest -q`; it fails until you build `engine.py` at the repo root. That's your progress bar.

**Two ways to build. Pick one per module:**
- **Fast path (recommended under time pressure):** the working reference implementation is in `reference/`. Tell Claude Code: "Use `reference/engine.py` as the starting point for module Mx, adapt it to the spec, and make the tests pass." Every line was written during this event.
- **Own-it path:** build the module from the spec without looking at the reference. The tests tell you when you've matched it. Use this for anything you want to explain deeply to judges (M2, M4 and M6 are the ones they'll ask about).

**If Claude Code goes off track:**
- **Tests fail and it wants to change a test:** say no. "Fix the code, not the test."
- **It adds a dependency:** ask why. Usually it isn't needed.
- **It over-engineers:** "Simplest version that passes the tests; no new abstractions."

## A5. Build order and time budget

| Module | Depends on | Fast path | Own-it path | Who |
|---|---|---|---|---|
| M0 Setup | nothing | 15 min | 15 min | Anyone |
| M1 Data | M0 | 15 min | 30 min | Logic lead |
| M2 Answer key | M1 | 20 min | 45 min | Logic lead |
| M3 Realistic runway | M2 | 20 min | 45 min | Logic lead |
| M4 Trough + watchlist | M2, M3 | 25 min | 60 min | Logic lead |
| M5 Kalman | M1 | 15 min | 30 min | Logic lead |
| M6 Monte Carlo | M3 | 20 min | 45 min | Logic lead |
| M7 Optimiser | M6 | 20 min | 45 min | Logic lead |
| M8 Plan | M3, M7 | 15 min | 30 min | Logic lead |
| M9 Evidence | M2–M4 | 30 min | 60 min | Logic or stats teammate |
| M10 AI | M3 | 30 min | 45 min | AI teammate |
| M11 App | all | 60 min | 2 h | Frontend teammate |
| M12 Extras | M11 | as time allows | | Everyone |

**Parallel plan for 3–4 people:**
- **Logic lead:** M1→M8.
- **Frontend teammate:** starts M11 immediately against `reference/engine.py` (same function names), then switches imports when your modules land.
- **AI teammate:** M10, plus the Devpost draft by 8 PM, then the video.
- **Stats teammate:** M9.

**Checkpoints:**
- **Sat 8 PM:** Devpost draft with the Tangerine track.
- **Sun 2 AM:** feature freeze.
- **Sun 11 AM:** submit.
- **Sun 1:00–2:30 PM:** demos. Someone must be at the table the whole time.

---

# Part B. The modules

## M0. Project setup

**Goal:** a repo where tests run and data loads, with nothing secret committed.

**Steps:**
1. Create the layout:
   ```
   runway/
     CLAUDE.md  BUILD_GUIDE.md  README.md  requirements.txt  pytest.ini  .gitignore
     engine.py  evidence.py  ai.py  app.py
     tests/test_acceptance.py
     reference/   (working implementation, optional)
     data/        (Tangerine CSVs, NOT committed)
   ```
2. Set up the `.gitignore`:
   ```
   data/
   .env
   __pycache__/
   *.pyc
   .venv/
   evidence.json   # optional: commit it if you want judges to see it without running
   ```
3. Create the environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run `pytest -q`. Everything fails at first; that's expected.

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M0. Set up the project skeleton exactly as described: folder layout,
.gitignore (data/, .env, caches), requirements.txt, pytest.ini (already provided; keep it). Create empty
engine.py, evidence.py, ai.py, app.py with a module docstring each. Do not write any logic yet.
Show me the tree and the output of `pytest -q --collect-only`.
```

## M1. Data loading and audit

**Goal:** load the Tangerine data reliably and know its quirks. This feeds Data Use (25%).

**Spec (engine.py):**
- `DATA = Path(os.environ.get("RUNWAY_DATA", <folder of engine.py>/"data"))`
- `END_OF_DATA = pd.Timestamp("2025-12-31")`, `RUNWAY_CAP = 120.0`
- `load(data_dir=DATA) -> dict` with:
  - `"monthly"`: `monthly_summary.csv` sorted by `account_id, month`. `month` stays a `YYYY-MM` string; string comparison works.
  - `"loans"`: `loans.csv` with `loan_start` parsed as a date, `loan_end = loan_start + duration_months` (use `pd.DateOffset(months=...)`), and `running_end_2025 = loan_end > END_OF_DATA`.

**Audit facts the tests check** (also put them in `findings_log.md`):
- 185,326 monthly rows, 4,500 accounts, 2020-01 to 2025-12. No missing values.
- Money-in parts (`cash_deposits + transfers_in + pension_in + interest_in`) add up to `money_in` exactly. Money-out parts add up to `money_out`.
- 682 loans, 76 defaulted. `running_end_2025` is True exactly for statuses C and D.
- About 75% of money in is cash deposits and 76% of money out is cash withdrawals. That's why we say "money in" rather than "income".

**Tests:** `test_data_loads`, `test_loans_running_matches_status`

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M1. Implement load() in engine.py exactly per the spec
(DATA from RUNWAY_DATA env var or ./data; monthly sorted by account_id, month; loans with loan_start parsed,
loan_end via pd.DateOffset(months=duration_months), running_end_2025 = loan_end > 2025-12-31).
Then write a short audit script audit.py that prints: row counts, date range, missing values per column,
component-sum checks, share of money_in from cash deposits and share of money_out from cash withdrawals,
loan status counts. Run `pytest -q -k "data_loads or loans_running"` and the audit script; show both outputs.
```

## M2. Answer-key engine (the judges' formula)

**Goal:** reproduce the judges' numbers exactly. This is what gets checked live in the 3-minute twist, so it must be perfect.

**The judges' definitions** (from `monthly_summary.csv`, per account):

| Symbol | Definition |
|---|---|
| I, typical money in | median of `money_in` (all the account's months) |
| F, fixed costs | median of `household_bills + insurance + loan_payments`; shown in part 1, not used in runway |
| S, typical spending | median of `money_out` |
| B, buffer | mean of `avg_daily_balance` over the account's **last 6 rows** sorted by month |
| H, household bills | median of `household_bills` |
| P, loan payment | `monthly_payment` if the loan is still running at the end of 2025, else 0 |

**Runway formula:**
```
buffer_left = B - one_off_costs
gap         = spending_after_shock - income_after_shock
if buffer_left <= 0:  runway = 0
elif gap <= 0:        runway = "no shortfall (120+)"
else:                 runway = min(buffer_left / gap, 120), rounded to 1 decimal
```

**How shocks apply:**
- Job loss with EI at 55%: income = 0.55 × I
- Household bills up 15%: spending = S + 0.15 × H
- Furnace costing a month of spending: one-off = 1.0 × S
- Combine freely.

**Spec:**
- `@dataclass Profile(account_id, income, fixed_costs, spending, buffer, household_bills, loan_payment, months_of_data, breakdown: dict = {})`
- `profile(acct, d) -> Profile`. Raises `KeyError` for an unknown account.
- `@dataclass Shock(income_factor=1.0, bills_increase_pct=0.0, spending_increase=0.0, one_off_cost=0.0, one_off_months_of_spending=0.0)`
- `runway(p, s=Shock()) -> dict` with keys `runway` (float), `label` (`"x.y months"`, `"no shortfall (120+)"` or `"0 (buffer wiped out)"`), `income_after`, `spending_after`, `one_off`, `buffer_left`, `monthly_gap`
- `TWISTS`: the three README twists as `Shock` objects
- `all_profiles(d) -> DataFrame` indexed by account_id, with columns `I, F, S, H, n_months, B, P` (vectorised)
- `runway_vec(df, s) -> Series`: the same formula, vectorised. It must equal the scalar version.

**Verified numbers (tests):**

| Item | Value |
|---|---|
| Account 20111 | I = 6,339.39 · S = 8,599.605 · B = 17,611.86 · H = 0 · P = 2,330.19 · F = 2,330.06 |
| 20111, job loss EI 55% | **3.4 months** |
| 20111, furnace (one month of spending) | **4.0 months** |
| 20111, job loss + bills 15% | **3.4 months** (H = 0, so the bills shock does nothing) |

Population checks:
- H = 0 for 1,225 accounts
- B ≤ 0 for 23
- B < S for 181
- I = 0 for 14
- S = 0 for 77
- 76 accounts have no activity after a month before 2025-12
- Median EI-55% runway is 8.6 months
- 75.5% of accounts show "no shortfall" under the furnace twist

**Edge cases to show in the UI, not crash on:**
- H = 0: "No labelled bill payments: a bills shock changes nothing in the standard formula."
- B ≤ 0: runway 0 before any shock.
- Account ends before 2025-12: "No activity recorded after YYYY-MM."

**Tests:** `test_profile_20111`, `test_twists_20111`, `test_runway_rules`, `test_vectorised_matches_scalar`, `test_edge_case_counts`, `test_twist_distribution`

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M2. Implement Profile, profile(), Shock, runway(), TWISTS,
all_profiles() and runway_vec() in engine.py exactly per the spec. This is the judges' answer key: follow
the formula literally (medians over all of the account's months, buffer = mean avg_daily_balance of the
LAST 6 ROWS sorted by month, loan payment only if running at end of 2025, round to 1 decimal, cap 120,
the three label strings). The vectorised version must equal the scalar version.
Run `pytest -q -k "profile_20111 or twists_20111 or runway_rules or vectorised or edge_case or twist_distribution"`.
Do not change tests.
```

## M3. Realistic runway

**Goal:** a second runway that fixes what the standard method misses, and explains the difference in plain English. This feeds Discovery and Communication.

**Why each fix exists:**
1. **Recent averages, not all-history medians.** Medians flag 26% of customers as having more going out than coming in. But for 97.5% of them, more actually came in on average, and 90% ended with a higher balance. Inflows are lumpy.
2. **Pension and interest keep coming after a job loss.** Only other inflows stop.
3. **Real EI cap.** EI is 55% of insurable earnings, up to **$729/week in 2026** (≈ $3,159/month = 729 × 52 / 12). For 57% of customers, 55% of money in exceeds the cap.
4. **Dip-aware buffer.** Overdraft happens at the month's low point, not at the average, so subtract the customer's typical monthly dip.
5. **Explicit pay-share assumption.** We can't see which deposits are wages, so a slider sets the share of non-pension inflows that a job loss stops (default 100%).

**Definitions (window = last 12 rows of the account, sorted by month):**

| Item | Definition |
|---|---|
| money in | mean `money_in` over the window |
| protected income | mean `pension_in + interest_in` |
| earned (other) income | max(money in − protected, 0) |
| money out | mean `money_out` |
| essential | mean `household_bills + insurance + loan_payments + bank_fees` |
| flexible (UI: "unlabelled outflows") | max(money out − essential, 0) |
| household bills | mean `household_bills` over the window |
| buffer B | same as the answer key: mean `avg_daily_balance`, last 6 rows |
| dip | **median** of (`avg_daily_balance − min_balance`) over the window |

**Shock under the realistic engine:**
```
if job_loss:
    wage          = employment_share × earned
    income_after  = protected + (earned − wage) + EI(wage)
    EI(x)         = min(ei_rate × x, 3159) if ei_cap else ei_rate × x
else:
    income_after  = protected + (1 − income_cut) × earned
spending_after  = money_out + bills_pct × household_bills + spending_increase
one_off         = one_off_cost + one_off_months × money_out
usable          = B − one_off − dip
if not a job loss (or ei_months = 0): same rules as the answer key
   usable <= 0 → 0; gap <= 0 → 120+; else min(usable/gap, 120), 1 decimal; label "120+ months" when capped
if a job loss, EI ENDS after ei_months (the standard formula pays it forever):
   gap_after_ei = gap + EI                      (EI stops; pension and non-wage inflows continue)
   t = usable / gap                              (months while on EI; ∞ if gap ≤ 0)
   if t ≤ ei_months: runway = t
   else: runway = ei_months + (usable − ei_months·max(gap,0)) / gap_after_ei   (120 if gap_after_ei ≤ 0)
   cap 120, round 1 decimal
```

Worked example (a test): earned 5,000, money out 4,000, buffer 20,000, dip 0. EI = 2,750, so the gap is 1,250. Paid forever: 20,000 / 1,250 = **16.0** months. Ending at 6: 6 + (20,000 − 7,500) / 4,000 = **9.1** months.

Why it matters across the bank: under the formula, 39% of customers last a year after a layoff; with EI stopping at month 6, 22%. 257 customers flip from "no shortfall" to running out.

**Pensioners:** 740 accounts (16%) get ~98% of money in from pensions, and every owner is 59+. Because pension counts as protected income, a layoff barely touches them in the realistic engine. `explain_difference` must say so when pension is over 50% of money in.

**Spec:**
- Constants: `EI_RATE = 0.55`, `EI_WEEKLY_MAX_2026 = 729.0`, `EI_MONTHLY_MAX = 729 * 52 / 12`, `WINDOW = 12`
- `@dataclass Realistic(account_id, income, protected_income, earned_income, spending, essential, flexible, transfers_out_other, loan_payments, household_bills, buffer, dip, window_months)`
- `realistic_profile(acct, d, window=12) -> Realistic`
- `@dataclass Scenario(job_loss=False, ei_rate=0.55, ei_months=6, ei_cap=True, income_cut=0.0, bills_increase_pct=0.0, spending_increase=0.0, one_off_cost=0.0, one_off_months_of_spending=0.0, return_to_work_month=None, employment_share=1.0)` with `to_answer_key_shock()`. Job loss maps to `income_factor = ei_rate`; otherwise `1 − income_cut`.
- `ei_benefit(earned, rate=0.55, cap=True) -> float`
- `realistic_runway(r, sc) -> dict` with keys `runway, label, income_after, spending_after, one_off, usable_buffer, monthly_gap, ei_monthly, ei_capped, gap_after_ei`
- `explain_difference(p, r, sc) -> list[str]`: plain sentences, generated from the numbers, for:
  - the median vs average mislabel
  - the EI cap biting
  - EI ending ("EI stops after N months. The standard formula keeps paying it forever.")
  - pension kept (or, if pension is over 50% of money in, "a layoff doesn't stop a pension")
  - the dip
  - recent money out differing from the median by more than 15%

**Verified numbers:**

| Scenario: job loss, EI 55%, 6 months, bills +15% | Answer key | Realistic |
|---|---|---|
| Account 20111 | 3.4 | **1.3** |
| Account 20133 | 4.2 | **1.4** |

- Account 20111, job loss: pay share 100% gives 1.3 months; 50% gives **3.4 months**.
- Out of time (features through 2024, predicting any overdraft in 2025, 3,668 accounts, 129 events): realistic AUC **0.841** vs answer key **0.783**, difference **+0.058** (95% CI +0.031 to +0.089).

**Tests:** `test_ei_cap_constant`, `test_realistic_examples`, `test_employment_share_assumption`, `test_median_mislabel`, `test_ei_cap_finding`, `test_realistic_ei_ends_after_6_months`

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M3. Implement the EI constants, Realistic, realistic_profile(),
Scenario (with to_answer_key_shock and employment_share), ei_benefit(), realistic_runway() and
explain_difference() exactly per the spec: window = last 12 rows; protected = pension+interest;
dip = MEDIAN of (avg_daily_balance - min_balance) over the window; EI capped at 729*52/12 per month;
usable buffer = B - one-offs - dip; label "120+ months" when capped. Explanations must be built from the
numbers, use the wording rules in CLAUDE.md, and never say "saving" or "income" loosely.
Run `pytest -q -k "ei_cap or realistic or employment or mislabel"`. Do not change tests.
```

## M4. Liquidity Trough Ratio, watchlist, Time Machine

**Goal:** the headline finding as a product feature. This is most of Discovery (35%) and the pitch moment.

**The idea in one line:** customers can look healthy on average and still dip close to zero. That low point predicts a first overdraft.

**Definition:**
```
LTR = (lowest end-of-day balance in the last 6 months) ÷ (mean of avg_daily_balance over the same 6 months)
if the mean is ≤ 0: LTR = −1 (already in trouble)
only score accounts with ≥ 12 months of history up to the as-of date
rank (percentile) among scorable accounts; the riskiest 10% are flagged
```

**Why the 12-month rule:** an account's first month starts at its first deposit, which fakes a deep trough. Without the rule, 98–100% of the watchlist's top 50 were accounts under 8 months old, and the Time Machine top 50 (as of Dec 2023) had only 1 first-time overdraft. With the rule: **7 of 50** as of Dec 2023 and **14 of 50** as of Dec 2024.

**Evidence (first-time overdrafts, accounts never below zero before):**

| Predicting | Accounts | First overdrafts | AUC | Riskiest 10% | Everyone else | Risk ratio |
|---|---|---|---|---|---|---|
| 2023 (from 2022) | 1,556 | 18 | 0.841 | 7.7% | 0.43% | 17.9× |
| 2024 (from 2023) | 2,213 | 34 | 0.844 | 9.0% | 0.70% | 12.8× |
| 2025 (from 2024) | 3,417 | 55 | **0.860** | **9.94% (34 of 342)** | **0.68% (21 of 3,075)** | **14.6× (95% CI 8.5–24.8)** |

- **Head to head, 2025, same accounts:**

  | Measure | AUC |
  |---|---|
  | Trough ratio | 0.860 |
  | Lowest balance, last 6 months | 0.840 |
  | Realistic runway | 0.759 |
  | Answer-key runway | 0.685 |

- **Windows:** 3, 6 and 12 months give 0.839, 0.860 and 0.859.
- **Account 93172:**
  - July–December 2024: average balance $18,502.57, lowest $238.49 (LTR 1.29%)
  - The standard runway said "no shortfall"
  - January 2025: 13 days below zero; February: 8; lowest −$717.24
  - As of Dec 2024 it ranks in the riskiest **1.6%** of scorable accounts

**Spec:**
- `LTR_WINDOW = 6`, `LTR_MIN_HISTORY = 12`
- `ltr_table(d, window=6, asof=None) -> DataFrame`, indexed by account. Columns: `min_balance, avg_balance, neg_days_recent, n_months, ltr, scorable, ltr_pct_rank` (NaN when not scorable). `asof="YYYY-MM"` keeps only months ≤ asof. This is the Time Machine.
- `liquidity_trough(acct, d, table=None, asof=None) -> dict`: `ltr, min_balance, avg_balance, pct_rank, bottom_10, neg_days_recent, scorable, n_months`
- `realistic_vec(d) -> DataFrame` with column `realistic_runway_ei`: the realistic runway under a job loss on capped EI, vectorised, for every account
- `watchlist(d) -> DataFrame`:
  - columns: `all_profiles[I,S,B,H]` joined with `ltr_table` and `realistic_vec`, plus `answer_key_runway_ei` (= `runway_vec` with income_factor 0.55), `reasons` (semicolon-joined) and `last_activity`
  - sort by `scorable` descending, then `ltr` ascending, then `realistic_runway_ei` ascending
- `what_happened_next(acct, d, asof, months=12) -> DataFrame`: `month, days_below_zero, min_balance, avg_daily_balance` for the months after asof

**Reason codes:**
- "Too new to score (N months)"
- "Balance dips close to zero (lowest 10% trough)"
- "N days below zero in last 6 months"
- "Under 3 months on EI"
- "Standard runway looks fine; realistic doesn't" (answer key ≥ 6 and realistic < 3)
- "No labelled bill payments"

**Time Machine logic (in the app):**
1. Pick as-of = Dec 2023 or Dec 2024.
2. Build the watchlist on data up to as-of.
3. Add a toggle, "Early warning only: hide accounts already below zero", on by default.
4. Keep scorable accounts only.
5. Reveal from later data whether each one went below zero in the next 12 months.
6. Show "Of these 50, N went below zero, against X% of all accounts in this view."

**Tests:** `test_trough_backtest_2025`, `test_trough_other_years`, `test_example_93172`, `test_trough_needs_12_months`, `test_watchlist_time_machine`

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M4. Implement ltr_table() (with asof for the Time Machine and the
12-month scorable rule; percentile rank only among scorable accounts), liquidity_trough(), realistic_vec(),
watchlist() (columns, reason codes and sort order exactly as specified) and what_happened_next().
Precompute over all accounts with group-bys, no Python loops over accounts except the reasons apply.
Run `pytest -q -k "trough or 93172 or watchlist"`. Do not change tests.
```

## M4b. Credit view and bank view

**Goal:** connect the early warning to the bank's real losses (loan defaults) and show the whole portfolio. Bank judges think in portfolios and credit risk.

**The finding behind it (Finding 5):**
- All **76 of 76** borrowers who were ever overdrawn defaulted; **0 of 606** who never were did. Statuses A and C are never overdrawn; B and D always are.
- **27 loans** ($3.48M, median $112K) went to customers **already overdrawn before the loan started**. **All 27 defaulted** (8 B, 19 D), versus 49 of the other 655 (7.5%). Fisher exact p = 1.6 × 10⁻²⁸.
- **Clean version, no leakage:** among 588 borrowers never overdrawn before their loan (6+ months of history), the trough ratio over the 6 months **before the loan** predicts default with AUC **0.775**. The lowest 20% defaulted **19.5%** (23 of 118) versus **3.2%**. Payment ÷ pre-loan money in: AUC 0.677. Both flags together: 26.3% of 38.
- **212 accounts without a loan have been overdrawn** (122 in 2025): the next credit risk.
- **Caveat:** status D means "in debt", so the D link is partly definitional. It holds for B, for the pre-loan overdrafts, and for the pre-loan trough.

**Spec:**
- `loan_risk(acct, d) -> dict | None` with keys:
  - `loan_start`, `amount`, `monthly_payment`, `duration_months`
  - `status`, `status_meaning`, `defaulted`
  - `months_before_loan`, `overdrawn_before_loan`
  - `pre_loan_ltr` and `pre_loan_min_balance` (last 6 months before the loan month)
  - `payment_to_money_in` (payment ÷ median money in before the loan)
  - `ever_overdrawn`
- `realistic_runway_vec(d, sc) -> Series`: the M3 realistic runway, including EI ending, for every account under one scenario. It must match the scalar version within 0.05.
- `portfolio_curve(d, sc, months=24) -> DataFrame(month, standard, realistic)`: the share of all accounts whose runway is at least each month. Under a 6-month-EI layoff, month 6 gives standard **0.649** and realistic **0.408**.

**Demo account 93172:**

| When | What happened |
|---|---|
| Sep 2024 | Balance dips to $238 |
| Dec 6, 2024 | $166,958 loan at $4,638/month, payment ÷ money in = **1.50** |
| Jan–Feb 2025 | 21 days below zero |
| Today | Status D |

**Tests:** `test_loan_risk_93172`, `test_overdraft_splits_loan_book`, `test_realistic_vector_matches_scalar`, `test_portfolio_curve`

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M4b. Implement loan_risk() (pre-loan trough and min balance from
the 6 months before the loan month, payment as a share of median pre-loan money in, overdrawn_before_loan),
realistic_runway_vec() (vectorised M3 realistic runway including EI ending; must match the scalar version
within 0.05) and portfolio_curve(). Run `pytest -q -k "loan_risk or overdraft_splits or vector_matches or portfolio"`.
```

## M5. Kalman filter (signal vs noise)

**Goal:** show the customer's underlying monthly cash flow with uncertainty. It's the principled answer to "median or average?", and a good talking point for quant judges.

**Model (local level):**
```
observation:  y_t  = μ_t + ε_t,    ε_t ~ N(0, σ²)
state:        μ_t  = μ_{t−1} + η_t, η_t ~ N(0, q·σ²)
y_t = monthly net flow (money_in − money_out)
```

**Filter, with σ² = 1 inside the loop (the "concentrated likelihood" trick):**
```
a = y_0, P = 1e7                       (diffuse start)
for t = 1..n−1:
    P_pred = P + q
    F      = P_pred + 1                 (innovation variance)
    v      = y_t − a                    (innovation)
    K      = P_pred / F                 (Kalman gain)
    a      = a + K·v
    P      = P_pred·(1 − K)
σ²_hat = mean(v²/F) over t ≥ 2         (skip the first innovation; it's dominated by the diffuse start)
logL(q) = −½ Σ log F − ½ (n−2) log σ²_hat
choose q from logspace(−5, 1, 61) maximising logL
level_t = a_t, sd_t = sqrt(P_t · σ²_hat)
```

**Spec:**
- `kalman_level(y, q_grid=None) -> dict(level, sd, q, obs_sd)`
- `net_flow_filter(acct, d) -> dict(month, net, level, sd, q, obs_sd, drift_sd)`, where `drift_sd = (level[-1] − level[-7]) / max(sd[-1], 1)`: the change over 6 months in filter standard deviations.

**How to read it:** if the chosen q is tiny, the underlying level is nearly flat and month-to-month swings are noise. That itself is evidence that medians and averages disagree because of lumpiness, not because of a trend.

**Tests:** `test_kalman_tracks_level` (a synthetic step from 0 to 1,000 plus noise is tracked)

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M5. Implement kalman_level() as a local-level Kalman filter in
plain NumPy with the diffuse start, the concentrated likelihood and the q grid exactly as specified, and
net_flow_filter() on monthly net flow. No statsmodels for this; we want to explain every line.
Add a docstring with the model equations. Run `pytest -q -k kalman`.
```

## M6. Monte Carlo simulation and exposure profile

**Goal:** turn "how many months?" into "what's the chance they make it?", with a range. This is your quant centrepiece.

**Method: block bootstrap Monte Carlo**
1. Take the customer's **last 24 months** (`money_in`, `money_out`, pension + interest, household bills).
2. Build **2,000 future paths** of 24 months each, by stitching together **random 3-month blocks** from that history. Blocks keep real month-to-month patterns, like a big deposit followed by withdrawals.
3. Apply the shock to each simulated month:
   - **Job loss:** income = protected_t + (1 − share) × earned_t + EI for the first `ei_months`, then nothing. With `return_to_work_month = k`, income goes back to normal from month k.
   - **Pay cut:** income = protected_t + (1 − cut) × earned_t.
   - **Money out:** out_t + bills_pct × bills_t + spending_increase.
4. Start balance = B − one-off costs. Balance_t = start + cumulative(income − money out).
5. **"Broke"** = the balance minus the typical dip goes below 0, so the in-month low point is below zero.
6. Report, by month:
   - p10/p50/p90 balance bands
   - the chance of surviving 6 and 12 months
   - the median month to zero, if more than half the paths get there
   - **expected overdraft (EE)** and the **95th-percentile overdraft (PFE)**: mean and 95th percentile of max(dip − balance, 0). That's the bank's view, like a credit-exposure profile.
7. **Seed with the account_id,** so the same customer and shock always give identical results.
8. Flag `insufficient_history` if there are under 18 months.

**Why this is defensible:** it uses the customer's own real months, not invented distributions. Its limit: it can't produce situations they've never lived through.

**Monte Carlo error:** with 2,000 paths, a probability near 50% has a standard error of about √(0.25/2000) ≈ 1.1 percentage points. More than precise enough.

**Spec:**
- `simulate(acct, d, sc, months=24, n_paths=2000, history=24, block=3, seed=None) -> dict` with keys `months, p10, p50, p90, start, dip, p_survive_6, p_survive_12, median_months_to_zero, n_paths, history_months, ee, pfe95, insufficient_history`
- Vectorised: build an index array of shape (n_paths, months) from the block starts. No Python loop over paths.

**Implementation notes:**
- RNG: `np.random.default_rng(acct)`.
- `starts = rng.integers(0, n − b + 1, size=(n_paths, ceil(months/b)))`.
- `idx = (starts[:,:,None] + arange(b)).reshape(n_paths, −1)[:, :months]`.
- If history < 3 months, use b = 1.

**Tests:** `test_simulation_reproducible_and_sane` (identical results twice, p10 ≤ p50 ≤ p90, P(12) ≤ P(6), and no shock is at least as safe as a job loss)

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M6. Implement simulate() as a vectorised block-bootstrap Monte
Carlo exactly per the spec (last 24 months, 3-month blocks, 2,000 paths, 24 months ahead, seeded with
account_id, shock applied per simulated month, broke = balance - dip < 0, bands, survival probabilities,
EE and PFE95 exposure, insufficient_history if < 18 months). It must run in well under a second.
Run `pytest -q -k simulation` and time one call.
```

## M7. Optimised cut schedule (linear programming)

**Goal:** turn the plan into an answer: "cut $190 a month and you stay out of overdraft all year." This is the strongest Impact feature, and it speaks to optimisation-minded judges.

**Formulation:**
```
inputs:  bal_t = the 10th-percentile (bad) or median (typical) simulated balance at month t, no changes
         dip   = the overdraft line (typical in-month dip)
         u_max = max_cut_share × (unlabelled outflows + loan payments)   (bills and insurance are never cut)
decision: u_t ≥ 0 = reduction in money out in month t
minimise   Σ u_t
subject to bal_t + Σ_{s≤t} u_s ≥ dip   for every month t = 1..T
           0 ≤ u_t ≤ u_max
```

**Algorithm:**
1. Compute `base_months` = how many months the balance stays above the line with no changes.
2. For T from 12 down to `base_months + 1`, solve the LP with SciPy `linprog(method="highs")`.
3. The first feasible T is the best achievable. Return its schedule.
4. If none is feasible, say honestly that cuts alone can't protect month `base_months + 1`, and that a bridge is needed: claim EI immediately, a loan deferral, or overdraft protection.

**Receding horizon:** re-solved each month with new data, this is a model-predictive-control style plan. Say this in Q&A; the demo solves once.

**Honest caveat:** the 10th-percentile balance is taken month by month, which is a conservative envelope rather than one real path. The upgrade would be optimising across all 2,000 scenarios at once.

**Verified behaviour** (roughly; exact cents depend on the Monte Carlo implementation):
- Account 20134, furnace twist, bad outcome: safe 6 months → **12 months** with cuts averaging about **$190/month**.
- Account 20111, rent +$600: 1 → 12 months with about $2,055/month.
- Under a job loss on capped EI, most accounts can't be protected in month 1 by cuts alone. The app must say so.

**Spec:** `optimize_cuts(acct, d, sc, horizon=12, max_cut_share=0.5, pessimistic=True, n_paths=2000) -> dict` with keys `base_months, protected_months, horizon, cuts, total, avg_monthly_cut, max_monthly_cut, path, protected_path, dip, outcome`

**Tests:** `test_optimiser_improves_or_explains` (protected ≥ base; cuts within bounds; the protected path stays above the line)

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M7. Implement optimize_cuts() as the linear program specified
(minimise total cuts subject to cumulative-cut constraints keeping the p10 or p50 simulated balance above
the dip line; bounds 0..u_max where u_max excludes bills and insurance; search the longest feasible
horizon from 12 down). Use scipy.optimize.linprog(method="highs") and a lower-triangular constraint
matrix. Return the documented dict. Run `pytest -q -k optimiser` and print results for account 20134
with Scenario(one_off_months_of_spending=1.0).
```

## M8. Plan generator

**Goal:** the challenge's part 3, built from the customer's own numbers.

**Goal plan:** milestones toward surviving 6 months of a job loss on capped EI.
1. `gap_on_ei = max(money_out − (protected + EI(earned)), 0)`
2. Milestone targets:
   - Starter: dip + 1 × gap_on_ei
   - Core: dip + 3 × gap_on_ei
   - Full: dip + 6 × gap_on_ei
3. `need = max(target − buffer, 0)`
4. Two saving speeds:
   - steady = 50% of the monthly surplus (money in − money out, if positive)
   - stretch = steady + 10% of unlabelled outflows
   - Months to each milestone = need ÷ speed
5. If the surplus is negative, show "close the monthly gap of $X first".

**Backup plan:** under the selected shock, compute the realistic runway after each action and rank them by months gained:
- Apply for EI in week one (if it's a job loss)
- Reduce unlabelled outflows 10%, 20%, or 50% (the "survival budget")
- Ask the lender for a payment deferral (if there are loan payments)
- Pause other transfers out
- Combined: a 20% reduction plus the deferral

**Spec:** `make_plan(acct, d, sc) -> dict`:
- `goal`: `have, monthly_gap_on_ei, monthly_surplus, steady_saving, stretch_saving, milestones[name, target, need, done, months_steady, months_stretch], benchmark_3mo_spending, deficit_to_close`
- `backup`: `base_runway, levers[action, how, monthly_saving, runway, gain]`
- also `profile`, `realistic`

**Tests:** `test_plan_shape`

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M8. Implement make_plan() with the milestone goal plan and the
backup levers exactly as specified, every number derived from realistic_profile() and realistic_runway().
Lever names must follow the wording rules in CLAUDE.md. Run `pytest -q -k plan` and print the plan for
account 20133 under a job loss with bills +15%.
```

## M9. Evidence engine

**Goal:** prove the findings, reproducibly. This is Data Use (25%), plus the "Why trust it" tab.

**`evidence.py` → `evidence.json` sections:**

1. **mislabel:** how many accounts have median money out above median money in (1,181, 26%); of those, the share with positive mean net flow (97.5%) and the share whose balance grew (90.4%).
2. **ei_cap:**
   - the share where 0.55 × I > $3,159 (57.2%)
   - their median runway, card vs capped (5.4 → 3.1)
   - surviving 6 months, card vs capped (44.5% → 16.3%; for all accounts 64.9% → 48.8%)
3. **out_of_time:** features from months ≤ 2024-12 for accounts with ≥ 12 months; outcome = any `days_below_zero` in 2025.
   - Answer key: EI-55% runway on pre-2025 data.
   - Realistic: the M3 definition on the last 12 pre-2025 months, falling back to all pre-2025 months if missing.
   - AUC 0.783 vs 0.841, with a bootstrap 95% CI on the difference (1,000 resamples of accounts, seed 0).
4. **trough:**
   - the three-year backtest table, with the risk-ratio CI
   - the 2025 head-to-head
   - the bootstrap CI for the trough AUC (0.809–0.911)
   - window sensitivity
   - the no-shock vs shock comparison
   - the 93172 example

**The no-shock vs shock point (it resolves a conflict between two analyses):** with no shock, almost every account shows "no shortfall", so no runway can rank anyone. The AUCs are 0.626 (median) and 0.541 (average) on 4,424 accounts with a full 2025. Under the EI shock they're 0.727 vs **0.777**.

5. **loans** (`loan_evidence(d)`): the crosstab, pre-loan overdrafts with Fisher's exact test, the 212 no-loan overdrawn, and the pre-loan signal block (AUC 0.775; 19.5% vs 3.2%).
6. **formula_holes** (`formula_holes(d)`):
   - EI forever: 39.3% → 21.8% last a year; 257 flips
   - pensioners: 740, owners 59+, pension 98%, formula runway 35.4
   - 57 minors
   - 64.3% of accounts are over 80% cash
   - bad months 1.96× the median
   - district unemployment correlation 0.98 (so it isn't used)
   - 76 stale accounts

**New tasks (not done yet; high value):**

A. **Benjamini–Hochberg correction** across every hypothesis in `findings_log.md` (about 9):
1. Compute a p-value per hypothesis. For AUC comparisons, a bootstrap p-value: the share of resamples where the difference is ≤ 0, times 2. For the risk ratio, a Fisher exact test.
2. Sort the p-values ascending.
3. Find the largest i with p_(i) ≤ (i/m)·q, with q = 0.10. Reject 1…i.
4. Use `statsmodels.stats.multitest.multipletests(p, method="fdr_bh")`.
5. The sentence to say: "We tested 9 ideas; the trough finding survives correction."

B. **Confounder check for the trough:**
1. Logistic regression of first overdraft in 2025 on `bottom_10_flag` + `log(avg_balance)` + `months_of_history` + district `unemployment_rate_2023`, using `statsmodels.Logit`.
2. Report the odds ratio for the flag, with a 95% CI. If it stays well above 1, the trough adds information beyond balance size and account age.
3. Report whatever it shows. Don't tune it until it looks good.

C. **Calibration:** for each year, the observed first-overdraft rate in each decile of the trough ratio. Show it as a small bar chart.

**Statistics used:**

| Statistic | Detail |
|---|---|
| ROC AUC | the chance that a random customer who did go overdrawn is ranked riskier than a random customer who didn't; 0.5 = coin flip |
| Bootstrap percentile CI | resample **accounts** with replacement 1,000 times, recompute, take the 2.5th and 97.5th percentiles |
| Risk-ratio CI | log(RR) ± 1.96·√(1/a − 1/n₁ + 1/c − 1/n₀), then exponentiate |
| Benjamini–Hochberg | controls the expected share of false discoveries among the findings we call real |

**Tests:** `test_evidence_out_of_time`, `test_evidence_loans_and_holes` (both slow)

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M9. Implement evidence.py with main(n_boot=1000, seed=0) writing
evidence.json with the sections mislabel, ei_cap, out_of_time and trough exactly as specified (populations,
time cutoffs, outcomes, bootstrap over accounts). Then add two new sections: "multiple_testing" (BH at
q=0.10 over the hypotheses listed in findings_log.md, using bootstrap p-values for AUC differences and
Fisher exact for the risk ratio) and "confounders" (statsmodels Logit of first overdraft in 2025 on the
bottom-10% trough flag, log average balance, months of history and district unemployment 2023; report
the flag's odds ratio and 95% CI). Report results honestly. Run `pytest -q -m slow`.
```

## M10. AI layer

**Goal:** a useful AI feature that can't break the demo or invent numbers.

**What AI does:**
1. **Twist-card reader:** a judge's sentence becomes structured shock settings. They're shown as chips for confirmation before anything runs.
2. **Plan writer:** a warm 4–6 sentence plan using only the numbers the engine produced.

**What AI never does:** calculate.

**Settings schema** (the AI must return exactly these keys):
```json
{"job_loss": false, "ei_rate": 0.55, "ei_months": 6, "income_cut": 0.0,
 "bills_increase_pct": 0.0, "spending_increase": 0.0, "one_off_cost": 0.0,
 "one_off_months_of_spending": 0.0, "return_to_work_month": null}
```

**Backends, in order:**
1. **Gemini on Vertex AI:**
   - `genai.Client(vertexai=True, project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION or "us-central1")`
   - Setup: enable the Vertex AI API, run `gcloud auth application-default login`, set `GOOGLE_CLOUD_PROJECT`.
2. **Gemini API key:** `genai.Client(api_key=GEMINI_API_KEY)`.
3. **Offline rules:** a regex parser that always works.

The model name comes from `GEMINI_MODEL`, default `gemini-2.5-flash`; change it if a newer one is available. Call `client.models.generate_content(model, contents, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))`.

**Sanitise everything the AI returns:** clamp rates between 0 and 5, EI months between 0 and 12 (EI lasts at most 45 weeks), and coerce types. On any exception, fall back to the offline parser.

**Offline parser rules:**

| Card says | Setting |
|---|---|
| laid off / lose job / job loss / unemployed / fired | `job_loss = True` |
| "EI … N%" | `ei_rate` |
| "for N months" | `ei_months` |
| "new job … month N" | `return_to_work_month` |
| pay / hours cut N% (not a job loss) | `income_cut` |
| bills / rent / utilities … up N% | `bills_increase_pct` |
| "$X a month" / "per month" / "monthly" | added to `spending_increase` |
| any other "$X" with a repair-type word | `one_off_cost` |
| "a full / half a / N month(s) of … spending" | `one_off_months_of_spending` |

**Number verifier:**
1. Extract every number from the AI text.
2. Each must appear in the facts, as given or rounded (to an integer, 1 decimal, or ×100 for percentages), or be a small counting word (1, 2, 3, 6, 12).
3. If any number fails, use the template text instead.

**Spec (`ai.py`):** `init() -> backend name`, `backend()`, `parse_twist(text) -> (settings, "AI" | "rules")`, `parse_twist_offline(text)`, `write_plan(facts) -> (text, "AI (numbers verified)" | "template")`, `verify_numbers(text, facts) -> bool`, `template_plan(facts) -> str`

**Tests:** `test_twist_reader_offline` (5 cards, including rent plus repair and a pay cut), `test_number_verifier`

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M10. Implement ai.py: init() choosing Vertex AI, API key or offline;
parse_twist() using Gemini JSON output with temperature 0, sanitised and falling back to
parse_twist_offline() on any error; the offline regex parser covering every rule in the table (monthly vs
one-off dollar amounts!); write_plan() that only uses provided facts and passes verify_numbers(), else
template_plan(). Never let AI compute a number. Run `pytest -q -k "twist_reader or verifier"`, then write
10 extra unusual twist cards and show what the offline parser returns for each.
```

## M11. Streamlit app

**Goal:** the experience judges touch. Clear, fast, and impossible to break live.

**Layout:**

*Sidebar:*
- the title
- "Random customer" button
- `account_id` number input
- **Time Machine** selector: Today / Dec 2024 / Dec 2023
- AI backend status
- one line: "All numbers come from the engine; AI only reads cards and writes plans."

*Header:* customer ID, owner age (from `clients.csv` via `dispositions.csv`), and flag chips:
- loan granted while already overdrawn
- has been overdrawn before
- pension over 50% of money in ("a layoff doesn't apply")
- owner under 18
- trough in the riskiest 10%
- no labelled bills
- savings ≤ 0, or under one month of spending saved
- no activity after a date
- medians and averages disagree
- joint account

*Tabs:*

| Tab | Contents |
|---|---|
| **Watchlist** | Below the table, the **Bank view**: `portfolio_curve` under the Shock tab's current scenario (cached per scenario), standard vs realistic, with a one-line caption at month 6. Above it: top 50 by trough ratio, with the early-warning toggle and the scorable filter. Columns: trough %, lowest and average balance, both EI runways, reasons, and (in Time Machine) "overdraft next 12 months". Clicking a row opens that account. The reveal sentence goes on top. |
| **1 · Know** | A **credit view** (four metrics: loan, payment with its share of money in, trough before the loan, status today, plus a warning if overdrawn before the loan) when `loan_risk` isn't None. Three cards: standard runway (no shock), realistic runway (no shock), trough ratio (or "too new"). Two tables: the judges' numbers and our numbers. In Time Machine, a "what happened next" chart. Then a balance chart (average vs lowest), the Kalman chart (bars = monthly net, line = level, band = ±2 sd), and a money-in sources stacked bar. |
| **2 · Shock** | Left: twist-card text box, "Read card", "Reset", three preset buttons, chips showing what was understood, and an expander of controls (job loss toggle, EI %, EI months, cap toggle, new job month, pay share, pay cut %, bills %, extra monthly $, one-off $, one-off months). Right: two big runway cards, "why the two numbers differ" bullets, the chance of making 6 and 12 months, a fan chart (p10–p90 band, p50 line, dip line, "EI ends" marker), and the exposure caption. |
| **3 · Plan** | Milestones table with progress bars, a deficit note, backup levers bar chart, the optimiser (bad/typical toggle, max-cut slider, success or warning message, chart of both paths plus cut bars, method caption), and a "Write the plan" button showing the verified text and its source. |
| **Why trust it** | Everything from `evidence.json`: the trough headline and three-year table, the loan finding with its caveat, the formula's blind spots, the head-to-head, no-shock vs shock, the EI cap, the mislabel, the 93172 story, and the limits. |

**Streamlit pitfalls (tell Claude Code):**
- **Changing a widget's value from code:** do it only in an `on_click` / `on_select` callback. Callbacks run before widgets are drawn; setting `st.session_state[key]` after the widget exists throws an error. This matters for "Read card", the presets, "Reset" and watchlist row clicks.
- **Caching:** `@st.cache_resource` for the data dict and the watchlist (one per as-of date). The data dict isn't hashable for `cache_data`.
- **Watchlist row click:** `st.dataframe(..., on_select=callback, selection_mode="single-row", key="wl_table")`. In the callback, read `st.session_state.wl_table.selection.rows` and set `st.session_state.acct`.
- **Width:** use `width="stretch"` (newer Streamlit deprecates `use_container_width`).
- **Speed:** one account renders in about a second. Never loop over all accounts on a click.

**Design:**
- Orange (#e86f00) = ours; slate grey = the standard runway. One accent colour.
- Big serif numerals for the two runways (the only "big number" moment).
- Sentence case. No all-caps labels.
- Every chart title states the takeaway.

**Smoke test** (headless, with `streamlit.testing.v1.AppTest`):
1. Load the app.
2. Click every preset, "Write the plan" and "Reset".
3. Switch the Time Machine to Dec 2024 and Dec 2023.
4. Open 93172 and an account that's too new as of Dec 2024 (e.g. 20134).
5. Move the optimiser controls and the pay-share slider.
6. Open 25 random accounts under the job-loss + bills twist.
7. Expect zero exceptions.

**Claude Code prompt:**
```
Read CLAUDE.md and BUILD_GUIDE.md section M11. Build app.py in Streamlit exactly per the layout: sidebar
(random customer, account_id, Time Machine selector, AI status), flag chips, and five tabs (Watchlist,
Know, Shock, Plan, Why trust it). The app must not compute any money: call engine.py and ai.py only.
Follow the pitfalls list (callbacks for programmatic widget changes, cache_resource, dataframe on_select
for the watchlist, width="stretch"). Then write tests/test_app_smoke.py using streamlit.testing.v1.AppTest
covering the smoke-test list, and run it until there are zero exceptions.
```

## M12. Differentiators if you're ahead

In order of value per hour:

1. **Demo mode button (30 min):** one click sets the Time Machine to Dec 2024, opens 93172, and scrolls to the reveal. It makes the pitch flawless.
2. **Scenario comparison (1 h):** columns A (no action), B (optimised cuts) and C (loan deferral, or cuts plus EI on day one), each with realistic runway, chance of making 6 months, and lowest projected balance. All from engine functions.
3. **BH + confounder results in "Why trust it" (from M9):** one sentence each.
4. **Printable plan (30 min):** `st.download_button` with the customer's plan as a Markdown or text file. Something an advisor could actually send.
5. **French plan (20 min):** Canada is bilingual. AI translates the verified English plan, numbers unchanged (re-run `verify_numbers`).
6. **Calibration chart (30 min):** the observed first-overdraft rate by trough decile.

Don't start anything new after the 2 AM feature freeze.

---

# Part C. Reference

## C1. Stats and algorithms cheat sheet

| Method | What it does | Where we use it | Pitfall we avoided |
|---|---|---|---|
| Median vs mean | Typical month vs total ÷ months | Answer key vs realistic | Medians mislabel lumpy inflows; with no shock neither ranks anyone |
| Liquidity Trough Ratio | Low point relative to normal balance | Early warning, watchlist | Opening-month artefact: require 12 months |
| Out-of-time test | Fit on past, check on the future | All findings | Using future data in features (leakage) |
| ROC AUC | Ranking quality, 0.5–1.0 | All comparisons | Comparing AUCs on different populations |
| Bootstrap CI | Uncertainty by resampling accounts | AUC, AUC differences | Resampling rows instead of accounts makes intervals falsely narrow |
| Risk ratio + CI | How many times more likely | Trough bottom 10% | Tiny event counts; we show n |
| Benjamini–Hochberg | Controls false discoveries | All hypotheses | Testing many ideas and reporting the best |
| Logistic regression | Effect after controlling for other factors | Trough confounder check | Calling it causal |
| Kalman filter | Signal vs noise with uncertainty | Net-flow chart | Over-smoothing: q chosen by maximum likelihood |
| Block bootstrap Monte Carlo | Possible futures from real history | Shock tab | Invented distributions; unseeded randomness |
| Exposure (EE / PFE) | Expected and tail overdraft | Bank's view | Calling it expected loss (no PD or LGD here) |
| Linear programming | Cheapest plan meeting the constraints | Optimiser | Cutting bills; pretending a pointwise p10 is one path |

## C2. Integration contract

Function names below are fixed. The app, the tests and the evidence script depend on them.

| Function | Returns | Used by |
|---|---|---|
| `load()` | dict of DataFrames | everything |
| `profile`, `runway`, `all_profiles`, `runway_vec`, `TWISTS` | answer key | Know, Shock, watchlist, evidence |
| `realistic_profile`, `realistic_runway`, `Scenario`, `ei_benefit`, `explain_difference` | realistic engine | Know, Shock, Plan |
| `ltr_table`, `liquidity_trough`, `watchlist`, `realistic_vec`, `what_happened_next` | trough + Time Machine | Watchlist, Know |
| `loan_risk`, `realistic_runway_vec`, `portfolio_curve` | credit view, bank view | Know, Watchlist |
| `kalman_level`, `net_flow_filter` | signal vs noise | Know |
| `simulate` | Monte Carlo + exposure | Shock, optimiser |
| `optimize_cuts` | LP schedule | Plan |
| `make_plan` | goal + backup | Plan |
| `ai.init`, `parse_twist`, `write_plan`, `verify_numbers` | AI layer | Shock, Plan |
| `evidence.main` → `evidence.json` | findings | Why trust it |

**Definition of done for the whole project:** `pytest -q` and `pytest -q -m slow` pass, the app smoke test has zero exceptions, and `python evidence.py` regenerates `evidence.json`.

## C3. Submission checklist

- [ ] **Sat 8 PM:** Devpost draft, **Tangerine track selected**, all members added (max 4)
- [ ] Public GitHub repo: code, README, `CLAUDE.md`, `BUILD_GUIDE.md`, tests. No `data/`, no keys.
- [ ] README: how to run, the logic, findings, limits, and sources (PKDD'99 link, Canada EI page, list of libraries and Gemini)
- [ ] Write-up: the question ("Who is closer to running out than they look, and what should they do?"), what we did, what we found (trough 14.6×, EI cap, median mislabel), limits
- [ ] **Video, 2:00–2:10:**
  - 0:00 the 93172 Time Machine story
  - 0:30 the evidence
  - 1:00 a live twist on a random account
  - 1:40 the plan and optimiser
  - 1:55 one line on limits

  Public YouTube or Drive link, tested in a private browser window.
- [ ] **Submit by 11 AM Sunday** (Devpost closes at 12)
- [ ] Demo laptop charged, app running locally, fallback screenshots, phone hotspot
- [ ] **Sun 1:00–2:30 PM:** someone at the table the whole time

## C4. Demo script, live-twist runbook, Q&A

**1-minute pitch:**
> "The bank already had a warning sign. It just wasn't looking at it. [Time Machine → Dec 2024 → 93172]
> In September this customer's balance dipped to $238 while the average looked like $18,500. The standard runway said fine. In December the bank lent them $167,000, a payment one and a half times their monthly money in. In January they were overdrawn; the loan is now in debt.
> It's not one story: every borrower here who went below zero defaulted, 76 of 76, and 27 loans went to people already overdrawn. All 27 went bad.
> Our trough indicator catches the dip first: the 10% we flag are 14 times more likely to have a first overdraft, in three separate years, and measured before a loan it finds borrowers who default 6 times as often.
> Runway shows your exact numbers, our realistic numbers, and a plan. Pick any account and any twist."

**Live twist (3 minutes):**
1. Time Machine → **Today**. Type the `account_id`.
2. Paste the card → **Read card** → read the chips aloud.
3. Say the **standard runway first** (it matches their answer key), then ours, then one "why they differ" line.
4. Give the chance they make 6 months.
5. Plan tab: the next milestone, then the optimiser result ("cut $X a month, safe for Y months", or "cuts alone can't cover month 1; here's the bridge").
6. If AI fails, the rules parser still works. If that fails, use the sliders.

**Q&A:**

- **"Why do your numbers differ?"** Yours uses medians and a flat 55%. Ours uses recent averages, the real $729/week cap, keeps pensions, and counts the monthly dip. We show both.
- **"Isn't a low trough obviously risky?"** That's why we tested only customers who had never been overdrawn. It beats the raw lowest balance (0.860 vs 0.840), and it catches customers the runway calls healthy.
- **"Luck?"** Three separate years, 95% intervals, and window sensitivity. Plus Benjamini–Hochberg across everything we tested, and a confounder check, if done.
- **"Isn't 100% default definitional?"** Partly for status D ("in debt"). It holds for every B loan, for the 27 overdrafts before the loan existed, and for the trough measured before the loan (19.5% vs 3.2%). 76 cases means "every case here", not a law.
- **"Your number differs for a pensioner?"** A layoff doesn't stop a pension; the formula cuts it to 55%. We flag it.
- **"Couldn't a simple rule catch 93172?"** By November, yes. The standard runway still said fine, and the bank lent in December.
- **"Causal?"** No. It's an early-warning signal. The next step is a pilot: contact flagged customers and compare overdraft rates.
- **"Monte Carlo assumptions?"** It replays 3-month blocks of the customer's own last 24 months, seeded and reproducible. It can't invent situations they've never had.
- **"Why linear programming?"** It finds the cheapest monthly cuts that meet "never below the overdraft line". Re-solved monthly, it's a receding-horizon plan.
- **"What does the AI do?"** It reads the card and writes the plan. It never calculates, and every number it writes is checked.
- **"Is this Tangerine data?"** No. It's the public PKDD'99 Czech bank dataset, re-dated and converted to CAD by the organisers.
- **"Scale?"** Everything is a per-customer monthly update: a nightly batch or a stream keyed by customer. At bank volume, sketches like HyperLogLog and Bloom filters would handle features like payee novelty.

## C5. What can go wrong, and the fallback

| Risk | Fallback |
|---|---|
| Wi-Fi dies | The app runs locally; the offline twist parser; hotspot |
| Gemini fails live | The rules parser takes over automatically; sliders as a last resort |
| A judge picks a weird account | Flags explain it (pensioner, owner under 18, no bills, savings ≤ 0, too new to score, overdrawn before the loan). The engine never crashes; every account is tested. Rehearse 20176 (pensioner) and 56072 (16-year-old owner). |
| Laptop dies | A second laptop with the repo pulled and data copied; screenshots |
| Our number differs from theirs | The standard card shows their exact number; explain ours as a second opinion |
| A judge challenges the finding | Open "Why trust it": three years, intervals, the confounder check, the limits |
| Running out of time | Cut from M12 up. M1–M8 plus a simple app already wins on substance. |
