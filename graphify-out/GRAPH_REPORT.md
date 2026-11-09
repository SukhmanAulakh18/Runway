# Graph Report - tangerine-resilience-engine-94bfb1  (2026-11-09)

## Corpus Check
- 88 files · ~102,590 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .ini 1, .css 1)

## Summary
- 1036 nodes · 2137 edges · 84 communities (68 shown, 16 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 271 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `290cb89e`
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
- engine.py
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
- parse_twist_checked
- _FakeGemini
- Runway: a liquidity early warning for Tangerine (Devpost write-up draft)
- Deploy Runway: Docker locally, then Google Cloud Run
- data.py
- Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)
- M3. Realistic runway
- M4. Liquidity Trough Ratio, watchlist, Time Machine
- test_formula_all_accounts.py
- ai.py
- pytest
- main
- with
- engine.py
- Part A. Strategy and setup
- evidence.py
- M2. Answer-key engine (the judges' formula)
- test_bank_case.py
- _ltr_backtest
- Model card: Runway liquidity early warning
- realistic_runway_vec
- Judge Q&A: one-line answers, with the number to point at
- _load_env
- pandas
- overdraft_risk
- parametrize
- test_ai_cards.py
- Bank readiness: what a bank can run today, how it maps to model-risk guidance, and what is still missing
- monitoring
- numpy
- 2. Test cases for each financial calculation shown on screen
- CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)
- Runway QA report: every page, every kind of customer, every Time Machine date
- Runway: product and engineering spec (single source of truth)
- CTO review: is Runway a winner? (Sat Nov 7, evening)
- test_like_this.py
- sim_calibration
- _correction_scores
- Twist-card reader evaluation
- _numbers
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
9. `ltr_table()` - 19 edges
10. `compilerOptions` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Step 4 · Load (`engine.load()`)` --references--> `load()`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py
- `2. Which IDE: see everything that's happening` --references--> `runway()`  [INFERRED]
  docs/CLAUDE_CODE_GUIDE.md → engine.py
- `Part 1 · P1 only: create the repo (once)` --references--> `runway()`  [INFERRED]
  docs/CONTRIBUTING.md → engine.py
- `Make a plan: `POST /api/plan/{acct}` then `POST /api/write-plan`` --references--> `runway()`  [INFERRED]
  docs/FRONTEND.md → engine.py
- `Step 7 · Show it (`ui/`)` --references--> `Scenario`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py

## Import Cycles
- None detected.

## Communities (84 total, 16 thin omitted)

### Community 0 - "Runway React frontend: plan and rules"
Cohesion: 0.22
Nodes (8): API (full spec in openapi.json, live docs at /docs), Claude Code prompt for each React engineer (start of session), Hard rules (same as CLAUDE.md, plus three), Run it, Runway React frontend: plan and rules, Screens and the "fancy" that also scores points, Timeline, Who does what

### Community 1 - "test_acceptance.py"
Cohesion: 0.10
Nodes (15): M9. Evidence engine, test_evidence_buffer_confidence_curve(), test_evidence_confounders(), test_evidence_fairness_and_lessons(), test_evidence_impact(), test_evidence_loan_policy(), test_evidence_loans_and_holes(), test_evidence_monitoring_no_breaches() (+7 more)

### Community 2 - "app.py"
Cohesion: 0.13
Nodes (16): pcurve(), wl(), render(), render(), render(), render(), render(), apply_settings() (+8 more)

### Community 3 - "Claude Code guide: what to give it, how to watch it, how to track progress"
Cohesion: 0.22
Nodes (9): 1. What Claude Code needs (all already in this repo), 2. Which IDE: see everything that's happening, 3. The workflow for one task (10–40 minutes), 4. The project slash commands (in `.claude/commands/`), 5. Tracking progress as a team, 6. Prompt library (copy, edit the bits in <>), 7. Things to watch for (and what to say), 8. Should we install the softaworks/agent-toolkit skills? (+1 more)

### Community 4 - "verify_numbers"
Cohesion: 0.16
Nodes (13): _generate(), template_plan(), verify_numbers(), verify_wording(), _write(), write_plan(), M12. Differentiators if you're ahead, AI judges (OpenAI, Meta, Microsoft, IBM) (+5 more)

### Community 5 - "FRONTEND.md: how the React app connects to the logic"
Cohesion: 0.12
Nodes (16): 2. Run it, 3. App state: three things drive everything, 4. Endpoints, 5. Types (copy into `web/src/types.ts`), 6. Screen by screen: which call, which field, 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4), 9. Paste-ready Claude Code prompts (Streamlit now; same rules apply to React), Bank view: `POST /api/portfolio {scenario, asof}` (+8 more)

### Community 6 - "Part A. Strategy and setup"
Cohesion: 0.25
Nodes (7): C1. Stats and algorithms cheat sheet, C3. Submission checklist, C4. Demo script, live-twist runbook, Q&A, C5. What can go wrong, and the fallback, Contents, Part C. Reference, Runway build guide: every part, step by step, with Claude Code

### Community 7 - "test_app_smoke.py"
Cohesion: 0.25
Nodes (9): at(), _click(), _no_errors(), test_controls(), test_custom_twist_card(), test_presets_plan_reset(), test_random_accounts(), test_time_machine_and_demo_account() (+1 more)

### Community 8 - "engine.py"
Cohesion: 0.12
Nodes (25): 2. What happens when someone clicks, 5.2 Our realistic runway (`realistic_profile`, `realistic_runway`), 5.3 The warning score: Liquidity Trough Ratio (`ltr_table`, `liquidity_trough`, `watchlist`), 5.4 Credit view and bank view (`loan_risk`, `portfolio_curve`), 5.6 "Do they make it?": Monte Carlo simulation (`simulate`), 5.7 Smallest cuts: optimiser (`optimize_cuts`), 5.8 The plan (`make_plan`), 5.9 AI (`ai.py`) (+17 more)

### Community 9 - "Data pipeline: from raw files to every number on screen"
Cohesion: 0.20
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
Nodes (76): react, @tanstack/react-query, api, Asof, ASOF_LABEL, BankCase, BankCaseReq, BankCaseRow (+68 more)

### Community 20 - "Part B. The modules"
Cohesion: 0.15
Nodes (13): M0. Project setup, M1. Data loading and audit, M5. Kalman filter (signal vs noise), M6. Monte Carlo simulation and exposure profile, M7. Optimised cut schedule (linear programming), M8. Plan generator, Part B. The modules, test_data_loads() (+5 more)

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
Cohesion: 0.20
Nodes (4): challenger(), _features(), _p_boot(), trough_evidence()

### Community 35 - "test_api.py"
Cohesion: 0.07
Nodes (7): test_book_sentence_uses_one_population(), test_call_list_csv_matches_the_table(), test_customer_finance_fields_on_screen(), test_every_evidence_section_a_screen_reads_exists(), test_future_loans_hidden_in_time_machine(), test_time_machine_pitch_moment(), test_unforecast_customers_get_their_tiers_tested_rate()

### Community 36 - "Tasks: who builds what"
Cohesion: 0.25
Nodes (8): Definition of done for any task, First 30 minutes (everyone), P1: Sukhman (engine and data lead), P2: Frontend A (Watchlist, Know, look and feel), P4: Evidence page + submission (optional 4th person), Tasks: who builds what, Timeline, Who owns which files

### Community 37 - "parse_twist_checked"
Cohesion: 0.28
Nodes (6): describe_scenario(), parse_twist_checked(), plan_facts(), Round 3 (backend + AI hardening), _facts(), test_chips_and_checked_parse_offline()

### Community 38 - "_FakeGemini"
Cohesion: 0.17
Nodes (7): advisor_brief(), template_brief(), _FakeGemini, test_gemini_brief_rejected_when_number_invented(), test_gemini_path_flags_misread_card(), test_slow_gemini_falls_back_to_rules_fast(), generate_content()

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
Cohesion: 0.18
Nodes (9): parse_twist(), 8b. New backend pieces (round 3) the UI should use, Decisions, Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM), Must fix (judges will see these), New files from this review, Pitch order, Should fix (+1 more)

### Community 43 - "M3. Realistic runway"
Cohesion: 0.20
Nodes (9): M3. Realistic runway, test_ei_cap_constant(), test_ei_cap_finding(), test_employment_share_assumption(), test_median_mislabel(), test_realistic_ei_ends_after_6_months(), test_realistic_examples(), test_verdict() (+1 more)

### Community 44 - "M4. Liquidity Trough Ratio, watchlist, Time Machine"
Cohesion: 0.29
Nodes (8): M4. Liquidity Trough Ratio, watchlist, Time Machine, reasons(), _ltr_backtest(), test_example_93172(), test_trough_backtest_2025(), test_trough_needs_12_months(), test_trough_other_years(), test_watchlist_time_machine()

### Community 45 - "test_formula_all_accounts.py"
Cohesion: 0.06
Nodes (14): main(), out(), correct(), main(), run(), main(), call(), pytest_collection_modifyitems() (+6 more)

### Community 46 - "ai.py"
Cohesion: 0.12
Nodes (8): customer_facts(), customer_message(), init(), template_message(), brief(), _facts(), message(), test_brief_and_message_offline_templates_verify()

### Community 47 - "pytest"
Cohesion: 0.14
Nodes (14): M4b. Credit view and bank view, test_calibration_is_monotone_and_bounded(), test_conservative_buffer_and_haircut(), test_cushion_93172_time_machine(), test_dip_days(), test_extended_loan_payment_uses_data_fields_only(), test_loan_risk_93172(), test_new_loan_payment_counts_without_lookahead() (+6 more)

### Community 48 - "main"
Cohesion: 0.13
Nodes (6): formula_holes(), lessons(), loan_evidence(), loan_policy(), main(), multiple_testing_extended()

### Community 49 - "with"
Cohesion: 0.10
Nodes (23): run, jobs, python, web, name, on, pull_request, push (+15 more)

### Community 50 - "engine.py"
Cohesion: 0.13
Nodes (9): bank_case(), committed_outflows(), explain_difference(), pilot_sample_size(), Profile, Realistic, repeat_rates(), survival_score_month() (+1 more)

### Community 51 - "Part A. Strategy and setup"
Cohesion: 0.33
Nodes (6): A1. How we win against ~200 people, A2. What we're building (architecture), A3. Tech stack and why, A4. How to work with Claude Code, A5. Build order and time budget, Part A. Strategy and setup

### Community 52 - "evidence.py"
Cohesion: 0.18
Nodes (4): book(), diagnoses(), impact(), new_accounts()

### Community 53 - "M2. Answer-key engine (the judges' formula)"
Cohesion: 0.29
Nodes (7): M2. Answer-key engine (the judges' formula), test_edge_case_counts(), test_profile_20111(), test_runway_rules(), test_twist_distribution(), test_twists_20111(), test_vectorised_matches_scalar()

### Community 54 - "test_bank_case.py"
Cohesion: 0.24
Nodes (6): _ok(), test_bank_case_arithmetic_and_inputs(), test_capacity_section_reproduces_from_the_data(), test_data_contract_accepts_a_good_file_and_names_each_problem(), test_pilot_sample_size_matches_statsmodels_and_grows_as_the_effect_shrinks(), test_real_file_meets_the_contract_and_batch_scoring_matches_the_engine()

### Community 55 - "_ltr_backtest"
Cohesion: 0.20
Nodes (5): capacity(), confounders(), fairness(), _ltr_backtest(), segment_profile()

### Community 56 - "Model card: Runway liquidity early warning"
Cohesion: 0.18
Nodes (10): 1. Inventory record (E-23 Appendix 1), 2. Purpose and design (E-23 3.1, 3.3), 3. Data (E-23 3.2), 4. Validation (E-23 3.4), 4b. Fairness, 4c. Scale, 5. Ongoing monitoring (E-23 3.6), 6. Limits and judgement calls (+2 more)

### Community 57 - "realistic_runway_vec"
Cohesion: 0.31
Nodes (5): loan_adjust_vec(), realistic_runway_vec(), runway_vec(), Shock, watchlist()

### Community 58 - "Judge Q&A: one-line answers, with the number to point at"
Cohesion: 0.22
Nodes (8): Bankers (Scotiabank, RBC, CIBC, Sun Life), Consultants (Accenture, EY, PwC): the pilot plan, Data platforms (Snowflake, Dataiku, Thomson Reuters), Finance terms (if a banker or quant uses them), Judge Q&A: one-line answers, with the number to point at, Professor / methodology, Quant / risk (e.g. XVA, model risk, control backgrounds), The 60-second pitch (Pitch mode, press → five times)

### Community 60 - "pandas"
Cohesion: 0.11
Nodes (19): 1. Problem, users, use case, 3. Definitions (engine.py), all_profiles(), book_tiers(), check_monthly_contract(), like_cohort(), like_features(), like_query() (+11 more)

### Community 61 - "overdraft_risk"
Cohesion: 0.11
Nodes (18): 5.5 Signal vs noise: Kalman filter (`kalman_level`, `net_flow_filter`), Fixed today (engine and AI lanes, all tests green: 62 fast, 5 slow, 6 UI), Round 2: answering the "finding ≠ product" critique, Still open (ranked), What I found (strict), 8. Not in the API yet (ask P1, don't build in React), Log (newest last; one line per merged change, both lanes), _acct() (+10 more)

### Community 62 - "parametrize"
Cohesion: 0.25
Nodes (6): backend(), M10. AI layer, test_number_verifier(), test_sql_trough_matches_engine(), test_twist_reader_offline(), test_answer_key_20111()

### Community 63 - "test_ai_cards.py"
Cohesion: 0.21
Nodes (8): parse_twist_offline(), _sanitize(), P3: Frontend B + AI (Shock, Plan, Gemini), test_ai_engine_contract(), test_card(), test_eval_harness_runs_offline_and_reports_held_out(), test_no_shock_card_stays_empty(), test_sanitize_llm_shaped_output()

### Community 64 - "Bank readiness: what a bank can run today, how it maps to model-risk guidance, and what is still missing"
Cohesion: 0.25
Nodes (7): 1. What a bank can do today, 2. Data contract, 3. Model-risk mapping (US SR 11-7 and Canada's OSFI E-23), 4. Fairness and fair lending, 5. Pilot, 6. Not built yet, and why, Bank readiness: what a bank can run today, how it maps to model-risk guidance, and what is still missing

### Community 65 - "monitoring"
Cohesion: 0.25
Nodes (3): monitoring(), _psi(), test_psi_flags_drift_and_not_noise()

### Community 66 - "numpy"
Cohesion: 0.29
Nodes (3): overdraft_cost(), buffer_confidence(), survival()

### Community 67 - "2. Test cases for each financial calculation shown on screen"
Cohesion: 0.32
Nodes (6): Hard rules, 5.1 The judges' runway (`profile`, `runway`), 2. Test cases for each financial calculation shown on screen, profile(), runway(), when_overdraft()

### Community 68 - "CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)"
Cohesion: 0.25
Nodes (7): CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track), Commands, graphify, Start here, Two Claude Code sessions on this repo, Where things live, Working style

### Community 69 - "Runway QA report: every page, every kind of customer, every Time Machine date"
Cohesion: 0.33
Nodes (5): 1. What was tested, 2. What was wrong, and what we changed, 3. What is on screen, and is it worth it, 4. Where we stand, Runway QA report: every page, every kind of customer, every Time Machine date

### Community 70 - "Runway: product and engineering spec (single source of truth)"
Cohesion: 0.25
Nodes (7): 2. Data, 4. What is proven (evidence.json), 5. Product: screens and API, 6. AI (ai.py), 7. Governance and engineering, 8. Status (Nov 8), Runway: product and engineering spec (single source of truth)

### Community 71 - "CTO review: is Runway a winner? (Sat Nov 7, evening)"
Cohesion: 0.20
Nodes (9): CTO review: is Runway a winner? (Sat Nov 7, evening), Datathon services: use / skip, Is the maths "quant level"? Direct answers, Next 6 hours (in order), Pitch (60 seconds, in this order), React pivot: decision, Round 4 (diagnosis → action; the loan nobody counted), Verdict (+1 more)

### Community 72 - "test_like_this.py"
Cohesion: 0.22
Nodes (3): test_like_this_picks_the_nearest_and_counts_them(), test_pool_matches_the_three_year_backtest(), test_pool_never_uses_the_future()

### Community 73 - "sim_calibration"
Cohesion: 0.40
Nodes (3): 1. Rules (break one and the numbers on screen stop matching the judges'), sim_calibration(), _sim_cohort()

### Community 78 - "Twist-card reader evaluation"
Cohesion: 0.50
Nodes (3): Misses, Note (Nov 8): field definitions clarified after the Gemini run, Twist-card reader evaluation

### Community 79 - "_numbers"
Cohesion: 0.50
Nodes (4): _num(), _numbers(), walk(), test_numbers_reads_french_formats()

### Community 81 - "Test plan: how Runway is checked, from a code change to a live link"
Cohesion: 0.50
Nodes (3): 1. Stages of the lifecycle and what checks each, 3. Known limits of the tests, Test plan: how Runway is checked, from a code change to a live link

### Community 82 - "fixture"
Cohesion: 0.50
Nodes (3): d(), P(), d()

## Knowledge Gaps
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `runway()` connect `2. Test cases for each financial calculation shown on screen` to `Claude Code guide: what to give it, how to watch it, how to track progress`, `FRONTEND.md: how the React app connects to the logic`, `engine.py`, `sim_calibration`, `Contributing: getting started, Git, and Claude Code`, `engine.py`, `M2. Answer-key engine (the judges' formula)`, `realistic_runway_vec`, `pandas`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `Log (newest last; one line per merged change, both lanes)` (e.g. with `describe_scenario()` and `parse_twist_checked()`) actually correct?**
  _`Log (newest last; one line per merged change, both lanes)` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_acceptance.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10098522167487685 - nodes in this community are weakly interconnected._
- **Why does `C2. Integration contract` connect `engine.py` to `2. Test cases for each financial calculation shown on screen`, `verify_numbers`, `Part A. Strategy and setup`, `Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)`, `ai.py`, `main`, `engine.py`, `realistic_runway_vec`, `pandas`, `overdraft_risk`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `6. Function contract (don't rename without telling everyone)` (e.g. with `init()` and `all_profiles()`) actually correct?**
  _`6. Function contract (don't rename without telling everyone)` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13048780487804879 - nodes in this community are weakly interconnected._
- **Why does `Log (newest last; one line per merged change, both lanes)` connect `overdraft_risk` to `challenger`, `monitoring`, `numpy`, `verify_numbers`, `parse_twist_checked`, `test_acceptance.py`, `test_api.py`, `engine.py`, `sim_calibration`, `Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)`, `pytest`, `main`, `evidence.py`, `_ltr_backtest`, `realistic_runway_vec`, `pandas`, `test_ai_cards.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._