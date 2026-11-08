# Judge Q&A: one-line answers, with the number to point at

Every number is in `evidence.json` (rebuild: `python evidence.py`) and on the "Why trust it" screen.
Rule for the table: answer in one sentence, point at the screen, stop. Never claim the ratio beats the plain low point.

## The 60-second pitch (Pitch mode, press → five times)
1. **Finding:** banks watch the average; overdrafts happen at the low point. Flag 10% → catch **34 of 55 (62%)** first overdrafts, three years running.
2. **One customer (93172, Dec 2024):** looks fine ($18,503 average, standard runway "no shortfall") → dipped to **$238** → the bank lent **$167K** that month → realistic runway **2.4 months** → overdrawn in January. A trough check at approval would have held the loan.
3. **Twist card:** read the verdict, then "What moves the answer".
4. **Plan:** fix the cause first (call), then no-risk steps (alert, transfer from savings); a limit comes last, with its real cost.
5. **Trust:** tested on years the model never saw; model health shows no breaches; what failed is listed.

## Bankers (Scotiabank, RBC, CIBC, Sun Life)
| Question | Answer |
|---|---|
| Isn't the trough just a low balance? | Yes, that's the point: the standard runway and the average both miss it. 93172 averaged $18.5K and the formula said "no shortfall". The ratio and the plain low point are tied; both beat both runway formulas. |
| Why offer credit to your riskiest customers? | We don't lead with it. Alert and call first, then an auto-transfer from their own savings ($0); a small limit only after a call, at Tangerine's terms (~$108 for a $6,527 limit used a whole month). Every overdrawn borrower here defaulted. |
| What does it do for the bank? | Loan review rule: holds **17%** of loans; held loans default **34.7% vs 6.2%** (clean outcome **10.2% vs 3.4%**, p = 0.003). 93172's $167K loan would have been held. |
| False positives? | The alert pinged **22%** of flagged customers who never went overdrawn (0.65 pings a year); **1 in 4** alerts was followed by a real overdraft vs a 1.6% base rate. |
| Regulation? | Model card in the OSFI E-23 inventory format (effective May 1, 2027), monitoring with stated breach thresholds, human in the loop for every action. |
| Is it fair? | Checked by gender and age in two years: flag rates within the four-fifths band (0.86, 1.12); the catch-rate gap flips direction between years and is significant in neither (p = 0.30, 0.10). Gender and age are never inputs. Monitored every period. |

## AI judges (OpenAI, Meta, Microsoft, IBM)
| Question | Answer |
|---|---|
| Can the AI make up a number? | No. Every number in AI text must appear in the engine's facts (`verify_numbers`); simulation counts can't be called a "chance" (`verify_wording`). Otherwise a template is used. |
| Prompt injection through the twist card? | Gemini returns schema-typed JSON only; values are clamped (`_sanitize`); the rule parser cross-checks and flags disagreements; the chips must be confirmed before anything runs. |
| What if Gemini is slow or down? | Hard 6-second limit (one call once hung 92 s; fixed), then rules or template. Tests use a fake model, so they never call the live one. |
| Why not an ML model instead of a ratio? | We tried: a combined logistic model caught 33 vs the trough's 34 of 55. The simple, explainable ratio won; the extra signals choose the action instead. |
| How do you know the simulation is right? | Audited: deterministic, stable across seeds, monotonic, 0 errors on 4,500 accounts × 3 twists. Raw it was 8× too pessimistic (customers steer back); calibrated, it predicted 1.6% vs 1.6%. |

## Consultants (Accenture, EY, PwC): the pilot plan
| Phase | What happens | Success measure |
|---|---|---|
| 0–3 months: shadow | Score the whole book monthly; no customer contact; compare flags with real overdrafts | Catch rate and monitoring stay within thresholds on Tangerine data |
| 3–6 months: controlled pilot | Random half of flagged customers get the call + alert + transfer offer; the other half business as usual | First-overdraft rate, complaints and NSF fees, treated vs control |
| 6+ months: scale | Advisor call list in the CRM; loan review rule at origination | Overdrafts and loan losses avoided; advisor time per call |

## Data platforms (Snowflake, Dataiku, Thomson Reuters)
| Question | Answer |
|---|---|
| Does it scale to millions of accounts? | The core signal is one SQL query (`sql/trough.sql`, window functions) that runs in the warehouse; a test checks it gives identical results and flags to the Python on all 4,500 accounts. |
| Reproducible? | `python evidence.py` rebuilds every number; CI runs on every pull request; the data is never committed. |
| Data quality? | Checked on every build: money in/out parts add up on 100% of rows, 0 missing, 0 negative. Lookahead controls each have a test (Time Machine, loans counted from the month granted, standing orders excluded from backtests). |

## Professor / methodology
| Question | Answer |
|---|---|
| Overfitting? | Features up to December, outcome the next year, three separate years; thresholds fixed before the year they're judged on. |
| Multiple testing? | 45 tests, Benjamini–Hochberg q = 0.10: 37 survive; the failures are on screen with what we did about each. |
| Confounders? | Odds ratio 16.8 (95% CI 9.5–29.7) after balance size, account age and district unemployment. |
| Biggest weakness? | Money in is mostly cash, so a job loss assumes all non-pension money in stops; the slider shows it. And it's 1990s Czech data, which is why the pilot starts in shadow mode. |
