# CLAUDE.md: Runway (Sheridan Datathon 2026, Tangerine track)

Runway is a Streamlit app that, for any bank `account_id`, shows the customer's money picture, applies a shock (job loss with EI, higher bills, a one-off repair) and produces a plan. Its headline finding is the Liquidity Trough Ratio, an early warning for first overdrafts, which in this data also separate repaid from defaulted loans. Read `docs/ARCHITECTURE.md` for how it works and `docs/TASKS.md` for who owns which file.

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
