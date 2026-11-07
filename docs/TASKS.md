# Tasks: who builds what

The base is already working: all tabs, the engine, the tests. Our job now is to make it **clearer, more impressive and bulletproof** for the live demo. Each person owns specific files, so nobody edits the same file at the same time.

**Starting a task in Claude Code:** type `/task <ID>` (e.g. `/task F1`). It reads the rules and the prompt below, proposes a plan, and waits for your "go". Use `/check` to test and `/review` before your PR.

## Who owns which files

| Person | Role | Owns these files | Never edits |
|---|---|---|---|
| **P1: Sukhman** | Engine and data lead, repo owner, reviewer | `engine.py`, `evidence.py`, `ui/context.py`, `tests/test_acceptance.py` | (reviews everything) |
| **P2: Frontend A** | Watchlist, Know page, look and feel, sidebar | `ui/pages/watchlist.py`, `ui/pages/know.py`, `ui/style.py`, `app.py` (sidebar only) | `engine.py` |
| **P3: Frontend B + AI** | Shock and Plan pages, Gemini | `ui/pages/shock.py`, `ui/pages/plan.py`, `ai.py`, `tests/test_ai_cards.py` (new) | `engine.py` |
| **P4: Evidence + submission** (optional) | Why-trust-it page, Devpost, write-up, video | `ui/pages/evidence.py`, `README.md`, `docs/` | `engine.py` |

**Only 3 of you?** P2 also takes `ui/pages/evidence.py`; P3 also takes the Devpost tasks (D1, D3).

**Need a new number?** Pages never compute money. Message P1 with "engine: I need X for page Y". P1 adds the function and a test, then you call it. Building a different `Scenario` and passing it to existing engine functions is fine; that's not computing money.

---

## First 30 minutes (everyone)

1. Follow [CONTRIBUTING.md](CONTRIBUTING.md) up to "Run it". Get `pytest -q`, `pytest -q -m ui` and `streamlit run app.py` working.
2. Click through every tab on 3 accounts: **93172** (demo), **20176** (pensioner), **56072** (16-year-old owner).
3. Write 3 things that confuse you in the team chat. Fresh eyes are valuable; you see what a judge will see.

---

## P1: Sukhman (engine and data lead)

| # | Task | Done when | Priority | By |
|---|---|---|---|---|
| E1 | Create the GitHub repo, push this base, invite everyone, set up the `main` branch rules (see CONTRIBUTING) | Everyone can clone and push a branch | P0 | Now |
| E2 | Hand-check the judges' formula on 5 accounts against the README (calculator or spreadsheet) | Your numbers match the app to 1 decimal | P0 | Sat 8 PM |
| E3 | Benjamini–Hochberg correction across the hypotheses in `docs/findings_log.md`, added to `evidence.json` as `multiple_testing` | One sentence: "we tested N ideas; the trough survives correction" | P1 | Sat 11 PM |
| E4 | Confounder check: does the trough still predict after controlling for balance size and account age? Added to `evidence.json` as `confounders` | Odds ratio with a 95% CI, reported honestly | P1 | Sun 1 AM |
| E5 | Answer engine requests from P2/P3/P4 within 30 minutes (new function + test) | No one is blocked | Ongoing | |
| E6 | Review and merge PRs; run `pytest -q && pytest -q -m ui` on `main` after each merge | `main` always works | Ongoing | |
| E7 | Rehearse the live twist on 10 accounts, including the tricky ones | Each explained in one sentence | P0 | Sun 9 AM |

**Claude Code prompt for E3:**
```
Read CLAUDE.md and docs/BUILD_GUIDE.md section M9 ("New tasks" A). Add a multiple_testing section to
evidence.py: list the hypotheses from docs/findings_log.md, compute a p-value for each (bootstrap p-value for
AUC differences, Fisher exact for risk ratios), apply Benjamini-Hochberg at q=0.10 with
statsmodels.stats.multitest.multipletests, and write the table to evidence.json. Add a slow test. Run
pytest -q and pytest -q -m slow.
```

**Claude Code prompt for E4:**
```
Read CLAUDE.md and docs/BUILD_GUIDE.md section M9 ("New tasks" B). Add a confounders section to
evidence.py: statsmodels Logit of first overdraft in 2025 (accounts never negative before, complete
2024+2025) on the bottom-10% trough flag, log(avg balance), months of history and district
unemployment_rate_2023. Report the flag's odds ratio and 95% CI in evidence.json, whatever it shows.
Add a slow test that checks the section exists. Run pytest -q -m slow.
```

---

## P2: Frontend A (Watchlist, Know, look and feel)

| # | Task | Done when | Priority | By |
|---|---|---|---|---|
| F1 | **Demo mode button** in the sidebar: one click sets the Time Machine to Dec 2024 and opens account 93172 | One click lands on the pitch moment | P0 | Sat 10 PM |
| F2 | **Customer summary sentence** at the top of Know: "Brings in about $X a month, sends out $Y, has $Z saved. Standard runway N; realistic M." | Readable in 5 seconds | P0 | Sat 11 PM |
| F3 | **Watchlist filters:** a multiselect to filter by reason (e.g. only "Balance dips close to zero"), a count of matching customers, and the current account highlighted | Filter works with the Time Machine on | P1 | Sun 1 AM |
| F4 | **Chart titles that say the takeaway** on Know ("Balance dipped to $238 in Sep 2024" rather than "Balance over time") | Every chart title is a sentence | P1 | Sun 1 AM |
| F5 | **Style pass:** consistent colours (orange = ours, grey = standard), spacing, number formats ($ and commas everywhere), works on a 13-inch laptop | Looks clean at 1280px wide | P1 | Sun 2 AM |
| F6 | **Fallback screenshots** of every tab for 93172 and one random account, in a folder outside the repo | Folder exists | P0 | Sun 9 AM |

**Claude Code prompt for F1:**
```
Read CLAUDE.md and docs/ARCHITECTURE.md. In app.py's sidebar only, add a "Demo mode" button. Use an
on_click callback (define it in ui/state.py) that sets st.session_state.asof_label = "Dec 2024" and
st.session_state.acct = 93172. Callbacks must set state before widgets draw. Don't touch engine.py.
Run pytest -q -m ui, then add a smoke test that clicks Demo mode and checks the Time Machine reveal text
appears.
```

**Claude Code prompt for F2:**
```
Read CLAUDE.md. In ui/pages/know.py, add a one-sentence customer summary at the top of the tab, built
only from values already in the context c (c.p, c.r, c.key_res, c.real_res; no new calculations). Use
"money in" / "money out" wording from CLAUDE.md, $ with commas, and runway labels as given. Run
pytest -q -m ui.
```

**Claude Code prompt for F3:**
```
Read CLAUDE.md. In ui/pages/watchlist.py, add a st.multiselect "Show only" over the distinct reason codes
in the watchlist's reasons column (split on "; "), filter the table to rows containing any selected
reason, show "N customers match", and highlight the row whose account_id equals c.acct. Keep the row-click
callback working. Run pytest -q -m ui.
```

**Claude Code prompt for F5:**
```
Read CLAUDE.md and ui/style.py. Do a consistency pass on ui/pages/watchlist.py and ui/pages/know.py:
colours only from ui/style.py (ORANGE = ours, SLATE = standard), all money formatted as $ with commas,
sentence-case labels, chart heights consistent, no horizontal scrolling at 1280px. No logic changes.
Run pytest -q -m ui and show me a summary of what changed.
```

---

## P3: Frontend B + AI (Shock, Plan, Gemini)

| # | Task | Done when | Priority | By |
|---|---|---|---|---|
| S1 | **Turn on Gemini via Vertex AI** with the event's Google Cloud credits (README "Optional AI") on the demo laptop | Sidebar says "Gemini on Vertex AI"; "Read card" shows "Understood (AI)" | P0 | Sat 10 PM |
| S2 | **Twist-card stress test:** write 20 unusual cards (mixed shocks, odd wording, typos), put them in `tests/test_ai_cards.py`, and fix `parse_twist_offline` in `ai.py` until they pass | 20 cards pass offline | P0 | Sat 11 PM |
| S3 | **"Judge check" expander** on the Shock tab showing the formula's raw numbers (I, S, B, H, money in after shock, money out after shock, gap, runway) from `c.key_res` and `c.p` | A judge can check our answer in 5 seconds | P0 | Sun 12 AM |
| S4 | **Scenario comparison** on the Plan tab: three columns, A (no action), B (optimised cuts), C (loan deferral, if they have a loan). Each shows realistic runway and chance of making 6 months, built by passing different `Scenario`s to engine functions | Three columns render for 93172 and 20134 | P1 | Sun 2 AM |
| S5 | **Download the plan** button on the Plan tab: the customer's plan and key numbers as a `.md` file | The file downloads and reads well | P2 | Sun 2 AM |

**Claude Code prompt for S2:**
```
Read CLAUDE.md and ai.py. Create tests/test_ai_cards.py with 20 parametrised twist cards and the settings
each should produce (use the keys in ai.SCENARIO_FIELDS). Include: job loss with different EI % and
months, "laid off but finds a new job in month 4", pay cuts, rent up $X a month, bills up N%, one-off
repairs in $ and in months of spending, combinations, and two cards with typos. Run them against
ai.parse_twist_offline, then fix the regexes in ai.py until all pass without breaking
tests/test_acceptance.py. Show which cards needed fixes.
```

**Claude Code prompt for S3:**
```
Read CLAUDE.md. In ui/pages/shock.py, add an expander "Judge check: the standard formula's numbers" under
the two runway cards. Show I, S, B, H from c.p, and income_after, spending_after, one_off, buffer_left,
monthly_gap and runway from c.key_res, each to 1 decimal, plus one line showing the formula with the
numbers substituted. Display only; no calculations beyond formatting. Run pytest -q -m ui.
```

**Claude Code prompt for S4:**
```
Read CLAUDE.md and docs/ARCHITECTURE.md section 6. In ui/pages/plan.py, add a "Compare options" section
with three st.columns: A = current scenario c.sc; B = c.sc with spending_increase reduced by the
optimiser's average monthly cut (from E.optimize_cuts); C = c.sc with spending_increase reduced by the
loan payment (only if c.LR exists). For each, call E.realistic_runway(c.r, scenario) and
E.simulate(c.acct, c.d, scenario) and show the runway label and chance of making 6 months. Build Scenario
objects with dataclasses.replace; do not write any formula. Run pytest -q -m ui.
```

**Claude Code prompt for S5:**
```
Read CLAUDE.md. In ui/pages/plan.py, add st.download_button "Download this plan" that saves a Markdown
file with the customer id, the shock in plain words (from the parsed chips or sliders), both runways,
the next milestone, the top backup action, and the verified plan text if written. Values come only from
what the page already shows. Run pytest -q -m ui.
```

---

## P4: Evidence page + submission (optional 4th person)

| # | Task | Done when | Priority | By |
|---|---|---|---|---|
| D1 | **Devpost draft with the Tangerine track selected, all members added** | Draft saved | **P0 (hard deadline)** | **Sat 8 PM** |
| D2 | **Evidence charts** on Why trust it: (a) bar chart by year, riskiest 10% vs everyone else; (b) loans, overdrawn vs never, repaid vs defaulted. Read the numbers from `EV` (evidence.json) | Two charts that make the findings obvious | P1 | Sun 1 AM |
| D3 | **Repo is public and clean:** no `data/`, no keys, README sources complete; test the link in a private browser window | Link works logged-out | P0 | Sun 9 AM |
| D4 | **Write-up draft** for Devpost (the question, what we did, what we found), from `docs/FINDINGS.md` | P1 reviewed it | P0 | Sun 9 AM |
| D5 | **Video** (2:00–2:10), recorded from the running app; public YouTube or Drive link | Link works logged-out | P0 | Sun 10:30 AM |

**Claude Code prompt for D2:**
```
Read CLAUDE.md. In ui/pages/evidence.py, add two Plotly charts using only values from EV (evidence.json):
(1) grouped bars per predicted year (EV["trough"]["by_year"]): first-overdraft rate for the riskiest 10%
vs everyone else, labelled with the risk ratio; (2) for loans (EV["loans"]): repaid vs defaulted for
"ever overdrawn" vs "never overdrawn". Colours from ui/style.py. Titles state the takeaway. Run
pytest -q -m ui.
```

---

## Timeline

| When | Milestone |
|---|---|
| Now | P1 creates the repo (E1); everyone runs it (first 30 minutes) |
| **Sat 8 PM** | **Devpost draft + Tangerine track (D1)**; formula hand-check (E2) |
| Sat 10–11 PM | Demo mode, Gemini live, twist-card tests, customer summary |
| **Sun 2 AM** | **Feature freeze.** After this, only fixes and polish. |
| Sun 2–7 AM | Sleep in shifts; P1 keeps `main` green |
| Sun 8–10:30 AM | Screenshots, write-up, video, rehearsal (pitch guide comes separately) |
| **Sun 11 AM** | **Submit** (Devpost closes at 12) |
| Sun 1:00–2:30 PM | Demos: someone at the table the whole time |

## Definition of done for any task

- [ ] Works in the running app (`streamlit run app.py`)
- [ ] `pytest -q` passes, and `pytest -q -m ui` passes if you touched `app.py` or `ui/`
- [ ] Only your files changed (check `git status`)
- [ ] No formulas in pages; no data or keys committed
- [ ] PR opened with the template filled in, and P1 has reviewed it
