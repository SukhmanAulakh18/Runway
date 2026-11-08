# Graph Report - tangerine-resilience-engine-94bfb1  (2026-11-07)

## Corpus Check
- 70 files · ~66,153 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 5, .ini 1, .css 1)

## Summary
- 754 nodes · 1566 edges · 44 communities (30 shown, 14 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 191 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2a254283`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- engine.py
- test_acceptance.py
- pandas
- Claude Code guide: what to give it, how to watch it, how to track progress
- ai.py
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
- audit_data.py
- What we found, in plain words
- Runway 🍊
- package.json
- evidence.py
- Ponytail
- Data audit
- test_api.py
- compilerOptions
- compilerOptions
- tsconfig.json
- CTO review: is Runway a winner? (Sat Nov 7, evening)
- Runway React frontend: plan and rules
- Tasks: who builds what
- CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)
- Runway: a liquidity early warning for Tangerine (Devpost write-up draft)
- Deploy Runway to Google Cloud Run (public demo link for Devpost)

## God Nodes (most connected - your core abstractions)
1. `6. Function contract (don't rename without telling everyone)` - 32 edges
2. `C2. Integration contract` - 29 edges
3. `Scenario` - 24 edges
4. `compilerOptions` - 19 edges
5. `main()` - 17 edges
6. `compilerOptions` - 17 edges
7. `money()` - 16 edges
8. `Log (newest last; one line per merged change, both lanes)` - 16 edges
9. `load_all()` - 15 edges
10. `Stress()` - 15 edges

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

## Communities (44 total, 14 thin omitted)

### Community 0 - "engine.py"
Cohesion: 0.06
Nodes (62): init(), Hard rules, 2. What happens when someone clicks, 5.1 The judges' runway (`profile`, `runway`), 5.2 Our realistic runway (`realistic_profile`, `realistic_runway`), 5.3 The warning score: Liquidity Trough Ratio (`ltr_table`, `liquidity_trough`, `watchlist`), 5.4 Credit view and bank view (`loan_risk`, `portfolio_curve`), 5.5 Signal vs noise: Kalman filter (`kalman_level`, `net_flow_filter`) (+54 more)

### Community 1 - "test_acceptance.py"
Cohesion: 0.05
Nodes (60): backend(), M0. Project setup, M10. AI layer, M1. Data loading and audit, M2. Answer-key engine (the judges' formula), M3. Realistic runway, M4. Liquidity Trough Ratio, watchlist, Time Machine, M4b. Credit view and bank view (+52 more)

### Community 2 - "pandas"
Cohesion: 0.06
Nodes (42): accounts(), brief(), clean(), ctx(), customer(), evidence(), _facts(), health() (+34 more)

### Community 3 - "Claude Code guide: what to give it, how to watch it, how to track progress"
Cohesion: 0.22
Nodes (9): 1. What Claude Code needs (all already in this repo), 2. Which IDE: see everything that's happening, 3. The workflow for one task (10–40 minutes), 4. The project slash commands (in `.claude/commands/`), 5. Tracking progress as a team, 6. Prompt library (copy, edit the bits in <>), 7. Things to watch for (and what to say), 8. Should we install the softaworks/agent-toolkit skills? (+1 more)

### Community 4 - "ai.py"
Cohesion: 0.05
Nodes (44): advisor_brief(), customer_facts(), customer_message(), describe_scenario(), _generate(), _load_env(), _num(), _numbers() (+36 more)

### Community 5 - "FRONTEND.md: how the React app connects to the logic"
Cohesion: 0.12
Nodes (16): 2. Run it, 3. App state: three things drive everything, 4. Endpoints, 5. Types (copy into `web/src/types.ts`), 6. Screen by screen: which call, which field, 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4), 9. Paste-ready Claude Code prompts (Streamlit now; same rules apply to React), Bank view: `POST /api/portfolio {scenario, asof}` (+8 more)

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
Cohesion: 0.08
Nodes (65): @fontsource-variable/plus-jakarta-sans, react, react-dom, recharts, @tanstack/react-query, dependencies, @fontsource-variable/plus-jakarta-sans@^5.1.0, react@^19.1.0 (+57 more)

### Community 21 - "What we found, in plain words"
Cohesion: 0.25
Nodes (7): 1. Healthy on average, close to zero at the low point (the headline), 2. An overdraft is the line between repaid and defaulted loans, 3. Where the standard runway formula misleads, 4. A trap we caught, Limits (we say these first), The demo customer: account 93172, What we found, in plain words

### Community 22 - "Runway 🍊"
Cohesion: 0.25
Nodes (8): Commands, Data and sources, Event rules that affect the code, Quick start (10 minutes), Repo map, Runway 🍊, The four rules, What we're building (plain English)

### Community 23 - "package.json"
Cohesion: 0.08
Nodes (32): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, @types/react, @types/react-dom, typescript (+24 more)

### Community 24 - "evidence.py"
Cohesion: 0.07
Nodes (19): 1. Rules (break one and the numbers on screen stop matching the judges'), confounders(), _correction_scores(), formula_holes(), impact(), loan_evidence(), _ltr_backtest(), main() (+11 more)

### Community 25 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 26 - "Data audit"
Cohesion: 0.40
Nodes (4): 1. Files, 2. Integrity checks, 3. Quirks, and what we do about each, Data audit

### Community 28 - "test_api.py"
Cohesion: 0.13
Nodes (3): test_answer_key_20111(), test_brief_and_message_offline_templates_verify(), test_time_machine_pitch_moment()

### Community 30 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 31 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+10 more)

### Community 33 - "CTO review: is Runway a winner? (Sat Nov 7, evening)"
Cohesion: 0.25
Nodes (7): CTO review: is Runway a winner? (Sat Nov 7, evening), Datathon services: use / skip, Is the maths "quant level"? Direct answers, Next 6 hours (in order), Pitch (60 seconds, in this order), React pivot: decision, Verdict

### Community 35 - "Runway React frontend: plan and rules"
Cohesion: 0.22
Nodes (8): API (full spec in openapi.json, live docs at /docs), Claude Code prompt for each React engineer (start of session), Hard rules (same as CLAUDE.md, plus three), Run it, Runway React frontend: plan and rules, Screens and the "fancy" that also scores points, Timeline, Who does what

### Community 36 - "Tasks: who builds what"
Cohesion: 0.25
Nodes (8): Definition of done for any task, First 30 minutes (everyone), P1: Sukhman (engine and data lead), P2: Frontend A (Watchlist, Know, look and feel), P4: Evidence page + submission (optional 4th person), Tasks: who builds what, Timeline, Who owns which files

### Community 37 - "CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)"
Cohesion: 0.29
Nodes (6): CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track), Commands, graphify, Start here, Where things live, Working style

### Community 39 - "Runway: a liquidity early warning for Tangerine (Devpost write-up draft)"
Cohesion: 0.25
Nodes (7): Runway: a liquidity early warning for Tangerine (Devpost write-up draft), Sources, The question, What we built, What we don't claim (said first), What we found, Who it's for

### Community 40 - "Deploy Runway to Google Cloud Run (public demo link for Devpost)"
Cohesion: 0.33
Nodes (5): Check it, Deploy (from the repo root, with the CSVs in ./data), Deploy Runway to Google Cloud Run (public demo link for Devpost), Once (about 10 minutes), Take it down after judging

## Knowledge Gaps
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `C2. Integration contract` connect `engine.py` to `evidence.py`, `ai.py`, `Part A. Strategy and setup`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `6. Function contract (don't rename without telling everyone)` (e.g. with `init()` and `all_profiles()`) actually correct?**
  _`6. Function contract (don't rename without telling everyone)` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `engine.py` be split into smaller, more focused modules?**
  _Cohesion score 0.056578947368421055 - nodes in this community are weakly interconnected._
- **Why does `runway()` connect `engine.py` to `test_acceptance.py`, `Claude Code guide: what to give it, how to watch it, how to track progress`, `FRONTEND.md: how the React app connects to the logic`, `Contributing: getting started, Git, and Claude Code`, `evidence.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `C2. Integration contract` (e.g. with `init()` and `parse_twist()`) actually correct?**
  _`C2. Integration contract` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_acceptance.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05242566510172144 - nodes in this community are weakly interconnected._
- **Why does `Scenario` connect `engine.py` to `test_acceptance.py`, `ai.py`, `FRONTEND.md: how the React app connects to the logic`, `Tasks: who builds what`, `Data pipeline: from raw files to every number on screen`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._