# Graph Report - tangerine-resilience-engine-94bfb1  (2026-11-09)

## Corpus Check
- 88 files · ~103,723 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .ini 1, .css 1)

## Summary
- 1041 nodes · 2154 edges · 80 communities (65 shown, 15 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 271 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8b6278ca`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Runway React frontend: plan and rules
- test_acceptance.py
- app.py
- Claude Code guide: what to give it, how to watch it, how to track progress
- verify_numbers
- FRONTEND.md: how the React app connects to the logic
- Part A. Strategy and setup
- test_app_smoke.py
- 6. Function contract (don't rename without telling everyone)
- Data pipeline: from raw files to every number on screen
- Contributing: getting started, Git, and Claude Code
- Architecture: the tech, and how everything works
- Findings log (Tangerine: Resilience Rewired)
- pull_request_template.md
- create_issues.sh
- .claude/CLAUDE.md
- api.ts
- Part B. The modules
- What we found, in plain words
- Runway 🍊
- package.json
- multiple_testing
- Ponytail
- Data audit
- api.py
- compilerOptions
- compilerOptions
- tsconfig.json
- challenger
- test_api.py
- Tasks: who builds what
- DataFrame
- _FakeGemini
- Runway: a liquidity early warning for Tangerine (Devpost write-up draft)
- Deploy Runway: Docker locally, then Google Cloud Run
- data.py
- Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)
- eval_ai.py
- M4. Liquidity Trough Ratio, watchlist, Time Machine
- test_bank_case.py
- ai.py
- pytest
- main
- with
- engine.py
- test_formula_all_accounts.py
- advisor_brief
- M2. Answer-key engine (the judges' formula)
- _ltr_backtest
- Model card: Runway liquidity early warning
- Judge Q&A: one-line answers, with the number to point at
- Log (newest last; one line per merged change, both lanes)
- overdraft_risk
- parametrize
- parse_twist_offline
- Bank readiness: what a bank can run today, how it maps to model-risk guidance, and what is still missing
- monitoring
- numpy
- runway
- CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)
- Runway QA report: every page, every kind of customer, every Time Machine date
- Runway: product and engineering spec (single source of truth)
- CTO review: is Runway a winner? (Sat Nov 7, evening)
- test_like_this.py
- _correction_scores
- Twist-card reader evaluation
- verify_numbers
- Test plan: how Runway is checked, from a code change to a live link
- fixture

## God Nodes (most connected - your core abstractions)
1. `Log (newest last; one line per merged change, both lanes)` - 36 edges
2. `6. Function contract (don't rename without telling everyone)` - 30 edges
3. `main()` - 29 edges
4. `C2. Integration contract` - 29 edges
5. `3. Definitions (engine.py)` - 27 edges
6. `2. Test cases for each financial calculation shown on screen` - 24 edges
7. `Scenario` - 21 edges
8. `load_all()` - 21 edges
9. `pct()` - 19 edges
10. `CustomerScreen()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Step 7 · Show it (`ui/`)` --references--> `Scenario`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py
- `Who owns which files` --references--> `Scenario`  [INFERRED]
  docs/TASKS.md → engine.py
- `Know the customer: `GET /api/customer/{acct}?asof=`` --references--> `what_happened_next()`  [INFERRED]
  docs/FRONTEND.md → engine.py
- `6. Function contract (don't rename without telling everyone)` --references--> `flags_html()`  [INFERRED]
  docs/ARCHITECTURE.md → ui/style.py
- `2. Data contract` --references--> `check_monthly_contract()`  [INFERRED]
  docs/BANK_READINESS.md → engine.py

## Import Cycles
- None detected.

## Communities (80 total, 15 thin omitted)

### Community 0 - "Runway React frontend: plan and rules"
Cohesion: 0.22
Nodes (8): API (full spec in openapi.json, live docs at /docs), Claude Code prompt for each React engineer (start of session), Hard rules (same as CLAUDE.md, plus three), Run it, Runway React frontend: plan and rules, Screens and the "fancy" that also scores points, Timeline, Who does what

### Community 1 - "test_acceptance.py"
Cohesion: 0.09
Nodes (16): M9. Evidence engine, test_evidence_buffer_confidence_curve(), test_evidence_confounders(), test_evidence_fairness_and_lessons(), test_evidence_impact(), test_evidence_loan_policy(), test_evidence_loans_and_holes(), test_evidence_monitoring_no_breaches() (+8 more)

### Community 2 - "app.py"
Cohesion: 0.14
Nodes (16): pcurve(), wl(), render(), render(), render(), render(), render(), apply_settings() (+8 more)

### Community 3 - "Claude Code guide: what to give it, how to watch it, how to track progress"
Cohesion: 0.22
Nodes (9): 1. What Claude Code needs (all already in this repo), 2. Which IDE: see everything that's happening, 3. The workflow for one task (10–40 minutes), 4. The project slash commands (in `.claude/commands/`), 5. Tracking progress as a team, 6. Prompt library (copy, edit the bits in <>), 7. Things to watch for (and what to say), 8. Should we install the softaworks/agent-toolkit skills? (+1 more)

### Community 4 - "verify_numbers"
Cohesion: 0.13
Nodes (12): _load_env(), plan_facts(), template_plan(), verify_wording(), write_plan(), 7. AI component (E-23 AI/ML expectations), _facts(), test_gemini_plan_rejected_when_it_says_chance() (+4 more)

### Community 5 - "FRONTEND.md: how the React app connects to the logic"
Cohesion: 0.11
Nodes (17): 1. Rules (break one and the numbers on screen stop matching the judges'), 2. Run it, 3. App state: three things drive everything, 4. Endpoints, 5. Types (copy into `web/src/types.ts`), 6. Screen by screen: which call, which field, 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4), 9. Paste-ready Claude Code prompts (Streamlit now; same rules apply to React) (+9 more)

### Community 6 - "Part A. Strategy and setup"
Cohesion: 0.14
Nodes (13): A1. How we win against ~200 people, A2. What we're building (architecture), A3. Tech stack and why, A4. How to work with Claude Code, A5. Build order and time budget, C1. Stats and algorithms cheat sheet, C3. Submission checklist, C4. Demo script, live-twist runbook, Q&A (+5 more)

### Community 7 - "test_app_smoke.py"
Cohesion: 0.25
Nodes (9): at(), _click(), _no_errors(), test_controls(), test_custom_twist_card(), test_presets_plan_reset(), test_random_accounts(), test_time_machine_and_demo_account() (+1 more)

### Community 8 - "6. Function contract (don't rename without telling everyone)"
Cohesion: 0.16
Nodes (17): 5.4 Credit view and bank view (`loan_risk`, `portfolio_curve`), 6. Function contract (don't rename without telling everyone), C2. Integration contract, M11. Streamlit app, all_profiles(), ei_benefit(), loan_adjust_vec(), loan_risk() (+9 more)

### Community 9 - "Data pipeline: from raw files to every number on screen"
Cohesion: 0.18
Nodes (10): Data pipeline: from raw files to every number on screen, How to add a new calculation (the safe way), Step 1 · Get the data, Step 2 · Check your setup, Step 3 · Audit the data, and the "cleaning" decisions, Step 4 · Load (`engine.load()`), Step 5 · Per-customer numbers (`engine.py`), Step 6 · Prove the findings (`evidence.py`) (+2 more)

### Community 10 - "Contributing: getting started, Git, and Claude Code"
Cohesion: 0.22
Nodes (9): Contributing: getting started, Git, and Claude Code, Part 1 · P1 only: create the repo (once), Part 2 · Everyone: get it running, Part 3 · Install Claude Code (everyone), Part 4 · The workflow for every task, Part 5 · Working with Claude Code in this repo, Part 6 · Pull request rules, Part 7 · When things go wrong (+1 more)

### Community 11 - "Architecture: the tech, and how everything works"
Cohesion: 0.29
Nodes (6): 1. The big picture, 3. Tech stack, 4. The data, simply, 7. Testing, 8. Performance, Architecture: the tech, and how everything works

### Community 12 - "Findings log (Tangerine: Resilience Rewired)"
Cohesion: 0.33
Nodes (5): Audit notes (Sat ~1:30 PM), Explain-it-back, Explain-it-back (v2), Findings log (Tangerine: Resilience Rewired), Hypotheses tested

### Community 13 - "pull_request_template.md"
Cohesion: 0.50
Nodes (3): Checklist, Screenshot, What this changes

### Community 19 - "api.ts"
Cohesion: 0.07
Nodes (80): react, @tanstack/react-query, api, Asof, ASOF_LABEL, BankCase, BankCaseReq, BankCaseRow (+72 more)

### Community 20 - "Part B. The modules"
Cohesion: 0.11
Nodes (18): M0. Project setup, M1. Data loading and audit, M4b. Credit view and bank view, M5. Kalman filter (signal vs noise), M6. Monte Carlo simulation and exposure profile, M7. Optimised cut schedule (linear programming), M8. Plan generator, Part B. The modules (+10 more)

### Community 21 - "What we found, in plain words"
Cohesion: 0.25
Nodes (7): 1. Healthy on average, close to zero at the low point (the headline), 2. An overdraft is the line between repaid and defaulted loans, 3. Where the standard runway formula misleads, 4. A trap we caught, Limits (we say these first), The demo customer: account 93172, What we found, in plain words

### Community 22 - "Runway 🍊"
Cohesion: 0.25
Nodes (8): Commands, Data and sources, Event rules that affect the code, Quick start (10 minutes), Repo map, Runway 🍊, The four rules, What we're building (plain English)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @fontsource-variable/plus-jakarta-sans, globals, react-dom, recharts (+33 more)

### Community 24 - "multiple_testing"
Cohesion: 0.20
Nodes (4): multiple_testing(), _p_auc(), _p_ci(), _watchlist_hits()

### Community 25 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 26 - "Data audit"
Cohesion: 0.40
Nodes (4): 1. Files, 2. Integrity checks, 3. Quirks, and what we do about each, Data audit

### Community 28 - "api.py"
Cohesion: 0.08
Nodes (21): accounts(), bank_case(), BankCaseReq, book(), _book(), clean(), ctx(), customer() (+13 more)

### Community 30 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 31 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+10 more)

### Community 33 - "challenger"
Cohesion: 0.25
Nodes (3): challenger(), _p_boot(), trough_evidence()

### Community 35 - "test_api.py"
Cohesion: 0.07
Nodes (6): test_bank_case_endpoint(), test_call_list_csv_matches_the_table(), test_every_evidence_section_a_screen_reads_exists(), test_future_loans_hidden_in_time_machine(), test_time_machine_pitch_moment(), test_unforecast_customers_get_their_tiers_tested_rate()

### Community 36 - "Tasks: who builds what"
Cohesion: 0.22
Nodes (9): Definition of done for any task, First 30 minutes (everyone), P1: Sukhman (engine and data lead), P2: Frontend A (Watchlist, Know, look and feel), P3: Frontend B + AI (Shock, Plan, Gemini), P4: Evidence page + submission (optional 4th person), Tasks: who builds what, Timeline (+1 more)

### Community 37 - "DataFrame"
Cohesion: 0.11
Nodes (11): 2. Data, committed_outflows(), like_cohort(), like_features(), like_query(), load(), load_dip_days(), load_standing_orders() (+3 more)

### Community 38 - "_FakeGemini"
Cohesion: 0.25
Nodes (4): _FakeGemini, test_gemini_path_flags_misread_card(), test_slow_gemini_falls_back_to_rules_fast(), generate_content()

### Community 39 - "Runway: a liquidity early warning for Tangerine (Devpost write-up draft)"
Cohesion: 0.22
Nodes (8): How a bank would roll it out, Runway: a liquidity early warning for Tangerine (Devpost write-up draft), Sources, The question, What we built, What we don't claim (said first), What we found, Who it's for

### Community 40 - "Deploy Runway: Docker locally, then Google Cloud Run"
Cohesion: 0.33
Nodes (5): 1. Run the container on your laptop (no cloud needed), 2. Deploy to Cloud Run (about 10 minutes, uses the event credits), 3. Check it, 4. Take it down after judging, Deploy Runway: Docker locally, then Google Cloud Run

### Community 41 - "data.py"
Cohesion: 0.29
Nodes (12): evidence(), health(), build_context(), Context, ai_backend(), dip_days(), like_table(), load_all() (+4 more)

### Community 42 - "Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)"
Cohesion: 0.29
Nodes (6): Decisions, Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM), Must fix (judges will see these), New files from this review, Pitch order, Verified (don't re-check)

### Community 43 - "eval_ai.py"
Cohesion: 0.22
Nodes (5): init(), correct(), main(), run(), call()

### Community 44 - "M4. Liquidity Trough Ratio, watchlist, Time Machine"
Cohesion: 0.29
Nodes (8): M4. Liquidity Trough Ratio, watchlist, Time Machine, reasons(), _ltr_backtest(), test_example_93172(), test_trough_backtest_2025(), test_trough_needs_12_months(), test_trough_other_years(), test_watchlist_time_machine()

### Community 45 - "test_bank_case.py"
Cohesion: 0.08
Nodes (10): main(), out(), main(), pytest_collection_modifyitems(), _ok(), test_bank_case_arithmetic_and_inputs(), test_capacity_section_reproduces_from_the_data(), test_data_contract_accepts_a_good_file_and_names_each_problem() (+2 more)

### Community 46 - "ai.py"
Cohesion: 0.15
Nodes (7): customer_facts(), customer_message(), template_message(), brief(), _facts(), message(), test_brief_and_message_offline_templates_verify()

### Community 47 - "pytest"
Cohesion: 0.12
Nodes (18): M3. Realistic runway, test_calibration_is_monotone_and_bounded(), test_conservative_buffer_and_haircut(), test_cushion_93172_time_machine(), test_dip_days(), test_ei_cap_constant(), test_ei_cap_finding(), test_employment_share_assumption() (+10 more)

### Community 48 - "main"
Cohesion: 0.13
Nodes (6): lessons(), loan_evidence(), loan_policy(), main(), multiple_testing_extended(), new_accounts()

### Community 49 - "with"
Cohesion: 0.10
Nodes (23): run, jobs, python, web, name, on, pull_request, push (+15 more)

### Community 50 - "engine.py"
Cohesion: 0.14
Nodes (9): bank_case(), explain_difference(), pilot_sample_size(), Profile, Realistic, repeat_overdraft(), survival_score_month(), verdict() (+1 more)

### Community 51 - "test_formula_all_accounts.py"
Cohesion: 0.23
Nodes (6): checked(), _independent_inputs(), _independent_runway(), test_edge_cases_are_covered_and_counted(), test_per_account_profile_matches_too(), test_runway_matches_an_independent_implementation_on_36000_cases()

### Community 52 - "advisor_brief"
Cohesion: 0.29
Nodes (5): advisor_brief(), _generate(), template_brief(), _write(), test_gemini_brief_rejected_when_number_invented()

### Community 53 - "M2. Answer-key engine (the judges' formula)"
Cohesion: 0.29
Nodes (7): M2. Answer-key engine (the judges' formula), test_edge_case_counts(), test_profile_20111(), test_runway_rules(), test_twist_distribution(), test_twists_20111(), test_vectorised_matches_scalar()

### Community 55 - "_ltr_backtest"
Cohesion: 0.18
Nodes (6): capacity(), confounders(), fairness(), _features(), _ltr_backtest(), segment_profile()

### Community 56 - "Model card: Runway liquidity early warning"
Cohesion: 0.18
Nodes (10): 1. Inventory record (E-23 Appendix 1), 2. Purpose and design (E-23 3.1, 3.3), 3. Data (E-23 3.2), 4. Validation (E-23 3.4), 4b. Fairness, 4c. Scale, 5. Ongoing monitoring (E-23 3.6), 6. Limits and judgement calls (+2 more)

### Community 58 - "Judge Q&A: one-line answers, with the number to point at"
Cohesion: 0.22
Nodes (8): Bankers (Scotiabank, RBC, CIBC, Sun Life), Consultants (Accenture, EY, PwC): the pilot plan, Data platforms (Snowflake, Dataiku, Thomson Reuters), Finance terms (if a banker or quant uses them), Judge Q&A: one-line answers, with the number to point at, Professor / methodology, Quant / risk (e.g. XVA, model risk, control backgrounds), The 60-second pitch (Pitch mode, press → five times)

### Community 60 - "Log (newest last; one line per merged change, both lanes)"
Cohesion: 0.11
Nodes (23): 5.7 Smallest cuts: optimiser (`optimize_cuts`), Log (newest last; one line per merged change, both lanes), 1. Problem, users, use case, 3. Definitions (engine.py), 2. Test cases for each financial calculation shown on screen, _acct(), book_tiers(), check_monthly_contract() (+15 more)

### Community 61 - "overdraft_risk"
Cohesion: 0.19
Nodes (10): 5.5 Signal vs noise: Kalman filter (`kalman_level`, `net_flow_filter`), Fixed today (engine and AI lanes, all tests green: 62 fast, 5 slow, 6 UI), Round 2: answering the "finding ≠ product" critique, Still open (ranked), What I found (strict), 8. Not in the API yet (ask P1, don't build in React), calibrate_break(), kalman_level() (+2 more)

### Community 62 - "parametrize"
Cohesion: 0.29
Nodes (6): backend(), M10. AI layer, test_number_verifier(), test_twist_reader_offline(), test_verdict(), test_answer_key_20111()

### Community 63 - "parse_twist_offline"
Cohesion: 0.15
Nodes (14): describe_scenario(), parse_twist(), parse_twist_checked(), parse_twist_offline(), _sanitize(), Round 3 (backend + AI hardening), 8b. New backend pieces (round 3) the UI should use, Should fix (+6 more)

### Community 64 - "Bank readiness: what a bank can run today, how it maps to model-risk guidance, and what is still missing"
Cohesion: 0.25
Nodes (7): 1. What a bank can do today, 2. Data contract, 3. Model-risk mapping (US SR 11-7 and Canada's OSFI E-23), 4. Fairness and fair lending, 5. Pilot, 6. Not built yet, and why, Bank readiness: what a bank can run today, how it maps to model-risk guidance, and what is still missing

### Community 65 - "monitoring"
Cohesion: 0.25
Nodes (3): monitoring(), _psi(), test_psi_flags_drift_and_not_noise()

### Community 66 - "numpy"
Cohesion: 0.14
Nodes (7): realistic_vec(), buffer_confidence(), formula_holes(), sim_calibration(), _sim_cohort(), survival(), test_sql_trough_matches_engine()

### Community 67 - "runway"
Cohesion: 0.16
Nodes (13): Hard rules, 2. What happens when someone clicks, 5.1 The judges' runway (`profile`, `runway`), 5.2 Our realistic runway (`realistic_profile`, `realistic_runway`), 5.3 The warning score: Liquidity Trough Ratio (`ltr_table`, `liquidity_trough`, `watchlist`), 5.6 "Do they make it?": Monte Carlo simulation (`simulate`), 5.8 The plan (`make_plan`), 5.9 AI (`ai.py`) (+5 more)

### Community 68 - "CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)"
Cohesion: 0.29
Nodes (6): CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track), Commands, graphify, Start here, Where things live, Working style

### Community 69 - "Runway QA report: every page, every kind of customer, every Time Machine date"
Cohesion: 0.33
Nodes (5): 1. What was tested, 2. What was wrong, and what we changed, 3. What is on screen, and is it worth it, 4. Where we stand, Runway QA report: every page, every kind of customer, every Time Machine date

### Community 70 - "Runway: product and engineering spec (single source of truth)"
Cohesion: 0.33
Nodes (5): 4. What is proven (evidence.json), 5. Product: screens and API, 7. Governance and engineering, 8. Status (Nov 8), Runway: product and engineering spec (single source of truth)

### Community 71 - "CTO review: is Runway a winner? (Sat Nov 7, evening)"
Cohesion: 0.20
Nodes (9): CTO review: is Runway a winner? (Sat Nov 7, evening), Datathon services: use / skip, Is the maths "quant level"? Direct answers, Next 6 hours (in order), Pitch (60 seconds, in this order), React pivot: decision, Round 4 (diagnosis → action; the loan nobody counted), Verdict (+1 more)

### Community 72 - "test_like_this.py"
Cohesion: 0.13
Nodes (6): book(), diagnoses(), impact(), test_like_this_picks_the_nearest_and_counts_them(), test_pool_matches_the_three_year_backtest(), test_pool_never_uses_the_future()

### Community 78 - "Twist-card reader evaluation"
Cohesion: 0.50
Nodes (3): Misses, Note (Nov 8): field definitions clarified after the Gemini run, Twist-card reader evaluation

### Community 79 - "verify_numbers"
Cohesion: 0.29
Nodes (7): _num(), _numbers(), verify_numbers(), walk(), M12. Differentiators if you're ahead, AI judges (OpenAI, Meta, Microsoft, IBM), test_numbers_reads_french_formats()

### Community 81 - "Test plan: how Runway is checked, from a code change to a live link"
Cohesion: 0.29
Nodes (5): Two Claude Code sessions on this repo, 1. Stages of the lifecycle and what checks each, 3. Known limits of the tests, Test plan: how Runway is checked, from a code change to a live link, test_ai_engine_contract()

### Community 82 - "fixture"
Cohesion: 0.50
Nodes (3): d(), P(), d()

## Knowledge Gaps
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `C2. Integration contract` connect `6. Function contract (don't rename without telling everyone)` to `numpy`, `runway`, `verify_numbers`, `DataFrame`, `Part A. Strategy and setup`, `eval_ai.py`, `verify_numbers`, `main`, `engine.py`, `Log (newest last; one line per merged change, both lanes)`, `overdraft_risk`, `parse_twist_offline`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `Log (newest last; one line per merged change, both lanes)` (e.g. with `describe_scenario()` and `parse_twist_checked()`) actually correct?**
  _`Log (newest last; one line per merged change, both lanes)` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_acceptance.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09247311827956989 - nodes in this community are weakly interconnected._
- **Why does `Log (newest last; one line per merged change, both lanes)` connect `Log (newest last; one line per merged change, both lanes)` to `challenger`, `monitoring`, `runway`, `verify_numbers`, `DataFrame`, `numpy`, `test_acceptance.py`, `6. Function contract (don't rename without telling everyone)`, `test_api.py`, `Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)`, `pytest`, `main`, `engine.py`, `_ltr_backtest`, `overdraft_risk`, `parse_twist_offline`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `6. Function contract (don't rename without telling everyone)` (e.g. with `init()` and `all_profiles()`) actually correct?**
  _`6. Function contract (don't rename without telling everyone)` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1417004048582996 - nodes in this community are weakly interconnected._
- **Why does `runway()` connect `runway` to `Claude Code guide: what to give it, how to watch it, how to track progress`, `FRONTEND.md: how the React app connects to the logic`, `6. Function contract (don't rename without telling everyone)`, `Contributing: getting started, Git, and Claude Code`, `engine.py`, `M2. Answer-key engine (the judges' formula)`, `Log (newest last; one line per merged change, both lanes)`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._