# Runway: product and engineering spec (single source of truth)

Read this first. It says what Runway is, how every number is defined, what has been proven, what is on screen,
and where the work stands. Numbers come from `evidence.json` (rebuild: `python evidence.py`); definitions from
`engine.py`. If this file and the code disagree, the code wins: fix this file.
Last full check: Nov 8, branch `p1/judge-ready` (114 fast, 6 UI, 12 slow tests passing; 0 WCAG A/AA violations).

---

## 1. Problem, users, use case

**Problem.** Banks judge resilience by averages (average balance, months of runway). Overdrafts happen at the
**low point** of the month. Customers who look fine on average dip close to $0 every month, and nobody sees it
until they go negative. In this data every borrower who was ever overdrawn defaulted (76 of 76).

**Users.** A bank's customer-care advisors and risk teams (and, through them, the customer).

**Use case, end to end.**
1. **Every month, tier the whole book** (`engine.book_tiers`): every customer gets one tier and one kind of action.
2. **Advisors work the call list**: the riskiest customers, each with their own cause and next step.
3. **Know the customer**: why they are at risk, the realistic runway, the calibrated chance of a first overdraft.
4. **Take a shock** (the judges' live twist): a plain verdict, the biggest reason, simulated futures.
5. **Act, safest first**: alert and call (no credit risk) → auto-transfer from own savings → a small priced limit
   only after a call. AI drafts the brief and the customer message (EN/FR); it never calculates.
6. **Lending**: a review rule at loan approval uses the same signal.

**The whole book (Dec 2024 cohort, outcome 2025)**: already overdrawn + riskiest 10% + new-and-swinging = **10%** of
customers, **68%** of next year's overdrafts. The **stable** tier overdrew **0.4%**, the same in every year tested.

| Tier (`BOOK_TIERS`) | Rule (data up to the as-of month) | Action | Overdrew next year (Dec 2024 → 2025) |
|---|---|---|---|
| overdrawn | any day below $0 in the last 12 months | recovery plan + personal alert | 60% |
| act | trough percentile ≤ 10% | advisor contact matched to the cause | 12.7% |
| watch | 10–30% | automatic personal alert, no call | 2.7% |
| stable | rest | nothing | 0.4% |
| new_hot | 3–11 months and top 10% of new accounts by swings in money in (`new_account_swing`) | welcome check-in call + personal alert | 18.6% |
| new | under 3 months, or new but not swinging | standard alerts | 2.8% (13% of overdrafts) |

---

## 2. Data

Tangerine/PKDD'99 Czech bank data, re-dated 2020–2025, money in CAD. 4,500 accounts, 185,326 account-months,
1,056,320 transactions, 682 loans. `data/` is never committed. All 9 files are used:

| File | Used for |
|---|---|
| monthly_summary | everything (judges' formula, trough, runways, simulation, diagnoses, tiers) |
| transactions | day of month each customer's balance bottoms out (`load_dip_days`); bill-timing test (rejected) |
| loans | loan payment P, forward loan payments, credit view, loan-approval rule, 76/76 |
| clients, dispositions | owner age, joint accounts, fairness check (gender, age are never model inputs) |
| accounts, districts, cards | confounder check, risk profile (district makes no difference) |
| standing_orders | today's view only (undated end-of-2025 snapshot: never used in backtests) |

Outside data (allowed by Tangerine): EI 2026 maximum $729/week (canada.ca); Tangerine overdraft protection
$5 per use + 19%/yr; federal NSF fee cap $10 (since Mar 12, 2026); OSFI Guideline E-23 for model governance.

**No-lookahead rules (each has a test):** Time Machine cuts all data at the as-of month; loans count from the month
granted and their outcome is hidden in Time Machine mode; standing orders are excluded from backtests; per-tier and
repeat-overdraft rates shown at an as-of date come from a year already over.

---

## 3. Definitions (engine.py)

| Name | Definition |
|---|---|
| Judges' profile (`profile`, `runway`) | I = median money in, S = median money out, B = mean avg daily balance over last 6 rows, H = median household bills, F = median bills+insurance+loans, P = loan payment if running at end-2025. Runway = (B − one-off) ÷ (spending after shock − income after shock), 0 if buffer ≤ 0, "no shortfall (120+)" if gap ≤ 0, cap 120, 1 decimal. **Never change** (answer key: 20111 → 3.4 / 4.0 / 3.4). |
| Realistic profile (`realistic_profile`) | last 12 months (`WINDOW`) means; pension + interest protected in a job loss; EI 55% capped at $729/week (`EI_MONTHLY_MAX` ≈ $3,159) and **stopping after `ei_months`**; usable buffer = B − typical in-month dip; **forward loan payments** (`loan_payment_due`, `loan_adjust`): a loan granted in the window counts at its full payment. |
| Liquidity trough (`ltr_table`) | lowest balance ÷ average balance over the last 6 months (`LTR_WINDOW`); scored only with ≥ 12 months (`LTR_MIN_HISTORY`); percentile rank 0 = most fragile; flag = riskiest 10%. |
| Monte Carlo (`simulate`, `_sim_paths`) | 2,000 futures from 3-month blocks of the customer's own last 24 months, shock applied, starting at today's balance, seeded by account. Under a shock, outputs are **shares of futures**, never "chance". Also exposure profile (`ee`, `pfe95`). |
| Calibrated risk (`overdraft_risk`, `calibrate_break`) | Platt map of the raw no-shock 12-month break probability: `SIM_CAL_A, SIM_CAL_B = -3.3602, 0.4574` (fit 2023→2024). Valid only for customers with 12+ months and never overdrawn. |
| Verdict (`verdict`) | Yes / No / Only on paper / Fragile for a 6-month horizon (`MAKE_IT_MONTHS`), the biggest reason in months (each adjustment switched back to the standard assumption), simulated range. |
| Cushion (`cushion`) | buffer = alert level = typical in-month dip; top-up now; usual dip day if reliable (`DIP_DAY_RELIABLE` 70% of months within ±5 days). |
| Diagnosis (`diagnose`) | most urgent first: repeat (overdrawn this year) → income_drop (money in last 3 ÷ prior 9 ≤ `INCOME_DROP` 0.75) → new_loan (new loan payment ≥ `NEW_LOAN_BURDEN` 30% of money in) → swing (sd of net flow ÷ balance ≥ `SWING_THRESHOLD` 0.47) → dip. Each with an action sized from own numbers. |
| Overdraft cost (`overdraft_cost`) | Tangerine terms: $5 per month used + 19%/yr (`TANGERINE_OD_FEE`, `TANGERINE_OD_RATE`). |
| Loan-approval rule (`loan_check`) | hold for review if, on data before the loan month, the applicant was ever overdrawn or is in the riskiest 10% by trough (`LOAN_REVIEW_TROUGH`). |
| Optimiser (`optimize_cuts`) | one linear program (HiGHS) over 12 months, solved once: smallest cuts keeping the 10th-percentile path above the dip; bills/insurance never cut; reports `share_of_futures_protected`. **Not** MPC/receding-horizon. |
| Book tiers (`book_tiers`) | see §1 (`WATCH_SHARE` 0.30). New accounts: `new_account_swing` = sd of monthly money in (opening month dropped), top 10% (`NEW_SWING_SHARE`) of accounts with 3–11 months (`NEW_MIN_MONTHS`). |
| Survival (`survival_cohort`, `survival_curves`, `when_overdraft`) | time to first overdraft for never-overdrawn customers, 24 months, groups riskiest 10% / next 20% / rest; per-customer "When?" uses the cohort scored 2 years before the as-of month (`survival_score_month`: no lookahead). |
| SQL (`sql/trough.sql`) | the trough as one window query; a test checks identical values and flags to the Python on all accounts. |

---

## 4. What is proven (evidence.json)

| Finding | Result | Method |
|---|---|---|
| Low point predicts first overdrafts | riskiest 10% catch **34 of 55 (62%)** in 2025; risk ratio 17.9× / 12.8× / 14.6× and AUC 0.841 / 0.844 / 0.860 for 2023 / 2024 / 2025 | out of time: features to Dec, outcome next year, never-overdrawn population |
| Not just balance size | odds ratio **16.8 (95% CI 9.5–29.7)** after balance, account age, district unemployment | logistic regression |
| Survives multiple testing | **48 of 57** tests (base family 28 of 29) | Benjamini–Hochberg q = 0.10 |
| Probabilities are real | raw simulation 8× too pessimistic; calibrated: **1.61% vs 1.61%**, AUC 0.882, Brier 0.0142 vs base 0.0158 | Platt, fit 2023→24, judged 2025 |
| Customers steer back | after a low month money in beats money out +36–37 pts vs +18–19 shuffled; 87–91% of customers | permutation vs shuffled months, 2 years |
| Cushion works as a limit | dip-sized buffer fully covers **27 of 34** caught overdrafts; **$78K drawn of $2.9M** | 2025 backtest |
| Personal alert | warns **23 of 34** a median **3 months** early (a $100 alert: 1); pings 22% of quiet flagged customers; precision 25% vs 1.6% base | 2025 backtest |
| Overdrafts and credit | **76 of 76** ever-overdrawn borrowers defaulted; 27 loans to already-overdrawn customers, all defaulted (Fisher p = 1.6e-28) | crosstab |
| Loan-approval rule | holds **118 (17%)**; catches **41 of 76** defaults; **34.7% vs 6.2%** default rate (clean outcome 10.2% vs 3.4%, p = 0.003); holds 77 good loans | before-loan data only |
| Hidden new loans | 186 customers at Dec 2024 had a loan not yet in their spending history; 93172: realistic runway 26.7 → **2.4 months** | forward loan payments |
| Causes pick the action | inside the flagged 10%: money in fell → 20% vs 8% overdrew (2025, survives BH), swings → 14% vs 6% (2025); 2024 not significant | Fisher, both years |
| New accounts can be scored | the trough fails on new accounts (AUC 0.55–0.71); swings in money in, chosen on 2023 + 2024 (most caught at a 10% flag both years: 5/15, 13/28), confirmed on 2025: catches **13 of 32**, **18.6% vs 3.0%**, AUC 0.80, p < 0.001 | 4 candidates, all 12 tests in the BH family |
| Repeat overdrafts | overdrawn one year → again 47% (2024), 60% (2025) vs 1.6–1.8% | out of time |
| Who the riskiest are | money in $16,809 vs $7,322, loan 37% vs 13%, pensioners 0.3% vs 20%; district, joint account: no difference | tested, effect-size labelled |
| Fairness | flag rate ratio women/men 1.12 (2024), 0.86 (2025): within four-fifths; catch-rate gap flips direction, p = 0.30, 0.10 | by gender and age |
| When first overdrafts come | never-overdrawn customers scored Dec 2022 / Dec 2023, followed 24 months: riskiest 10% reach 6.3% by month 6, 12.7% by 24 (2023 cohort); hazard ratio for the flag **11.2 (5.2–23.9)** / **12.4 (7.2–21.2)**, 2–4× higher in the first 6 months; log-rank p < 1e-9 | Kaplan–Meier, discrete-time hazard logit (Cox failed on monthly ties) |
| Champion vs challenger | gradient boosting on 12 features: **39 vs 34 of 55** caught, AUC 0.865 vs 0.860; not significant (McNemar p = 0.18, bootstrap p = 0.84); its top feature is the trough → trough kept | fit 2023→2024, judged 2024→2025 |
| Model health | 0 breaches on 10 monitors (PSI drift, AUC floor, calibration band, data quality) | OSFI E-23 style |

**Rejected, shown on screen:** trough beats plain lowest balance (tied); bills-before-deposit timing (protective, not
risky); a combined score (33 vs 34 of 55); weak steering as a predictor (2025 only); new-loan burden inside the
flagged 10% (too few customers).

---

## 5. Product: screens and API

React dashboard (`web/`, served by FastAPI `api.py`); Streamlit (`app.py`) is the backup. React never calculates
money; `api.py` calls `ui/context.build_context`, the same function Streamlit uses.

| Screen | Shows |
|---|---|
| 01 Who's at risk | headline results; **the whole book** (tiers, actions, tested rates); advisor call list (cause → next step, Time Machine reveal); bank-wide job-loss curve; loan-approval rule; who the riskiest are |
| 02 Know the customer | 4-step story strip; calibrated risk; trough; both runways; "why they're at risk, and what to do"; advisor assistant (brief, EN/FR message); balance chart; what happened next; loan card (would it have been held) |
| 03 Stress test | twist card → chips (+ AI/rules disagreement flags) → verdict + drivers → runways → simulated futures → fan chart → exposure profile (risk teams) → judge check |
| 04 Make a plan | first action; no-risk steps first with real costs; cushion backtest; cuts; backup levers; milestones; AI plan |
| 05 Why trust it | headline proof; model health; backtests; calibration; steering; loan rule; fairness; who the riskiest are; reasons; what didn't hold up; limits with responses |

**Pitch mode** (top bar): five guided steps; Demo account 93172 at Dec 2024.

API: `GET /api/health, /api/accounts, /api/customer/{acct}?asof, /api/watchlist?asof, /api/book?asof, /api/evidence`;
`POST /api/shock/{acct}, /api/plan/{acct}, /api/write-plan, /api/ai/brief/{acct}, /api/ai/message/{acct}?lang, /api/twist, /api/portfolio`.
`asof` must match `202[0-5]-MM`.

---

## 6. AI (ai.py)

Gemini (`gemini-3.5-flash`) on **Vertex AI** when `GOOGLE_CLOUD_PROJECT` is set (datathon credits project
`runway-datathon-11072341`), else API key, else offline rules/templates. Hard 6-second limit, minimal thinking.
- **Reads twist cards** into a typed schema (`_TWIST_SCHEMA`), values clamped (`_sanitize`), and the offline rules
  cross-check: disagreeing fields are flagged before anything runs (`parse_twist_checked`, chips).
- **Writes** the advisor brief, the customer message (EN/FR, no risk numbers, no credit offer) and the plan.
  Every number must appear in the engine's facts (`verify_numbers`), simulation counts can't be called a "chance"
  (`verify_wording`); otherwise a template is used. Facts lead with the engine's first action.
- **Measured** (`scripts/eval_ai.py` → `docs/AI_EVAL.md`): offline rules 22/22 on the cards they were tuned on,
  8/16 on the first held-out set (overfit). Generalised using that set (now the dev set), then scored **once** on a
  fresh held-out set frozen beforehand: **15/16 (94%)**. Gemini (Nov 8, Vertex): 22/22 tuned, 15/16 dev,
  **14/16 (88%) held-out v2**, median 1.3 s; its misses: "a third" read as 0.33, and "4 months, then back to work" read
  as returning in month 5. Neither reader is perfect alone, which is why chips + the disagreement flag come first.
  Never tune the rules to `HELD_OUT_V2`.

---

## 7. Governance and engineering

- **Model card** in OSFI E-23 inventory format: `docs/MODEL_CARD.md`. **Monitoring** thresholds are stated choices.
- **CI** (`.github/workflows/ci.yml`): compile check, data-free tests (data tests skip with a reason), dashboard build.
- **Tests**: `pytest -q` (fast), `-m ui` (Streamlit click-through), `-m slow` (evidence). Slow tests never write
  `evidence.json`; only `python evidence.py` does.
- **Accessibility**: axe-core WCAG 2 A/AA, 0 violations; tangerine `--ours-fill` #c94a0c behind white text.
- **Two sessions**: lanes in `CLAUDE.md`; log every change in `docs/HANDOFF.md`; `graphify update .` after code changes.
- **Pinned test values** changed only when the model changed on purpose, each logged old → new in HANDOFF.

---

## 8. Status (Nov 8)

| Where | What |
|---|---|
| `main` (`ba3756f`) | PRs #1–#14 merged |
| **missing from main** | `1a52f5e` Pitch mode, `a0da90b` fairness/SQL/Q&A (pushed after #14 merged) → included in `p1/judge-ready` |
| `p1/judge-ready` (bundle `judge-ready.bundle`) | the two lost commits + whole book, AI eval, exposure profile, MPC wording fix, one-population fix, this spec. **Needs pushing from the laptop + PR** |
| Survival + challenger | cherry-picked on top of `p1/judge-ready`, evidence rebuilt, tests green |

**Known gaps (say them first):** 1990s Czech data, not Tangerine customers; money in is mostly cash, so a job loss
assumes all non-pension money in stops (slider); accounts under 3 months can't be scored; diagnoses hold in
2025 only; exposure profile is uncalibrated; no causal evidence for actions (the pilot's controlled test is how).

**Next steps, in order:** merge `p1/judge-ready` → check `main` runs → Devpost + video → rehearse Pitch mode and the live twist on
93172, 20111, 20176 with `docs/JUDGE_QA.md`.

**Superseded docs:** `FRONTEND.md` and `REACT_PLAN.md` describe the plan before the React app existed; this spec and
the code are current.
