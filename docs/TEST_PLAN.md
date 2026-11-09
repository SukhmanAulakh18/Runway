# Test plan: how Runway is checked, from a code change to a live link

Every number on screen comes from `engine.py`; the tests check the maths, the API that carries it, the screens that
read it, the AI that words it, and the container that ships it. Run order before any merge:

```bash
pytest -q && pytest -q -m ui && pytest -q -m slow     # locally, with the data
python scripts/eval_ai.py                              # when ai.py changes (Vertex machine for Gemini rows)
python scripts/smoke.py http://localhost:8080          # against Docker or the Cloud Run URL
```

## 1. Stages of the lifecycle and what checks each

| Stage | What could go wrong | Check | Where |
|---|---|---|---|
| Requirements | The judges' formula drifts from the README | Answer-key tests: 20111 job loss 3.4 months, one-month repair 4.0, combo 3.4; **and an independent re-implementation (plain Python, no pandas, loan status from the status letter) agrees on all 36,000 cases = 4,500 accounts × 8 scenarios** | `test_acceptance.py`, `test_api.py`, `test_formula_all_accounts.py`, `scripts/smoke.py` |
| Design | Maths leaks into the screens or the AI | Rule: all maths in `engine.py`; the AI contract test fails if `Scenario` or the plan facts change shape | `test_ai_cards.py::test_ai_engine_contract` |
| Build: engine | A calculation is wrong or looks into the future | Unit and acceptance tests per function, including no-lookahead guards (Time Machine, loans from the month granted, survival cohort two years back) | `test_acceptance.py` (65 tests) |
| Build: statistics | A finding stops holding when code changes | Slow tests rebuild each evidence section and assert the claim: trough risk ratio, calibration, BH survivors, loan rule, fairness, survival hazard ratio, challenger tie, buffer curve | `pytest -m slow` (14) |
| Build: API | A screen reads a number the API no longer sends | Contract tests per endpoint; a test parses the React screens for every evidence section they read and checks the API serves it | `test_api.py` (21 tests) |
| Build: AI | Gemini invents a number or misreads a card | Fake-model tests (number checker, wording checker, timeout, fallback); evaluation on tuned, dev and held-out cards | `test_ai_cards.py` (17), `scripts/eval_ai.py` → `docs/AI_EVAL.md` |
| Build: screens | A page crashes on an odd account | Headless click-through of the Streamlit backup on tricky and random accounts; React type-check + build | `pytest -m ui` (6), `npm run build` |
| Accessibility | Colour-only meaning, low contrast | axe-core WCAG 2 A/AA on all five screens: 0 violations | browser run before each PR |
| Integration (CI) | A pull request breaks the build | GitHub Actions: compile, data-free tests (data tests skip with a reason), dashboard build | `.github/workflows/ci.yml` |
| Release | The container differs from the laptop | Docker image built for linux/amd64, then the smoke script against it | `Dockerfile`, `scripts/smoke.py` |
| Operate | The model degrades on new data | Monitoring with stated thresholds: drift (PSI), AUC floor, calibration band, data quality, fairness | `evidence.json -> monitoring`, Why trust it screen |

## 2. Test cases for each financial calculation shown on screen

| Calculation (engine) | Screen | Test case | Expected |
|---|---|---|---|
| Judges' runway (`profile`, `runway`) | Customer, Stress | 20111 with each README twist | 3.4 / 4.0 / 3.4 months exactly |
| Realistic runway (`realistic_profile`, `realistic_runway`) | Customer, Stress | 93172 at Dec 2024 | 2.4 months (new $4,638/month loan counted) |
| Liquidity trough (`ltr_table`, `liquidity_trough`) | Customer, Overview | Python vs SQL on all accounts; 93172 percentile | identical values and flags; riskier than 98% |
| Haircut (`liquidity_trough`) | Customer | 93172 | equals 1 − trough, above 95% |
| Calibrated risk (`overdraft_risk`) | Customer | 93172 at Dec 2024; 2025 backtest | 13.8%; predicted 1.61% vs 1.61% observed |
| Monte Carlo (`simulate`) | Stress | same account twice; shocked vs calm account | identical; p10 ≤ p50 ≤ p90; the calm account survives at least as well |
| Cushion and alert (`cushion`) | Plan | 93172 | alert = buffer = typical dip; conservative ≥ default |
| Buffer confidence (`evidence.buffer_confidence`) | Plan | 2024 and 2025 curves | coverage and limits rise with the level; drawn < 5% of limits |
| Overdraft cost (`overdraft_cost`) | Plan | $6,527 for a month | $5 fee + 19%/yr ≈ $108 |
| Optimiser (`optimize_cuts`) | Plan | 20134 with a repair; 93172 | every cut within the cap; protected path above the dip; 12-month horizon (bills and insurance are excluded by construction) |
| Diagnosis (`diagnose`) | Customer, Plan, call list | 93172 | money in fell 27% → "call first" |
| Loan check (`loan_check`) | Customer, Overview | 93172's Dec 2024 loan, data to Nov 2024 | held for review |
| Book tiers (`book_tiers`) | Overview | Dec 2024 | every customer in one tier; 93172 = act now; rates from a year already over |
| Survival (`survival_cohort`, `when_overdraft`) | Customer, Evidence | Dec 2024 view | uses the 2022 cohort; 6 ≤ 12 ≤ 24-month shares |
| Challenger (`evidence.challenger`) | Evidence | 2025 | trough is the top feature; McNemar and AUC p > 0.05 |
| Runway vs formula (`evidence.out_of_time` etc.) | Evidence | 2025 | realistic AUC above the formula's, CI above 0 |

## 3. Known limits of the tests
- Data tests can't run on GitHub (the data is never committed); they run locally before every merge.
- Gemini's live accuracy is measured by `scripts/eval_ai.py`, not by CI (CI uses a fake model, so it never calls Vertex).
- Accessibility is checked in the browser by hand before each PR, not in CI.
