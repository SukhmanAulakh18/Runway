# Graph Report - runway  (2026-11-08)

## Corpus Check
- 69 files · ~70,482 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .ini 1, .css 1)

## Summary
- 774 nodes · 1612 edges · 54 communities (41 shown, 13 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 199 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cffd41c0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- engine.py
- test_acceptance.py
- pandas
- Claude Code guide: what to give it, how to watch it, how to track progress
- write_plan
- FRONTEND.md: how the React app connects to the logic
- Part A. Strategy and setup
- test_app_smoke.py
- parse_twist
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
- evidence.py
- Ponytail
- Data audit
- api.py
- compilerOptions
- compilerOptions
- tsconfig.json
- CTO review: is Runway a winner? (Sat Nov 7, evening)
- Runway React frontend: plan and rules
- Tasks: who builds what
- CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)
- parse_twist_checked
- Runway: a liquidity early warning for Tangerine (Devpost write-up draft)
- Deploy Runway to Google Cloud Run (public demo link for Devpost)
- parse_twist_offline
- test_ai_cards.py
- M3. Realistic runway
- M4. Liquidity Trough Ratio, watchlist, Time Machine
- parse_twist
- verify_numbers
- pytest
- M10. AI layer
- _load_env
- pytest

## God Nodes (most connected - your core abstractions)
1. `6. Function contract (don't rename without telling everyone)` - 32 edges
2. `C2. Integration contract` - 29 edges
3. `Scenario` - 24 edges
4. `Log (newest last; one line per merged change, both lanes)` - 22 edges
5. `compilerOptions` - 19 edges
6. `main()` - 18 edges
7. `compilerOptions` - 17 edges
8. `money()` - 16 edges
9. `Stress()` - 15 edges
10. `load_all()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Step 7 · Show it (`ui/`)` --references--> `Scenario`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py
- `Who owns which files` --references--> `Scenario`  [INFERRED]
  docs/TASKS.md → engine.py
- `Know the customer: `GET /api/customer/{acct}?asof=`` --references--> `what_happened_next()`  [INFERRED]
  docs/FRONTEND.md → engine.py
- `Step 4 · Load (`engine.load()`)` --references--> `load()`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py
- `Next 6 hours (in order)` --references--> `overdraft_risk()`  [INFERRED]
  docs/CTO_REVIEW.md → engine.py

## Import Cycles
- None detected.

## Communities (54 total, 13 thin omitted)

### Community 0 - "engine.py"
Cohesion: 0.05
Nodes (66): init(), _sanitize(), Hard rules, 2. What happens when someone clicks, 5.1 The judges' runway (`profile`, `runway`), 5.2 Our realistic runway (`realistic_profile`, `realistic_runway`), 5.3 The warning score: Liquidity Trough Ratio (`ltr_table`, `liquidity_trough`, `watchlist`), 5.4 Credit view and bank view (`loan_risk`, `portfolio_curve`) (+58 more)

### Community 1 - "test_acceptance.py"
Cohesion: 0.15
Nodes (9): M2. Answer-key engine (the judges' formula), d(), P(), test_edge_case_counts(), test_profile_20111(), test_runway_rules(), test_twist_distribution(), test_twists_20111() (+1 more)

### Community 2 - "pandas"
Cohesion: 0.07
Nodes (31): advisor_brief(), customer_message(), _generate(), template_brief(), template_message(), _write(), health(), build_context() (+23 more)

### Community 3 - "Claude Code guide: what to give it, how to watch it, how to track progress"
Cohesion: 0.22
Nodes (9): 1. What Claude Code needs (all already in this repo), 2. Which IDE: see everything that's happening, 3. The workflow for one task (10–40 minutes), 4. The project slash commands (in `.claude/commands/`), 5. Tracking progress as a team, 6. Prompt library (copy, edit the bits in <>), 7. Things to watch for (and what to say), 8. Should we install the softaworks/agent-toolkit skills? (+1 more)

### Community 4 - "write_plan"
Cohesion: 0.21
Nodes (8): plan_facts(), template_plan(), verify_wording(), write_plan(), _facts(), test_plan_facts_lead_with_cushion_and_template_verifies(), test_template_plan_always_verifies(), test_wording_check_blocks_chance_for_simulation_counts()

### Community 5 - "FRONTEND.md: how the React app connects to the logic"
Cohesion: 0.11
Nodes (17): 1. Rules (break one and the numbers on screen stop matching the judges'), 2. Run it, 3. App state: three things drive everything, 4. Endpoints, 5. Types (copy into `web/src/types.ts`), 6. Screen by screen: which call, which field, 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4), 9. Paste-ready Claude Code prompts (Streamlit now; same rules apply to React) (+9 more)

### Community 6 - "Part A. Strategy and setup"
Cohesion: 0.14
Nodes (13): A1. How we win against ~200 people, A2. What we're building (architecture), A3. Tech stack and why, A4. How to work with Claude Code, A5. Build order and time budget, C1. Stats and algorithms cheat sheet, C3. Submission checklist, C4. Demo script, live-twist runbook, Q&A (+5 more)

### Community 7 - "test_app_smoke.py"
Cohesion: 0.25
Nodes (9): at(), _click(), _no_errors(), test_controls(), test_custom_twist_card(), test_presets_plan_reset(), test_random_accounts(), test_time_machine_and_demo_account() (+1 more)

### Community 8 - "parse_twist"
Cohesion: 0.29
Nodes (6): Decisions, Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM), Must fix (judges will see these), New files from this review, Pitch order, Verified (don't re-check)

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
Cohesion: 0.10
Nodes (59): react, @tanstack/react-query, api, Asof, ASOF_LABEL, Cushion, Customer, Diagnosis (+51 more)

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

### Community 24 - "evidence.py"
Cohesion: 0.06
Nodes (22): confounders(), _correction_scores(), diagnoses(), formula_holes(), impact(), loan_evidence(), _ltr_backtest(), main() (+14 more)

### Community 25 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 26 - "Data audit"
Cohesion: 0.40
Nodes (4): 1. Files, 2. Integrity checks, 3. Quirks, and what we do about each, Data audit

### Community 28 - "api.py"
Cohesion: 0.06
Nodes (22): customer_facts(), accounts(), brief(), clean(), ctx(), customer(), evidence(), _facts() (+14 more)

### Community 30 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 31 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+10 more)

### Community 33 - "CTO review: is Runway a winner? (Sat Nov 7, evening)"
Cohesion: 0.20
Nodes (9): CTO review: is Runway a winner? (Sat Nov 7, evening), Datathon services: use / skip, Is the maths "quant level"? Direct answers, Next 6 hours (in order), Pitch (60 seconds, in this order), React pivot: decision, Round 4 (diagnosis → action; the loan nobody counted), Verdict (+1 more)

### Community 35 - "Runway React frontend: plan and rules"
Cohesion: 0.22
Nodes (8): API (full spec in openapi.json, live docs at /docs), Claude Code prompt for each React engineer (start of session), Hard rules (same as CLAUDE.md, plus three), Run it, Runway React frontend: plan and rules, Screens and the "fancy" that also scores points, Timeline, Who does what

### Community 36 - "Tasks: who builds what"
Cohesion: 0.25
Nodes (8): Definition of done for any task, First 30 minutes (everyone), P1: Sukhman (engine and data lead), P2: Frontend A (Watchlist, Know, look and feel), P4: Evidence page + submission (optional 4th person), Tasks: who builds what, Timeline, Who owns which files

### Community 37 - "CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)"
Cohesion: 0.29
Nodes (6): CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track), Commands, graphify, Start here, Where things live, Working style

### Community 38 - "parse_twist_checked"
Cohesion: 0.47
Nodes (4): describe_scenario(), parse_twist_checked(), Round 3 (backend + AI hardening), test_chips_and_checked_parse_offline()

### Community 39 - "Runway: a liquidity early warning for Tangerine (Devpost write-up draft)"
Cohesion: 0.25
Nodes (7): Runway: a liquidity early warning for Tangerine (Devpost write-up draft), Sources, The question, What we built, What we don't claim (said first), What we found, Who it's for

### Community 40 - "Deploy Runway to Google Cloud Run (public demo link for Devpost)"
Cohesion: 0.33
Nodes (5): Check it, Deploy (from the repo root, with the CSVs in ./data), Deploy Runway to Google Cloud Run (public demo link for Devpost), Once (about 10 minutes), Take it down after judging

### Community 41 - "parse_twist_offline"
Cohesion: 0.22
Nodes (7): parse_twist_offline(), Two Claude Code sessions on this repo, P3: Frontend B + AI (Shock, Plan, Gemini), test_ai_engine_contract(), test_card(), test_no_shock_card_stays_empty(), test_sanitize_llm_shaped_output()

### Community 42 - "test_ai_cards.py"
Cohesion: 0.31
Nodes (4): _FakeGemini, test_gemini_brief_rejected_when_number_invented(), test_gemini_path_flags_misread_card(), test_gemini_plan_rejected_when_it_says_chance()

### Community 43 - "M3. Realistic runway"
Cohesion: 0.20
Nodes (9): M3. Realistic runway, test_ei_cap_constant(), test_ei_cap_finding(), test_employment_share_assumption(), test_median_mislabel(), test_realistic_ei_ends_after_6_months(), test_realistic_examples(), test_verdict() (+1 more)

### Community 44 - "M4. Liquidity Trough Ratio, watchlist, Time Machine"
Cohesion: 0.25
Nodes (8): M4. Liquidity Trough Ratio, watchlist, Time Machine, reasons(), _ltr_backtest(), test_example_93172(), test_trough_backtest_2025(), test_trough_needs_12_months(), test_trough_other_years(), test_watchlist_time_machine()

### Community 45 - "parse_twist"
Cohesion: 0.25
Nodes (5): parse_twist(), 8b. New backend pieces (round 3) the UI should use, Should fix, test_slow_gemini_falls_back_to_rules_fast(), generate_content()

### Community 46 - "verify_numbers"
Cohesion: 0.33
Nodes (6): _num(), _numbers(), verify_numbers(), walk(), M12. Differentiators if you're ahead, test_numbers_reads_french_formats()

### Community 47 - "pytest"
Cohesion: 0.20
Nodes (10): M4b. Credit view and bank view, test_calibration_is_monotone_and_bounded(), test_cushion_93172_time_machine(), test_dip_days(), test_extended_loan_payment_uses_data_fields_only(), test_loan_risk_93172(), test_new_loan_payment_counts_without_lookahead(), test_overdraft_splits_loan_book() (+2 more)

### Community 48 - "M10. AI layer"
Cohesion: 0.50
Nodes (4): backend(), M10. AI layer, test_number_verifier(), test_twist_reader_offline()

### Community 52 - "pytest"
Cohesion: 0.22
Nodes (9): M9. Evidence engine, test_evidence_confounders(), test_evidence_impact(), test_evidence_loans_and_holes(), test_evidence_multiple_testing(), test_evidence_out_of_time(), test_evidence_segment_profile(), test_evidence_self_correction_and_extended_bh() (+1 more)

## Knowledge Gaps
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `C2. Integration contract` connect `engine.py` to `write_plan`, `Part A. Strategy and setup`, `parse_twist`, `verify_numbers`, `evidence.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `6. Function contract (don't rename without telling everyone)` (e.g. with `init()` and `all_profiles()`) actually correct?**
  _`6. Function contract (don't rename without telling everyone)` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `engine.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05120883304778222 - nodes in this community are weakly interconnected._
- **Why does `runway()` connect `engine.py` to `test_acceptance.py`, `Contributing: getting started, Git, and Claude Code`, `Claude Code guide: what to give it, how to watch it, how to track progress`, `FRONTEND.md: how the React app connects to the logic`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `C2. Integration contract` (e.g. with `init()` and `parse_twist()`) actually correct?**
  _`C2. Integration contract` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `pandas` be split into smaller, more focused modules?**
  _Cohesion score 0.07433489827856025 - nodes in this community are weakly interconnected._
- **Why does `Scenario` connect `engine.py` to `Tasks: who builds what`, `FRONTEND.md: how the React app connects to the logic`, `parse_twist_offline`, `Data pipeline: from raw files to every number on screen`, `M3. Realistic runway`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._