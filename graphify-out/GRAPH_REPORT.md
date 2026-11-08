# Graph Report - runway  (2026-11-08)

## Corpus Check
- 77 files · ~90,941 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .ini 1, .css 1)

## Summary
- 927 nodes · 1904 edges · 80 communities (61 shown, 19 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 246 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `638f3d0d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Runway React frontend: plan and rules
- test_acceptance.py
- app.py
- Claude Code guide: what to give it, how to watch it, how to track progress
- write_plan
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
- CTO review: is Runway a winner? (Sat Nov 7, evening)
- test_api.py
- Tasks: who builds what
- CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)
- Runway: product and engineering spec (single source of truth)
- Runway: a liquidity early warning for Tangerine (Devpost write-up draft)
- Deploy Runway to Google Cloud Run (public demo link for Devpost)
- parse_twist
- Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)
- M3. Realistic runway
- M4. Liquidity Trough Ratio, watchlist, Time Machine
- audit_data.py
- ai.py
- pytest
- main
- with
- realistic_runway_vec
- numpy
- data.py
- M2. Answer-key engine (the judges' formula)
- pandas
- confounders
- Model card: Runway liquidity early warning
- monitoring
- Judge Q&A: one-line answers, with the number to point at
- test_ai_cards.py
- eval_ai.py
- overdraft_risk
- _correction_scores
- M10. AI layer
- runway
- load_all
- trough_evidence
- Log (newest last; one line per merged change, both lanes)
- Twist-card reader evaluation
- fixture
- 6. Function contract (don't rename without telling everyone)
- parse_twist
- Part A. Strategy and setup
- M4b. Credit view and bank view
- _load_env

## God Nodes (most connected - your core abstractions)
1. `Log (newest last; one line per merged change, both lanes)` - 36 edges
2. `6. Function contract (don't rename without telling everyone)` - 32 edges
3. `C2. Integration contract` - 29 edges
4. `main()` - 28 edges
5. `Scenario` - 23 edges
6. `3. Definitions (engine.py)` - 22 edges
7. `load_all()` - 19 edges
8. `compilerOptions` - 19 edges
9. `compilerOptions` - 17 edges
10. `ltr_table()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Should fix` --references--> `parse_twist()`  [INFERRED]
  docs/HANDOFF.md → ai.py
- `Step 4 · Load (`engine.load()`)` --references--> `load()`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py
- `2. Which IDE: see everything that's happening` --references--> `runway()`  [INFERRED]
  docs/CLAUDE_CODE_GUIDE.md → engine.py
- `Part 1 · P1 only: create the repo (once)` --references--> `runway()`  [INFERRED]
  docs/CONTRIBUTING.md → engine.py
- `Make a plan: `POST /api/plan/{acct}` then `POST /api/write-plan`` --references--> `runway()`  [INFERRED]
  docs/FRONTEND.md → engine.py

## Import Cycles
- None detected.

## Communities (80 total, 19 thin omitted)

### Community 0 - "Runway React frontend: plan and rules"
Cohesion: 0.22
Nodes (8): API (full spec in openapi.json, live docs at /docs), Claude Code prompt for each React engineer (start of session), Hard rules (same as CLAUDE.md, plus three), Run it, Runway React frontend: plan and rules, Screens and the "fancy" that also scores points, Timeline, Who does what

### Community 1 - "test_acceptance.py"
Cohesion: 0.11
Nodes (12): test_evidence_buffer_confidence_curve(), test_evidence_confounders(), test_evidence_fairness_and_lessons(), test_evidence_impact(), test_evidence_loan_policy(), test_evidence_monitoring_no_breaches(), test_evidence_multiple_testing(), test_evidence_segment_profile() (+4 more)

### Community 2 - "app.py"
Cohesion: 0.14
Nodes (16): pcurve(), wl(), render(), render(), render(), render(), render(), apply_settings() (+8 more)

### Community 3 - "Claude Code guide: what to give it, how to watch it, how to track progress"
Cohesion: 0.22
Nodes (9): 1. What Claude Code needs (all already in this repo), 2. Which IDE: see everything that's happening, 3. The workflow for one task (10–40 minutes), 4. The project slash commands (in `.claude/commands/`), 5. Tracking progress as a team, 6. Prompt library (copy, edit the bits in <>), 7. Things to watch for (and what to say), 8. Should we install the softaworks/agent-toolkit skills? (+1 more)

### Community 4 - "write_plan"
Cohesion: 0.13
Nodes (16): _generate(), plan_facts(), template_plan(), verify_numbers(), verify_wording(), _write(), write_plan(), M12. Differentiators if you're ahead (+8 more)

### Community 5 - "FRONTEND.md: how the React app connects to the logic"
Cohesion: 0.11
Nodes (17): 1. Rules (break one and the numbers on screen stop matching the judges'), 2. Run it, 3. App state: three things drive everything, 4. Endpoints, 5. Types (copy into `web/src/types.ts`), 6. Screen by screen: which call, which field, 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4), 9. Paste-ready Claude Code prompts (Streamlit now; same rules apply to React) (+9 more)

### Community 6 - "Part A. Strategy and setup"
Cohesion: 0.25
Nodes (7): C1. Stats and algorithms cheat sheet, C3. Submission checklist, C4. Demo script, live-twist runbook, Q&A, C5. What can go wrong, and the fallback, Contents, Part C. Reference, Runway build guide: every part, step by step, with Claude Code

### Community 7 - "test_app_smoke.py"
Cohesion: 0.25
Nodes (9): at(), _click(), _no_errors(), test_controls(), test_custom_twist_card(), test_presets_plan_reset(), test_random_accounts(), test_time_machine_and_demo_account() (+1 more)

### Community 8 - "engine.py"
Cohesion: 0.16
Nodes (13): committed_outflows(), ei_benefit(), explain_difference(), make_plan(), lever(), Profile, Realistic, realistic_runway() (+5 more)

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
Nodes (75): @fontsource-variable/plus-jakarta-sans, react, react-dom, recharts, @tanstack/react-query, dependencies, @fontsource-variable/plus-jakarta-sans@^5.1.0, react@^19.1.0 (+67 more)

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
Cohesion: 0.08
Nodes (32): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, @types/react, @types/react-dom, typescript (+24 more)

### Community 24 - "multiple_testing"
Cohesion: 0.19
Nodes (4): multiple_testing(), _p_auc(), _p_ci(), _watchlist_hits()

### Community 25 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 26 - "Data audit"
Cohesion: 0.40
Nodes (4): 1. Files, 2. Integrity checks, 3. Quirks, and what we do about each, Data audit

### Community 28 - "api.py"
Cohesion: 0.09
Nodes (15): customer_facts(), brief(), clean(), ctx(), _facts(), message(), plan(), PlanReq (+7 more)

### Community 30 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 31 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+10 more)

### Community 33 - "CTO review: is Runway a winner? (Sat Nov 7, evening)"
Cohesion: 0.20
Nodes (9): CTO review: is Runway a winner? (Sat Nov 7, evening), Datathon services: use / skip, Is the maths "quant level"? Direct answers, Next 6 hours (in order), Pitch (60 seconds, in this order), React pivot: decision, Round 4 (diagnosis → action; the loan nobody counted), Verdict (+1 more)

### Community 35 - "test_api.py"
Cohesion: 0.10
Nodes (5): test_answer_key_20111(), test_book_sentence_uses_one_population(), test_brief_and_message_offline_templates_verify(), test_future_loans_hidden_in_time_machine(), test_time_machine_pitch_moment()

### Community 36 - "Tasks: who builds what"
Cohesion: 0.25
Nodes (8): Definition of done for any task, First 30 minutes (everyone), P1: Sukhman (engine and data lead), P2: Frontend A (Watchlist, Know, look and feel), P4: Evidence page + submission (optional 4th person), Tasks: who builds what, Timeline, Who owns which files

### Community 37 - "CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)"
Cohesion: 0.20
Nodes (8): CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track), Commands, graphify, Start here, Two Claude Code sessions on this repo, Where things live, Working style, test_ai_engine_contract()

### Community 38 - "Runway: product and engineering spec (single source of truth)"
Cohesion: 0.29
Nodes (6): 2. Data, 4. What is proven (evidence.json), 5. Product: screens and API, 7. Governance and engineering, 8. Status (Nov 8), Runway: product and engineering spec (single source of truth)

### Community 39 - "Runway: a liquidity early warning for Tangerine (Devpost write-up draft)"
Cohesion: 0.22
Nodes (8): How a bank would roll it out, Runway: a liquidity early warning for Tangerine (Devpost write-up draft), Sources, The question, What we built, What we don't claim (said first), What we found, Who it's for

### Community 40 - "Deploy Runway to Google Cloud Run (public demo link for Devpost)"
Cohesion: 0.33
Nodes (5): Check it, Deploy (from the repo root, with the CSVs in ./data), Deploy Runway to Google Cloud Run (public demo link for Devpost), Once (about 10 minutes), Take it down after judging

### Community 41 - "parse_twist"
Cohesion: 0.17
Nodes (10): _num(), _numbers(), parse_twist_offline(), walk(), P3: Frontend B + AI (Shock, Plan, Gemini), test_card(), test_eval_harness_runs_offline_and_reports_held_out(), test_no_shock_card_stays_empty() (+2 more)

### Community 42 - "Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)"
Cohesion: 0.25
Nodes (7): Decisions, Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM), Must fix (judges will see these), New files from this review, Pitch order, Should fix, Verified (don't re-check)

### Community 43 - "M3. Realistic runway"
Cohesion: 0.20
Nodes (9): M3. Realistic runway, test_ei_cap_constant(), test_ei_cap_finding(), test_employment_share_assumption(), test_median_mislabel(), test_realistic_ei_ends_after_6_months(), test_realistic_examples(), test_verdict() (+1 more)

### Community 44 - "M4. Liquidity Trough Ratio, watchlist, Time Machine"
Cohesion: 0.29
Nodes (8): M4. Liquidity Trough Ratio, watchlist, Time Machine, reasons(), _ltr_backtest(), test_example_93172(), test_trough_backtest_2025(), test_trough_needs_12_months(), test_trough_other_years(), test_watchlist_time_machine()

### Community 45 - "audit_data.py"
Cohesion: 0.15
Nodes (3): main(), out(), pytest_collection_modifyitems()

### Community 47 - "pytest"
Cohesion: 0.18
Nodes (11): M9. Evidence engine, test_calibration_is_monotone_and_bounded(), test_conservative_buffer_and_haircut(), test_cushion_93172_time_machine(), test_dip_days(), test_evidence_loans_and_holes(), test_evidence_out_of_time(), test_extended_loan_payment_uses_data_fields_only() (+3 more)

### Community 48 - "main"
Cohesion: 0.13
Nodes (6): lessons(), loan_evidence(), loan_policy(), main(), multiple_testing_extended(), new_accounts()

### Community 49 - "with"
Cohesion: 0.10
Nodes (23): run, jobs, python, web, name, on, pull_request, push (+15 more)

### Community 50 - "realistic_runway_vec"
Cohesion: 0.24
Nodes (5): 1. Problem, users, use case, book_tiers(), loan_adjust_vec(), new_account_swing(), realistic_runway_vec()

### Community 51 - "numpy"
Cohesion: 0.17
Nodes (6): realistic_vec(), buffer_confidence(), impact(), sim_calibration(), _sim_cohort(), survival()

### Community 52 - "data.py"
Cohesion: 0.36
Nodes (8): build_context(), Context, ai_backend(), dip_days(), repeat_table(), standing_orders(), survival_table(), trough_table()

### Community 53 - "M2. Answer-key engine (the judges' formula)"
Cohesion: 0.29
Nodes (7): M2. Answer-key engine (the judges' formula), test_edge_case_counts(), test_profile_20111(), test_runway_rules(), test_twist_distribution(), test_twists_20111(), test_vectorised_matches_scalar()

### Community 54 - "pandas"
Cohesion: 0.18
Nodes (5): book(), challenger(), diagnoses(), _features(), formula_holes()

### Community 55 - "confounders"
Cohesion: 0.25
Nodes (4): confounders(), fairness(), _ltr_backtest(), segment_profile()

### Community 56 - "Model card: Runway liquidity early warning"
Cohesion: 0.18
Nodes (10): 1. Inventory record (E-23 Appendix 1), 2. Purpose and design (E-23 3.1, 3.3), 3. Data (E-23 3.2), 4. Validation (E-23 3.4), 4b. Fairness, 4c. Scale, 5. Ongoing monitoring (E-23 3.6), 6. Limits and judgement calls (+2 more)

### Community 57 - "monitoring"
Cohesion: 0.25
Nodes (3): monitoring(), _psi(), test_psi_flags_drift_and_not_noise()

### Community 58 - "Judge Q&A: one-line answers, with the number to point at"
Cohesion: 0.22
Nodes (8): Bankers (Scotiabank, RBC, CIBC, Sun Life), Consultants (Accenture, EY, PwC): the pilot plan, Data platforms (Snowflake, Dataiku, Thomson Reuters), Finance terms (if a banker or quant uses them), Judge Q&A: one-line answers, with the number to point at, Professor / methodology, Quant / risk (e.g. XVA, model risk, control backgrounds), The 60-second pitch (Pitch mode, press → five times)

### Community 59 - "test_ai_cards.py"
Cohesion: 0.17
Nodes (7): advisor_brief(), template_brief(), _FakeGemini, test_gemini_brief_rejected_when_number_invented(), test_gemini_path_flags_misread_card(), test_slow_gemini_falls_back_to_rules_fast(), generate_content()

### Community 60 - "eval_ai.py"
Cohesion: 0.48
Nodes (3): correct(), main(), run()

### Community 61 - "overdraft_risk"
Cohesion: 0.19
Nodes (10): 5.5 Signal vs noise: Kalman filter (`kalman_level`, `net_flow_filter`), Fixed today (engine and AI lanes, all tests green: 62 fast, 5 slow, 6 UI), Round 2: answering the "finding ≠ product" critique, Still open (ranked), What I found (strict), 8. Not in the API yet (ask P1, don't build in React), calibrate_break(), kalman_level() (+2 more)

### Community 63 - "M10. AI layer"
Cohesion: 0.29
Nodes (5): backend(), M10. AI layer, test_number_verifier(), test_sql_trough_matches_engine(), test_twist_reader_offline()

### Community 64 - "runway"
Cohesion: 0.14
Nodes (14): Hard rules, 2. What happens when someone clicks, 5.1 The judges' runway (`profile`, `runway`), 5.2 Our realistic runway (`realistic_profile`, `realistic_runway`), 5.4 Credit view and bank view (`loan_risk`, `portfolio_curve`), 5.6 "Do they make it?": Monte Carlo simulation (`simulate`), 5.8 The plan (`make_plan`), 5.9 AI (`ai.py`) (+6 more)

### Community 65 - "load_all"
Cohesion: 0.23
Nodes (10): accounts(), book(), _book(), customer(), evidence(), health(), _tiers(), watchlist() (+2 more)

### Community 67 - "Log (newest last; one line per merged change, both lanes)"
Cohesion: 0.12
Nodes (16): 5.7 Smallest cuts: optimiser (`optimize_cuts`), Log (newest last; one line per merged change, both lanes), 3. Definitions (engine.py), _acct(), cushion(), diagnose(), diagnosis_signals(), loan_check() (+8 more)

### Community 68 - "Twist-card reader evaluation"
Cohesion: 0.50
Nodes (3): Misses, Note (Nov 8): field definitions clarified after the Gemini run, Twist-card reader evaluation

### Community 71 - "6. Function contract (don't rename without telling everyone)"
Cohesion: 0.15
Nodes (16): init(), 5.3 The warning score: Liquidity Trough Ratio (`ltr_table`, `liquidity_trough`, `watchlist`), 6. Function contract (don't rename without telling everyone), C2. Integration contract, all_profiles(), liquidity_trough(), load(), load_dip_days() (+8 more)

### Community 74 - "parse_twist"
Cohesion: 0.27
Nodes (7): describe_scenario(), parse_twist(), parse_twist_checked(), _sanitize(), 8b. New backend pieces (round 3) the UI should use, 6. AI (ai.py), test_chips_and_checked_parse_offline()

### Community 77 - "Part A. Strategy and setup"
Cohesion: 0.33
Nodes (6): A1. How we win against ~200 people, A2. What we're building (architecture), A3. Tech stack and why, A4. How to work with Claude Code, A5. Build order and time budget, Part A. Strategy and setup

### Community 78 - "M4b. Credit view and bank view"
Cohesion: 0.40
Nodes (5): M4b. Credit view and bank view, test_loan_risk_93172(), test_overdraft_splits_loan_book(), test_portfolio_curve(), test_realistic_vector_matches_scalar()

## Knowledge Gaps
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `C2. Integration contract` connect `6. Function contract (don't rename without telling everyone)` to `runway`, `Log (newest last; one line per merged change, both lanes)`, `write_plan`, `Part A. Strategy and setup`, `engine.py`, `parse_twist`, `main`, `realistic_runway_vec`, `numpy`, `overdraft_risk`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `Log (newest last; one line per merged change, both lanes)` (e.g. with `describe_scenario()` and `parse_twist_checked()`) actually correct?**
  _`Log (newest last; one line per merged change, both lanes)` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_acceptance.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1076923076923077 - nodes in this community are weakly interconnected._
- **Why does `Log (newest last; one line per merged change, both lanes)` connect `Log (newest last; one line per merged change, both lanes)` to `runway`, `test_acceptance.py`, `test_api.py`, `write_plan`, `6. Function contract (don't rename without telling everyone)`, `engine.py`, `Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)`, `parse_twist`, `pytest`, `main`, `realistic_runway_vec`, `numpy`, `pandas`, `confounders`, `monitoring`, `overdraft_risk`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `6. Function contract (don't rename without telling everyone)` (e.g. with `init()` and `all_profiles()`) actually correct?**
  _`6. Function contract (don't rename without telling everyone)` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1417004048582996 - nodes in this community are weakly interconnected._
- **Why does `runway()` connect `runway` to `Claude Code guide: what to give it, how to watch it, how to track progress`, `Log (newest last; one line per merged change, both lanes)`, `FRONTEND.md: how the React app connects to the logic`, `6. Function contract (don't rename without telling everyone)`, `engine.py`, `Contributing: getting started, Git, and Claude Code`, `M2. Answer-key engine (the judges' formula)`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._