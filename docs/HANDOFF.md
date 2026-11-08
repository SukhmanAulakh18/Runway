# Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)

Read this before starting any task. It records what a full review of the repo found, what the team decided, and what's left. Every number below was re-run on the real data.

## Verified (don't re-check)
- `pytest -q`: 57 passed. `pytest -q -m ui`: 6 passed.
- Answer key matches the README: account 20111 → **3.4** (job loss EI 55%), **4.0** (furnace), **3.4** (job loss + bills 15%).
- Trough finding: 14.6× risk (2025), AUC 0.841 / 0.844 / 0.860 over three years.
- Confounder check (E4): adjusted odds ratio **16.8** (95% CI 9.5–29.7) after balance size, account age, district unemployment.
- BH correction (E3): **28 of 29** tests survive at q = 0.10.
- Overdraft → default: 76 of 76; 27 loans granted while already overdrawn, all defaulted (Fisher p = 1.6e-28).
- EI 2026: 55% up to **$729/week** (max insurable earnings $68,900), up to 45 weeks. Source: canada.ca.
- Speed: simulate ~10 ms, optimize_cuts ~0.3 s. No need for C++.

## Decisions
1. **React frontend is approved, Streamlit stays as the backup.** Plan: `docs/REACT_PLAN.md`. React talks to `api.py` (FastAPI). Neither React nor `api.py` computes money.
2. **Midnight go/no-go:** React must run the full live twist on 5 accounts with zero errors, or we demo Streamlit.
3. **No C++, no new AI backends** (no IBM, Lovable, Backboard). Gemini via Vertex AI only (Google Cloud credits claimed). ElevenLabs only for the video voiceover.
4. **Deploy:** Cloud Run, one container (FastAPI also serves the built React files), Sunday morning.

## Must fix (judges will see these)
| # | Bug | Owner | Fix |
|---|---|---|---|
| 1 | **Time Machine lookahead.** In Dec 2024 mode only the trough rewinds; runway cards, simulation and plan use data through Dec 2025. 93172 shows 6.6 months instead of "no shortfall" (the pitch line). | P1 | Streamlit: in `ui/context.py`, when `asof` is set, pass `{"monthly": d["monthly"][month <= asof], "loans": d["loans"]}` to profile / realistic_profile / simulate / make_plan / optimize_cuts / loan_risk. `api.py` already does this. |
| 2 | **Kalman chart band is ±$67M in month 1** (diffuse start), which squashes the chart. q also hits the grid floor (1e-5) for most accounts, which means "no trend". | P2 (`know.py`) | Skip the first 2 months when drawing the band. If `q <= 1e-5`, caption "No trend: month-to-month swings are noise around ~$X a month" instead of calling it a signal. Or drop the chart from the demo. |
| 3 | **Pitch claim that didn't survive our own BH test:** "trough beats raw lowest balance (0.860 vs 0.840)". | Everyone | Remove from pitch, Q&A, FINDINGS. Say instead: "It catches people the runway calls healthy; it survives correction across 28 tests and adjustment for balance size." |

## Should fix
| # | Issue | Owner | Fix |
|---|---|---|---|
| 4 | Realistic runway and Monte Carlo disagree (20111 job loss: realistic 1.3 months, simulation median month 3, 15% make 6 months). Realistic uses a 12-month window; simulate replays 24. | P1 | Same window for both, then make the simulation the headline and call the deterministic number "simple estimate". |
| 5 | Trough is a rank, not a probability. | P1 | Logistic fit: trough → P(first overdraft in next 12 months), trained 2023→2024, validated 2025, with Brier score + calibration bars. Card then says "X% chance of first overdraft in 12 months". |
| 6 | Gemini output not schema-constrained. | P3 | Pass `response_schema` with the field types in `parse_twist`. |
| 7 | Every page imports unused modules (ai, pcurve, preset, ...). | page owners | Clean before the repo goes public. |
| 8 | Know tab too dense for a 5-second read. | P2 | Summary sentence first (F2), one chart visible, rest in an expander; chart titles state the takeaway (F4). |

## New files from this review
- `api.py` / `openapi.json`: drafted and tested, but **held back from the repo** until frontend work starts (see `docs/FRONTEND.md`).
- `docs/REACT_PLAN.md`: stack, screens, owners, timeline.

## Pitch order
1. 93172 in the Time Machine (Dec 2024): averaged $18.5K, standard runway "no shortfall", but dipped to $238; flagged riskiest 2%; overdrawn 13 days in January.
2. 14.6× across three years; survives controls (OR 16.8) and multiple-testing correction.
3. Overdrafts matter: 76 of 76 overdrawn borrowers defaulted; 27 loans ($3.5M) went to already-overdrawn customers, all defaulted.
4. "Pick any account and any twist."

Limits to say first: 1990s Czech data re-dated (not Tangerine customers); money in ≠ pay (mostly cash); status D is partly "in debt" by definition; it's an early-warning signal, not causal.

## Log (newest last; one line per merged change, both lanes)
| Date | Lane | Change |
|---|---|---|
| Nov 7 | engine | Time Machine lookahead fixed in Streamlit (`ui/context.py` cuts data at `asof`; `Context.d_full` only for the reveal). 93172 Dec 2024 now reads "no shortfall (120+)", trough rank 1.6%, low $238. |
| Nov 7 | engine | Monte Carlo calibration: raw sim predicted 13.5% would break in 2025 vs 1.6% actual. New `engine.calibrate_break`, `engine.overdraft_risk` (Platt, fit 2023→2024, validated 2025: Brier 0.0152 vs base 0.0158, AUC 0.863). `evidence.json` → `sim_calibration`. |
| Nov 7 | engine | Watchlist `realistic_runway_ei` now equals the Know/Shock realistic runway (EI ends after 6 months); was different on 23.5% of accounts. `net_flow_filter` adds `has_trend`, `band_from` (handoff #2). |
| Nov 7 | ai | `_sanitize` coerces `return_to_work_month` (string from an LLM crashed the simulation); Gemini twist call uses `response_schema` (handoff #6). New contract test between lanes. |
| Nov 7 | engine | Dip product: `engine.cushion` (buffer = typical dip, personal alert, top-up now, usual dip day), `engine.load_dip_days` (transactions.csv), `make_plan()["cushion"]`. `evidence.json → impact`: flag 10% → 34/55 first overdrafts caught; buffer covers 27/34, $78K drawn of $2.9M; alert 23/34 early (3 mo) vs $100 alert 1/34. |
| Nov 8 | engine | Simulation starts at latest balance (E8); calibration refit `SIM_CAL_A/B = -3.3243/0.4567` → 2025 AUC 0.877, Brier 0.0145. `simulate` split into `_sim_paths` (same results). `optimize_cuts` adds `share_of_futures_protected`; `outcome` text now "a bad case (9 in 10 futures do better)" / "a typical case (median future)". Pinned value in `test_calibration_is_monotone_and_bounded` updated 0.049 → 0.035 because the model was refit on purpose. 93172 Dec 2024 risk now 4.0%. |
| Nov 8 | ai | `ai.plan_facts()` (use instead of building facts in plan.py; leads with cushion, `futures_lasting_6_months_of_10` replaces `chance_6_months_pct`), `ai.verify_wording()`, `ai.parse_twist_checked()` → `{settings, source, disagree, chips}`, `ai.describe_scenario()`. Template leads with the cushion. Fake-Gemini tests. |
| Nov 8 | engine | **Forward loan payments.** `realistic_profile` now counts the loan payment owed from now on (`loan_payment_due`, `loan_adjust`, `spending_history`); a loan granted inside the 12-month window was invisible before (186 accounts at Dec 2024). 93172 Dec 2024: realistic runway 26.7 → **2.4 months**, calibrated risk 4.0% → **13.8%**. Same adjustment in `_sim_paths` and `realistic_runway_vec`. Calibration refit `SIM_CAL_A/B = -3.3602/0.4574`: 2025 AUC 0.877 → **0.882**, Brier 0.01448 → **0.01418**. Pinned test values updated because the model changed on purpose: 20111 realistic 1.3 → 1.2, employment-share (1.3, 3.4) → (1.2, 3.1), portfolio realistic@6 0.408 → 0.407, 93172 furnace usable $392 → $6, API pitch risk 0.040 → 0.138. |
| Nov 8 | engine | **Diagnosis → next best action** (`engine.diagnose`, `diagnosis_signals`; thresholds `INCOME_DROP`, `NEW_LOAN_BURDEN`, `SWING_THRESHOLD` fixed from 2023). Most urgent first: already overdrawn → recovery plan; money in fell → call first; heavy new loan → loan review; swings → auto-save; dip → cushion + alert. `evidence.json → diagnoses` (both years, incl. rejected bill-timing idea and the combined model that was not adopted). Diagnosis tests added to the extended multiple-testing family. Loan outcome hidden in Time Machine mode (`ui/context.py`). |
| Nov 8 | engine | `test_evidence_self_correction_and_extended_bh`: the family count is now base + 8 steering + 8 diagnosis tests (was base + 8), asserted explicitly so a missing test still fails. |
| Nov 8 | ai | Brief facts carry `first_action` (engine's most urgent action), `new_loan_payment_per_month`, and historical money out; brief prompt and template lead with the matched action, then the cushion. |
| Nov 8 | web | Customer: "Why they're at risk, and what to do" card; Plan leads with the first action; Evidence: reasons table + rejected idea; fixes: phone width (tables), `.how` CSS clash (one word per line), trait formats ("aver*age*" matched "age"), "−$90K" axis, "the a bad case". |
| Nov 8 | web | Accessibility (checklist from ECC `frontend-a11y`, measured with axe-core 4.10 on all 5 screens): 176 WCAG 2 A/AA violations → **0**. Muted text #8a94a6 → #5f6b7d; filled buttons/badges use `--ours-fill` #c94a0c (white text 4.7:1); title accent #e0560b (large text 3.5:1); watchlist scroll region focusable; dots `role="img"`. Charts keep #f26a1b. |
| Nov 8 | engine | **Loan-approval review rule** (`engine.loan_check`, `evidence.loan_policy`): hold if overdrawn before the loan or riskiest 10% by trough, data before the loan month only, nothing fit on loan outcomes. 682 loans: holds 17%, catches 41/76 defaults, 34.7% vs 6.2% (clean B-only: 12/31, 10.2% vs 3.4%, p = 0.003). 93172's $167K loan would have been held. |
| Nov 8 | engine | **Lookahead fix:** 158 loans granted in 2025 appeared in the Dec 2024 view (`ui/context.py` now hides loans starting after asof; test `test_future_loans_hidden_in_time_machine`). |
| Nov 8 | product | **No-risk actions first** (engine diagnosis, Plan, AI prompts/templates EN/FR): alert + call, then auto-transfer from savings, a small overdraft limit only after a call. Customer messages no longer offer credit. |
| Nov 8 | evidence | **Monitoring** (`evidence.monitoring`): PSI drift, AUC per year, calibration, data quality vs stated thresholds (OSFI E-23 3.6 sets none). No breaches. Segment table: `effect` big / small / none (significant ≠ meaningful). |
| Nov 8 | sdlc | **CI** (`.github/workflows/ci.yml`): compile + data-free tests + dashboard type-check/build on every PR; data tests skip with a reason in CI (`tests/conftest.py`) and run locally. **Model card** in E-23 format: `docs/MODEL_CARD.md`. |
| Nov 8 | evidence | **Fairness** (`evidence.fairness`): flag and catch rates by gender and age, 2024 + 2025. Flag-rate ratio women/men 1.12, 0.86 (four-fifths band); catch-rate gap flips direction (71/50 → 50/72), significant in neither (p 0.30, 0.10). Two fairness rows added to monitoring. `evidence.lessons`: failed ideas grouped (rejected / not claimed / one year only) with what we did. |
| Nov 8 | sdlc | **Scale proof:** `sql/trough.sql` (standard window functions) returns the same trough and riskiest-10% flags as `engine.ltr_table` on all accounts (test, Dec 2024 + Dec 2025). |
| Nov 8 | docs | `docs/JUDGE_QA.md`: likely questions by judge type with one-line answers + pilot plan (shadow → controlled pilot → scale). Model card: fairness + scale sections. Evidence page: fairness table, lessons table, limits as limit → what we did → production fix. |
| Nov 8 | all | **Recovered** `1a52f5e` (Pitch mode) and `a0da90b` (fairness, SQL, Q&A) onto main: they were pushed to `p1/loan-policy` after PR #14 merged. Survival/challenger work from the Mac session cherry-picked on top (see below). |
| Nov 8 | engine/web | **The whole book:** `engine.book_tiers` (overdrawn / act / watch / stable / new), `evidence.json -> book` (Dec 2022/23/24 cohorts), `/api/book` (rates from a year already over: no lookahead), Overview card. Dec 2024 cohort: 8.5% of customers (overdrawn + riskiest 10%) produced 60% of 2025's overdrafts; stable 57% overdrew 0.4% in every year; too-new accounts 21% (a disclosed gap). |
| Nov 8 | engine/web | Optimiser docstring and Streamlit text no longer claim receding-horizon/MPC (it solves once). Stress: exposure profile (EE, 95% PFE) fold-out from the existing simulation, labelled uncalibrated. |
| Nov 8 | ai | `scripts/eval_ai.py` -> `docs/AI_EVAL.md`: rules 22/22 tuned vs 8/16 held-out (overfit). Run on a Vertex-configured machine to add Gemini's rows. Do not tune the rules to the held-out cards. |
| Nov 8 | all | **docs/SPEC.md** added: the single source of truth (problem, use case, data, definitions, proven results, screens, AI, governance, status, next steps); CLAUDE.md points to it and no longer says "Streamlit app" / "no API". Whole-book sentence fixed to describe one population (tested cohort): today 8.5% of customers → 60% of overdrafts. |
| Nov 8 | engine | **New accounts scored:** the trough fails on them (AUC 0.55–0.71); `new_account_swing` (sd of money in, opening month dropped, top 10% of 3–11-month accounts) chosen on 2023+2024 by catches at a 10% flag, confirmed on 2025 (13/32, 18.6% vs 3.0%, p<0.001). New tier `new_hot`. `evidence.json -> new_accounts`; 12 tests added to the extended family: **48 of 57** survive. Whole book (Dec 2024 → 2025): 10% of customers → 68% of overdrafts. Pinned test values updated on purpose: book sentence 0.085/0.60 → 0.101/0.684. |
| Nov 8 | ai | **Offline twist reader generalised** (number words, pay-cut/fraction phrasings, bill-rise verbs, job-loss words, any one-off $). Protocol: first held-out set → dev set; fresh `HELD_OUT_V2` frozen first and scored once: **15/16 (94%)** (was 8/16 on the first held-out). Test updated to the new protocol on purpose. Never tune to `HELD_OUT_V2`. |
| Nov 8 | engine | Fixed `evidence.main()` order: `new_accounts` now runs before the extended multiple-testing family (a full rebuild had silently given 37 of 45 because the 12 tests were added after the family was built). `test_evidence_self_correction_and_extended_bh` now counts them, so this cannot recur. |
| Nov 8 | engine/evidence | **Survival** (`engine.survival_cohort/curves/when_overdraft`, `evidence.survival`): KM + log-rank + discrete-time hazard logit (Cox PHReg failed on monthly ties). Flag HR 11.2 (2022 cohort), 12.4 (2023); 2–4× higher in first 6 months. New Context field `when` (Customer "When?" line; cohort = asof year − 2, no lookahead). **Challenger** (`evidence.challenger`): HistGB on 12 features 39 vs 34 of 55, McNemar p 0.18, top feature = trough → trough kept. |
| Nov 8 | ai | **Gemini measured** (`docs/AI_EVAL.md`, Vertex gemini-3.5-flash): 22/22 tuned, 15/16 dev, **14/16 held-out v2**, median 1.3 s; rules 15/16 on v2. Scorer not changed after seeing results. |
| Nov 8 | engine | **Risk appetite + haircut:** `cushion()["buffer_conservative"]` (75th-percentile dip, `BUFFER_CONSERVATIVE_Q`); `liquidity_trough()["haircut"]` = 1 − trough; `evidence.json -> buffer_confidence` (2024, 2025: 75th pct is the knee, ~$5K more drawn for +6–15 pts coverage). Plan shows the option and the curve; Customer shows the haircut. Default buffer unchanged (median, fixed before the backtest years). |
| Nov 8 | ai | Field definitions clarified after the Gemini run (exact decimals for fractions; `return_to_work_month` = months out of work, as `engine.simulate` uses it). Those two v2 cards are no longer blind for Gemini: noted in `docs/AI_EVAL.md`. |
| Nov 8 | ai | Reviewed p1/business; Gemini re-run after field definitions: still 14/16 held-out (not blind on 2 cards), timeouts 2 → 1. Logged in AI_EVAL.md. |
| Nov 8 | web | Card text tightened: trough note one line (haircut inline, glossary explains it); Plan auto-transfer note shortened (conservative amount kept, "a limit only after a call" kept); risk-appetite fold shows its headline (29 vs 27 of 34, $5K more drawn) without a click. No new numbers. |
| Nov 8 | ship | Wiring audit: every API field is read by a screen except last_activity, n_in_view; 4 evidence sections were Streamlit-only → new Evidence card. Contract test parses screens for evidence reads. Docker image verified (scripts/smoke.py 8/8). DEPLOY.md now Vertex (no key). TEST_PLAN.md, docs/guide (Word + PDF). |
| Nov 8 | web | Full screen run-through: every built feature found on its screen, no NaN/undefined, all charts have data. Customer header now shows every customer's tier (was only 'Riskiest 10%' or new-account badges). |
| Nov 8 | ship | **Deployed** to Cloud Run: https://runway-1085585470420.us-central1.run.app (image built locally from main a2a0746, pushed to Artifact Registry; --source failed on build-account permissions). Smoke 8/8, Gemini on Vertex live. Added .gcloudignore (else --source drops data/). |
