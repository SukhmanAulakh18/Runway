# Graph Report - runway  (2026-11-07)

## Corpus Check
- 47 files · ~46,891 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .ini 1)

## Summary
- 439 nodes · 896 edges · 28 communities (19 shown, 9 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 170 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5101994d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- engine.py
- test_acceptance.py
- pandas
- Claude Code guide: what to give it, how to watch it, how to track progress
- Tasks: who builds what
- evidence.py
- Part A. Strategy and setup
- test_app_smoke.py
- audit_data.py
- Data pipeline: from raw files to every number on screen
- Contributing: getting started, Git, and Claude Code
- Architecture: the tech, and how everything works
- Findings log (Tangerine: Resilience Rewired)
- pull_request_template.md
- create_issues.sh
- .claude/CLAUDE.md
- overdraft_risk
- Runway React frontend: plan and rules
- What we found, in plain words
- Runway 🍊
- Ponytail
- Data audit

## God Nodes (most connected - your core abstractions)
1. `6. Function contract (don't rename without telling everyone)` - 32 edges
2. `C2. Integration contract` - 29 edges
3. `Scenario` - 22 edges
4. `Part B. The modules` - 15 edges
5. `portfolio_curve()` - 14 edges
6. `watchlist()` - 14 edges
7. `runway()` - 14 edges
8. `simulate()` - 14 edges
9. `main()` - 14 edges
10. `ltr_table()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Know the customer: `GET /api/customer/{acct}?asof=`` --references--> `what_happened_next()`  [INFERRED]
  docs/FRONTEND.md → engine.py
- `Make a plan: `POST /api/plan/{acct}` then `POST /api/write-plan`` --references--> `runway()`  [INFERRED]
  docs/FRONTEND.md → engine.py
- `Step 7 · Show it (`ui/`)` --references--> `Scenario`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py
- `Who owns which files` --references--> `Scenario`  [INFERRED]
  docs/TASKS.md → engine.py
- `Step 4 · Load (`engine.load()`)` --references--> `load()`  [INFERRED]
  docs/DATA_PIPELINE.md → engine.py

## Import Cycles
- None detected.

## Communities (28 total, 9 thin omitted)

### Community 0 - "engine.py"
Cohesion: 0.09
Nodes (43): Hard rules, 2. What happens when someone clicks, 5.1 The judges' runway (`profile`, `runway`), 5.2 Our realistic runway (`realistic_profile`, `realistic_runway`), 5.3 The warning score: Liquidity Trough Ratio (`ltr_table`, `liquidity_trough`, `watchlist`), 5.4 Credit view and bank view (`loan_risk`, `portfolio_curve`), 5.5 Signal vs noise: Kalman filter (`kalman_level`, `net_flow_filter`), 5.6 "Do they make it?": Monte Carlo simulation (`simulate`) (+35 more)

### Community 1 - "test_acceptance.py"
Cohesion: 0.06
Nodes (53): backend(), M0. Project setup, M10. AI layer, M1. Data loading and audit, M2. Answer-key engine (the judges' formula), M3. Realistic runway, M4. Liquidity Trough Ratio, watchlist, Time Machine, M4b. Credit view and bank view (+45 more)

### Community 2 - "pandas"
Cohesion: 0.09
Nodes (24): init(), template_plan(), write_plan(), build_context(), Context, ai_backend(), load_all(), pcurve() (+16 more)

### Community 3 - "Claude Code guide: what to give it, how to watch it, how to track progress"
Cohesion: 0.22
Nodes (9): 1. What Claude Code needs (all already in this repo), 2. Which IDE: see everything that's happening, 3. The workflow for one task (10–40 minutes), 4. The project slash commands (in `.claude/commands/`), 5. Tracking progress as a team, 6. Prompt library (copy, edit the bits in <>), 7. Things to watch for (and what to say), 8. Should we install the softaworks/agent-toolkit skills? (+1 more)

### Community 4 - "Tasks: who builds what"
Cohesion: 0.07
Nodes (26): _num(), _numbers(), parse_twist_offline(), verify_numbers(), walk(), CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track), Commands, graphify (+18 more)

### Community 5 - "evidence.py"
Cohesion: 0.05
Nodes (29): 1. Rules (break one and the numbers on screen stop matching the judges'), 2. Run it, 3. App state: three things drive everything, 4. Endpoints, 5. Types (copy into `web/src/types.ts`), 6. Screen by screen: which call, which field, 7. Go/no-go checklist (midnight, see REACT_PLAN rule 4), Bank view: `POST /api/portfolio {scenario, asof}` (+21 more)

### Community 6 - "Part A. Strategy and setup"
Cohesion: 0.14
Nodes (13): A1. How we win against ~200 people, A2. What we're building (architecture), A3. Tech stack and why, A4. How to work with Claude Code, A5. Build order and time budget, C1. Stats and algorithms cheat sheet, C3. Submission checklist, C4. Demo script, live-twist runbook, Q&A (+5 more)

### Community 7 - "test_app_smoke.py"
Cohesion: 0.25
Nodes (9): at(), _click(), _no_errors(), test_controls(), test_custom_twist_card(), test_presets_plan_reset(), test_random_accounts(), test_time_machine_and_demo_account() (+1 more)

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

### Community 19 - "overdraft_risk"
Cohesion: 0.09
Nodes (23): parse_twist(), _sanitize(), CTO review: is Runway a winner? (Sat Nov 7, evening), Datathon services: use / skip, Fixed today (engine and AI lanes, all tests green: 62 fast, 5 slow, 6 UI), Is the maths "quant level"? Direct answers, Next 6 hours (in order), Pitch (60 seconds, in this order) (+15 more)

### Community 20 - "Runway React frontend: plan and rules"
Cohesion: 0.22
Nodes (8): API (full spec in openapi.json, live docs at /docs), Claude Code prompt for each React engineer (start of session), Hard rules (same as CLAUDE.md, plus three), Run it, Runway React frontend: plan and rules, Screens and the "fancy" that also scores points, Timeline, Who does what

### Community 21 - "What we found, in plain words"
Cohesion: 0.25
Nodes (7): 1. Healthy on average, close to zero at the low point (the headline), 2. An overdraft is the line between repaid and defaulted loans, 3. Where the standard runway formula misleads, 4. A trap we caught, Limits (we say these first), The demo customer: account 93172, What we found, in plain words

### Community 22 - "Runway 🍊"
Cohesion: 0.25
Nodes (8): Commands, Data and sources, Event rules that affect the code, Quick start (10 minutes), Repo map, Runway 🍊, The four rules, What we're building (plain English)

### Community 25 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 26 - "Data audit"
Cohesion: 0.40
Nodes (4): 1. Files, 2. Integrity checks, 3. Quirks, and what we do about each, Data audit

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `C2. Integration contract` connect `engine.py` to `pandas`, `Tasks: who builds what`, `evidence.py`, `Part A. Strategy and setup`, `overdraft_risk`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `6. Function contract (don't rename without telling everyone)` (e.g. with `init()` and `all_profiles()`) actually correct?**
  _`6. Function contract (don't rename without telling everyone)` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `engine.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08857808857808858 - nodes in this community are weakly interconnected._
- **Why does `runway()` connect `engine.py` to `test_acceptance.py`, `Contributing: getting started, Git, and Claude Code`, `Claude Code guide: what to give it, how to watch it, how to track progress`, `evidence.py`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `C2. Integration contract` (e.g. with `init()` and `parse_twist()`) actually correct?**
  _`C2. Integration contract` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_acceptance.py` be split into smaller, more focused modules?**
  _Cohesion score 0.059907834101382486 - nodes in this community are weakly interconnected._
- **Why does `Scenario` connect `engine.py` to `test_acceptance.py`, `Tasks: who builds what`, `evidence.py`, `Data pipeline: from raw files to every number on screen`, `overdraft_risk`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._