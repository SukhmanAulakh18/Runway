# Graph Report - tangerine-resilience-engine-94bfb1  (2026-11-07)

## Corpus Check
- 70 files · ~63,354 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 5, .ini 1, .css 1)

## Summary
- 732 nodes · 1515 edges · 59 communities (43 shown, 16 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aa24a6e5`
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
- Runway React frontend: plan and rules
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
- parse_twist_checked
- Tasks: who builds what
- CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)
- ai.py
- main
- _FakeGemini
- verify_numbers
- 6. Screen by screen: which call, which field
- trough_evidence
- _FakeGemini
- test_ai_cards.py
- sim_calibration
- _load_env
- confounders
- test_api.py
- audit_data.py
- app.py
- data.py
- Runway: a liquidity early warning for Tangerine (Devpost write-up draft)
- Deploy Runway to Google Cloud Run (public demo link for Devpost)

## God Nodes (most connected - your core abstractions)
1. `6. Function contract (don't rename without telling everyone)` - 32 edges
2. `C2. Integration contract` - 29 edges
3. `Scenario` - 23 edges
4. `compilerOptions` - 19 edges
5. `compilerOptions` - 17 edges
6. `main()` - 16 edges
7. `Log (newest last; one line per merged change, both lanes)` - 16 edges
8. `Part B. The modules` - 15 edges
9. `portfolio_curve()` - 14 edges
10. `watchlist()` - 14 edges

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

## Communities (59 total, 16 thin omitted)

### Community 0 - "engine.py"
Cohesion: 0.06
Nodes (58): init(), _sanitize(), Hard rules, 2. What happens when someone clicks, 5.1 The judges' runway (`profile`, `runway`), 5.2 Our realistic runway (`realistic_profile`, `realistic_runway`), 5.3 The warning score: Liquidity Trough Ratio (`ltr_table`, `liquidity_trough`, `watchlist`), 5.4 Credit view and bank view (`loan_risk`, `portfolio_curve`) (+50 more)

### Community 1 - "test_acceptance.py"
Cohesion: 0.06
Nodes (58): backend(), M0. Project setup, M10. AI layer, M12. Differentiators if you're ahead, M1. Data loading and audit, M2. Answer-key engine (the judges' formula), M3. Realistic runway, M4. Liquidity Trough Ratio, watchlist, Time Machine (+50 more)

### Community 2 - "pandas"
Cohesion: 0.17
Nodes (13): pcurve(), wl(), render(), render(), render(), render(), render(), open_from_watchlist() (+5 more)

### Community 3 - "Claude Code guide: what to give it, how to watch it, how to track progress"
Cohesion: 0.22
Nodes (9): 1. What Claude Code needs (all already in this repo), 2. Which IDE: see everything that's happening, 3. The workflow for one task (10–40 minutes), 4. The project slash commands (in `.claude/commands/`), 5. Tracking progress as a team, 6. Prompt library (copy, edit the bits in <>), 7. Things to watch for (and what to say), 8. Should we install the softaworks/agent-toolkit skills? (+1 more)

### Community 4 - "write_plan"
Cohesion: 0.25
Nodes (6): _generate(), verify_wording(), _write(), write_plan(), test_gemini_plan_rejected_when_it_says_chance(), test_wording_check_blocks_chance_for_simulation_counts()

### Community 5 - "FRONTEND.md: how the React app connects to the logic"
Cohesion: 0.25
Nodes (7): 2. Run it, 3. App state: three things drive everything, 4. Endpoints, 5. Types (copy into `web/src/types.ts`), 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4), 9. Paste-ready Claude Code prompts (Streamlit now; same rules apply to React), FRONTEND.md: how the React app connects to the logic

### Community 6 - "Part A. Strategy and setup"
Cohesion: 0.14
Nodes (13): A1. How we win against ~200 people, A2. What we're building (architecture), A3. Tech stack and why, A4. How to work with Claude Code, A5. Build order and time budget, C1. Stats and algorithms cheat sheet, C3. Submission checklist, C4. Demo script, live-twist runbook, Q&A (+5 more)

### Community 7 - "test_app_smoke.py"
Cohesion: 0.25
Nodes (9): at(), _click(), _no_errors(), test_controls(), test_custom_twist_card(), test_presets_plan_reset(), test_random_accounts(), test_time_machine_and_demo_account() (+1 more)

### Community 8 - "parse_twist"
Cohesion: 0.25
Nodes (7): Decisions, Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM), Must fix (judges will see these), New files from this review, Pitch order, Should fix, Verified (don't re-check)

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
Cohesion: 0.11
Nodes (52): react, @tanstack/react-query, api, Asof, ASOF_LABEL, Cushion, Customer, Evidence (+44 more)

### Community 20 - "Runway React frontend: plan and rules"
Cohesion: 0.22
Nodes (8): API (full spec in openapi.json, live docs at /docs), Claude Code prompt for each React engineer (start of session), Hard rules (same as CLAUDE.md, plus three), Run it, Runway React frontend: plan and rules, Screens and the "fancy" that also scores points, Timeline, Who does what

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
Cohesion: 0.19
Nodes (4): multiple_testing(), _p_auc(), _p_ci(), _watchlist_hits()

### Community 25 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 26 - "Data audit"
Cohesion: 0.40
Nodes (4): 1. Files, 2. Integrity checks, 3. Quirks, and what we do about each, Data audit

### Community 28 - "api.py"
Cohesion: 0.10
Nodes (18): accounts(), brief(), clean(), ctx(), customer(), evidence(), health(), plan() (+10 more)

### Community 30 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 31 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+10 more)

### Community 33 - "CTO review: is Runway a winner? (Sat Nov 7, evening)"
Cohesion: 0.25
Nodes (7): CTO review: is Runway a winner? (Sat Nov 7, evening), Datathon services: use / skip, Is the maths "quant level"? Direct answers, Next 6 hours (in order), Pitch (60 seconds, in this order), React pivot: decision, Verdict

### Community 35 - "parse_twist_checked"
Cohesion: 0.47
Nodes (4): describe_scenario(), parse_twist_checked(), Round 3 (backend + AI hardening), test_chips_and_checked_parse_offline()

### Community 36 - "Tasks: who builds what"
Cohesion: 0.22
Nodes (9): Definition of done for any task, First 30 minutes (everyone), P1: Sukhman (engine and data lead), P2: Frontend A (Watchlist, Know, look and feel), P3: Frontend B + AI (Shock, Plan, Gemini), P4: Evidence page + submission (optional 4th person), Tasks: who builds what, Timeline (+1 more)

### Community 37 - "CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)"
Cohesion: 0.29
Nodes (6): CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track), Commands, graphify, Start here, Where things live, Working style

### Community 38 - "ai.py"
Cohesion: 0.16
Nodes (5): customer_facts(), customer_message(), template_message(), _facts(), message()

### Community 39 - "main"
Cohesion: 0.18
Nodes (5): formula_holes(), impact(), loan_evidence(), main(), multiple_testing_extended()

### Community 40 - "_FakeGemini"
Cohesion: 0.25
Nodes (5): advisor_brief(), template_brief(), _FakeGemini, test_gemini_brief_rejected_when_number_invented(), test_gemini_path_flags_misread_card()

### Community 41 - "verify_numbers"
Cohesion: 0.24
Nodes (9): _numbers(), plan_facts(), template_plan(), verify_numbers(), walk(), _facts(), test_numbers_reads_french_formats(), test_plan_facts_lead_with_cushion_and_template_verifies() (+1 more)

### Community 42 - "6. Screen by screen: which call, which field"
Cohesion: 0.22
Nodes (9): 6. Screen by screen: which call, which field, Bank view: `POST /api/portfolio {scenario, asof}`, Know the customer: `GET /api/customer/{acct}?asof=`, Make a plan: `POST /api/plan/{acct}` then `POST /api/write-plan`, Shell, Take a shock: `POST /api/twist` then `POST /api/shock/{acct}`, Watchlist: `GET /api/watchlist?asof=&early_only=true&limit=50`, Why trust it: `GET /api/evidence` (+1 more)

### Community 44 - "_FakeGemini"
Cohesion: 0.29
Nodes (4): parse_twist(), 8b. New backend pieces (round 3) the UI should use, test_slow_gemini_falls_back_to_rules_fast(), generate_content()

### Community 45 - "test_ai_cards.py"
Cohesion: 0.21
Nodes (7): _num(), parse_twist_offline(), Two Claude Code sessions on this repo, test_ai_engine_contract(), test_card(), test_no_shock_card_stays_empty(), test_sanitize_llm_shaped_output()

### Community 46 - "sim_calibration"
Cohesion: 0.40
Nodes (3): 1. Rules (break one and the numbers on screen stop matching the judges'), sim_calibration(), _sim_cohort()

### Community 48 - "confounders"
Cohesion: 0.22
Nodes (4): confounders(), _correction_scores(), _ltr_backtest(), self_correction()

### Community 51 - "test_api.py"
Cohesion: 0.15
Nodes (3): test_answer_key_20111(), test_brief_and_message_offline_templates_verify(), test_time_machine_pitch_moment()

### Community 53 - "app.py"
Cohesion: 0.22
Nodes (3): apply_settings(), init_state(), scenario()

### Community 54 - "data.py"
Cohesion: 0.36
Nodes (6): build_context(), Context, ai_backend(), dip_days(), standing_orders(), trough_table()

### Community 55 - "Runway: a liquidity early warning for Tangerine (Devpost write-up draft)"
Cohesion: 0.25
Nodes (7): Runway: a liquidity early warning for Tangerine (Devpost write-up draft), Sources, The question, What we built, What we don't claim (said first), What we found, Who it's for

### Community 56 - "Deploy Runway to Google Cloud Run (public demo link for Devpost)"
Cohesion: 0.33
Nodes (5): Check it, Deploy (from the repo root, with the CSVs in ./data), Deploy Runway to Google Cloud Run (public demo link for Devpost), Once (about 10 minutes), Take it down after judging

## Knowledge Gaps
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `C2. Integration contract` connect `engine.py` to `write_plan`, `Part A. Strategy and setup`, `main`, `verify_numbers`, `_FakeGemini`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `6. Function contract (don't rename without telling everyone)` (e.g. with `init()` and `all_profiles()`) actually correct?**
  _`6. Function contract (don't rename without telling everyone)` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `engine.py` be split into smaller, more focused modules?**
  _Cohesion score 0.062421972534332085 - nodes in this community are weakly interconnected._
- **Why does `runway()` connect `engine.py` to `test_acceptance.py`, `Claude Code guide: what to give it, how to watch it, how to track progress`, `Contributing: getting started, Git, and Claude Code`, `6. Screen by screen: which call, which field`, `sim_calibration`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `C2. Integration contract` (e.g. with `init()` and `parse_twist()`) actually correct?**
  _`C2. Integration contract` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_acceptance.py` be split into smaller, more focused modules?**
  _Cohesion score 0.057342657342657345 - nodes in this community are weakly interconnected._
- **Why does `6. Function contract (don't rename without telling everyone)` connect `engine.py` to `pandas`, `Architecture: the tech, and how everything works`, `app.py`, `data.py`, `api.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._