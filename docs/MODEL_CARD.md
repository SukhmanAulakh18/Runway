# Model card: Runway liquidity early warning

Structured after OSFI Guideline E-23 (Model Risk Management, effective May 1, 2027), which applies to federally regulated
financial institutions and covers any model that "processes input data to generate results", including AI.
Inventory fields follow E-23 Appendix 1. Every number is recomputed by `python evidence.py` (see `evidence.json`).

## 1. Inventory record (E-23 Appendix 1)
| Field | Value |
|---|---|
| Model ID | RUNWAY-EWS-001 |
| Name and key features | Runway: liquidity trough early warning, realistic runway, calibrated Monte Carlo, dip-sized cushion, diagnosis → action, loan-approval review rule |
| Use | Advisor decision support: who to contact before a first overdraft, why, and what to offer; flag loan applications for review. **Not** an automated credit decision. |
| Proposed risk rating | **Medium**: customer-facing recommendations and a credit-review flag, but a human advisor acts on every output |
| Model owner / developer | Team Runway (P1: engine lead) |
| Origin | Internal. One third-party component: Google Gemini (Vertex AI) for wording only; it never produces a number |
| Version | Git commit of `main` at deployment |
| Data sources | Tangerine track dataset (PKDD'99 Financial, re-dated 2020-2025): monthly summaries, 1.06M transactions, 682 loans, clients, accounts, districts, cards, standing orders (today's view only) |
| Approved uses | Ranking customers for outreach; sizing alerts and auto-transfers; stress-testing a stated shock; flagging loans for human review |
| Not approved for | Automatic decline of credit; pricing; any use on populations unlike the training data (see Limits) |
| Dependencies | Python (pandas, numpy, scipy, scikit-learn, statsmodels), FastAPI, React; Gemini via Vertex AI with an offline fallback |
| Last review / next review | Datathon validation Nov 2026 / on any breach in section 5, or yearly |
| Monitoring status | Live in the app (Why trust it → Model health): no breaches at last run |

## 2. Purpose and design (E-23 3.1, 3.3)
- **Problem:** banks measure resilience by averages; overdrafts happen at the low point of the month.
- **Score:** liquidity trough = lowest balance ÷ average balance over 6 months; riskiest 10% are flagged (12+ months of history to score).
- **Forecast:** Monte Carlo (2,000 futures, 3-month block bootstrap of the customer's own months), calibrated with a 2-parameter logistic fitted on 2023→2024.
- **Runways:** the judges' formula exactly (never modified) and a realistic version (last 12 months, EI capped and ending, pensions kept, in-month dip, loans counted from the month granted).
- **Actions:** diagnosis in triage order (already overdrawn → money in fell → heavy new loan → swings → dip), each with a sized action; no-risk steps (alert, call) before any credit.
- **Explainability:** every output is a plain-English sentence with its numbers; the verdict names the biggest driver in months.

## 3. Data (E-23 3.2)
- Quality checks run on every evidence build (section 5): components of money in/out add up on 100% of rows; 0 missing; 0 negative flows.
- Lookahead controls: the Time Machine cuts every input at the as-of month; loans count only from the month granted; loan outcomes and standing orders (an end-2025 snapshot) are hidden or excluded in backtests. Each control has a test.
- Representativeness: re-dated 1990s Czech data, about 75% cash. Money in is not pay.

## 4. Validation (E-23 3.4)
All out of time: features up to December, outcome the next year.

| Claim | Result |
|---|---|
| Riskiest 10% → first overdraft | 12.8–17.9× everyone else in 2023, 2024 and 2025; AUC 0.84–0.86 |
| Robust to confounders | Odds ratio 16.8 (95% CI 9.5–29.7) after balance size, account age, unemployment |
| Multiple testing | 37 of 45 ideas survive Benjamini–Hochberg (q = 0.10); failures listed in the app |
| Forecast calibration (2025) | Predicted 1.61% vs 1.61% observed; AUC 0.88; Brier 0.0142 beats the base rate 0.0158 |
| Product backtest (2025) | Flag 10% → 34 of 55 first overdrafts; dip-sized buffer covers 27 of 34; alert fires before 23 of 34, median 3 months early, pinging 22% of flagged customers who never needed it |
| Loan review rule (all 682 loans) | Holds 17%; catches 41 of 76 defaults; held loans default 34.7% vs 6.2% (clean outcome: 10.2% vs 3.4%, p = 0.003) |
| Simulation audit | Deterministic; stable across seeds; monotonic in shock size; 0 errors over 4,500 accounts × 3 README twists |

Independence: validation here was done by the same team with automated, reproducible tests. Before production, an
independent reviewer (E-23 3.4) should re-run `python evidence.py` and challenge the choices in section 6.

## 4b. Fairness
Checked by owner gender and age band for 2024 and 2025 (`evidence.json -> fairness`). Flag-rate ratio women ÷ men: 1.12
and 0.86, both within the four-fifths band (0.8–1.25). Catch rate (share of first overdrafts flagged): women 71% vs men
50% in 2024, 50% vs 72% in 2025. The gap flips direction and is significant in neither (Fisher p = 0.30, 0.10). Gender
and age are never model inputs. 60+ customers are rarely flagged because most are steady pensioners with a near-zero
overdraft rate. Both fairness measures are monitored (section 5).

## 4c. Scale
The core signal is one SQL query (`sql/trough.sql`, standard window functions) that runs inside a data warehouse. A test
checks it returns the same trough and the same riskiest-10% flags as the Python engine on all 4,500 accounts.

## 5. Ongoing monitoring (E-23 3.6)
E-23 requires defined breach thresholds but sets no numbers. These are our stated choices:

| Monitor | Threshold | Last value |
|---|---|---|
| Trough score drift (PSI, year on year) | watch > 0.10, breach > 0.25 (industry convention) | 0.007 |
| Money in drift (PSI) | same | 0.004 |
| Early-warning AUC, each year | breach < 0.75 | 0.84 / 0.84 / 0.86 |
| Calibration, predicted ÷ actual | breach outside 0.67–1.5 | 1.00 |
| Fairness: flag-rate ratio women ÷ men | watch outside 0.8–1.25 (four-fifths rule) | 0.86 |
| Fairness: catch-rate gap women vs men | watch p < 0.05, breach p < 0.01 | p = 0.10 |
| Data quality | breach if any check fails | all pass |

A breach triggers re-validation and a review of the risk rating. CI checks every pull request (`.github/workflows/ci.yml`).

## 6. Limits and judgement calls
- Signal, not cause. The trough and the plain lowest balance are statistically tied; the claim is that the low point beats both runway formulas.
- Job loss assumes all non-pension money in stops (a slider shows this assumption).
- Loan status D ("in debt") is partly defined by overdraft; the clean outcome (B, finished unpaid) is reported alongside.
- Diagnosis reasons hold in 2025 and point the same way in 2024; the heavy-new-loan reason has too few cases to prove.
- Dollar figures are amounts lent or drawn, not losses (recoveries aren't in the data).

## 7. AI component (E-23 AI/ML expectations)
- Gemini reads twist cards into settings shown as chips before anything runs, and writes the brief, plan and EN/FR message.
- **It never calculates.** Every number in AI text must appear in the engine's facts (`verify_numbers`), and simulation counts can't be called a "chance" (`verify_wording`); otherwise a template is used.
- Hard 6-second limit, then rules or template; tests use fakes, so they never call the live model.
- Customer messages carry no risk percentages; credit is offered only after a call.

- **Measured, not assumed.** `scripts/eval_ai.py` scores the twist-card reader on tuned and held-out cards (an invented shock counts as an error) and writes `docs/AI_EVAL.md`. Offline rules: 22/22 tuned, 8/16 held-out, so they are a fallback only.

## 8. Decommissioning (E-23 D.2)
Retire on repeated monitoring breaches or a change in data or use. Keep the last version and its `evidence.json` as a
benchmark. Delete the Vertex project (`gcloud projects delete <project>`) to stop the AI component.
