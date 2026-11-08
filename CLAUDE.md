# CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)

Runway is a React dashboard (`web/`) over a FastAPI layer (`api.py`), with a Streamlit backup (`app.py`), that, for any bank `account_id`, shows the customer's money picture, applies a shock (job loss with EI, higher bills, a one-off repair) and produces a plan. Its headline finding is the Liquidity Trough Ratio, an early warning for first overdrafts, which in this data also separate repaid from defaulted loans. Read `docs/ARCHITECTURE.md` for how it works and `docs/TASKS.md` for who owns which file.

## Start here

Before any task, read `docs/SPEC.md` (the single source of truth: problem, definitions, proven results, screens, status), then `docs/HANDOFF.md` (verified numbers, decisions, open bugs with owners) and `docs/CTO_REVIEW.md` (what's strong, what's wrong, what to do next). The API (`api.py`) has no maths: it calls `ui/context.build_context`, the same function Streamlit uses. `docs/FRONTEND.md` and `docs/REACT_PLAN.md` are the pre-build plan (superseded by SPEC.md and the code).

## Two Claude Code sessions on this repo

Two sessions work here at once. Each stays in its lane, on its own branch, so they never edit the same file.

| Lane | Branch prefix | Owns | Never edits |
|---|---|---|---|
| **Engine** (maths, stats, evidence) | `p1/` | `engine.py`, `evidence.py`, `evidence.json`, `ui/context.py`, `tests/test_acceptance.py` | `ai.py` |
| **AI** (twist reader, plan writer) | `p3/` | `ai.py`, `tests/test_ai_cards.py` | `engine.py`, `evidence.py` |

- **The seam** is `engine.Scenario` (fields the AI may set) and the plan `facts` dict. `tests/test_ai_cards.py::test_ai_engine_contract` fails if either side breaks it. Renaming a Scenario field needs both lanes: write it in `docs/HANDOFF.md` first.
- **Before you start:** `git pull`, read the newest `docs/HANDOFF.md` log lines, run `graphify query "<question>"` instead of re-reading files.
- **When you finish:** run `pytest -q` (and `-m slow` if engine/evidence changed), `graphify update .`, add one line to the log at the bottom of `docs/HANDOFF.md` (date, lane, what changed, any new field), then open a PR.
- **`graphify-out/` merge conflict:** don't hand-merge it. Take either side, then run `graphify update .` and commit the result.
- **`evidence.json`:** only the engine lane rewrites it.

## Hard rules

1. **All maths lives in `engine.py`.** `app.py` and everything in `ui/` only display. A page may build `Scenario` objects and call engine functions, but must never contain a formula. If a page needs a new number, stop and say what engine function is needed.
2. **Stay inside the files the user owns** (see `docs/TASKS.md`). If a change needs another file, explain why and ask first.
3. **The standard (answer-key) runway must match the Tangerine README exactly.** Never change `profile()` or `runway()`; improvements go in the realistic functions.
4. **AI never calculates.** `ai.py` turns text into settings and writes sentences from engine numbers; every number in AI text must pass `verify_numbers()`, otherwise use the template.
5. **Never edit an existing test to make it pass.** Fix the code. If a test seems wrong, stop and explain. Adding new tests is encouraged.
6. **Never commit or create files in `data/`, `.env`, keys or credentials.**
7. **Streamlit state:** change widget values from code only inside callbacks (`on_click`, `on_select`) defined in `ui/state.py`. Cache anything that loops over all 4,500 accounts in `ui/data.py`.
8. **Wording:** "money in" / "money out" (not income/spending, except when quoting the judges' formula); "unlabelled outflows (purpose unknown)"; "no activity after YYYY-MM" (not "closed"); "household bills" (not "rent"). Sentence case. Colours only from `ui/style.py` (ORANGE = ours, SLATE = standard).
9. **Keep it simple:** smallest change that does the task; no new dependencies unless essential (explain why); no new abstractions.

## Where things live

| File | What | Owner |
|---|---|---|
| `engine.py` | all calculations | P1 |
| `evidence.py` → `evidence.json` | backtests and findings | P1 |
| `ai.py` | twist-card reader, plan writer, number checker | P3 |
| `app.py` | sidebar + tabs wiring | P2 (sidebar) / P1 |
| `ui/context.py` | builds one customer's numbers + flags (`c`) | P1 |
| `ui/data.py`, `ui/state.py`, `ui/style.py` | caching, widget state/callbacks, colours/CSS | P1 / P2 |
| `ui/pages/watchlist.py`, `know.py` | Watchlist and Know tabs | P2 |
| `ui/pages/shock.py`, `plan.py` | Shock and Plan tabs | P3 |
| `ui/pages/evidence.py` | Why trust it tab | P4 (or P2) |

Each page exposes `render(c)`, where `c` is the `Context` from `ui/context.py` (fields: `d, EV, accounts, acct, asof, p, r, sc, key_res, real_res, a_rows, lt, LR, sim, age, flags`).

## Commands

Project slash commands: `/task <ID>` (start a task from docs/TASKS.md), `/check` (run tests and explain), `/review` (rule check before a PR).

```bash
python scripts/check_setup.py   # setup doctor
python scripts/audit_data.py    # data checks → docs/DATA_AUDIT.md
pytest -q            # engine tests (must pass before any commit)
pytest -q -m ui      # headless click-through of the app (run if app.py or ui/ changed)
pytest -q -m slow    # statistical evidence checks (engine/evidence changes)
python evidence.py   # rebuild evidence.json
streamlit run app.py
```

## Working style

- Plan first for anything bigger than a few lines; list the files you'll touch.
- After changes: run the relevant tests, then summarise the diff and list every changed file.
- If a spec is unclear, check `docs/ARCHITECTURE.md` and `docs/BUILD_GUIDE.md`, then ask.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
