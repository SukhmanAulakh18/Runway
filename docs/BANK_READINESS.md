# Bank readiness: what a bank can run today, how it maps to model-risk guidance, and what is still missing

This is a **mapping and a gap list, not a compliance claim**. Nothing here is legal advice; a bank's model-risk,
compliance and legal teams decide what applies. Every result quoted is in `evidence.json` (rebuild: `python evidence.py`).

## 1. What a bank can do today

| Task | How | Where |
|---|---|---|
| Score its own book | Export a monthly summary that meets the data contract (section 2), run the batch scorer | `python scripts/score_book.py monthly.csv --out call_list.csv` |
| Size the call list to its capacity and costs | Pick a flag size, enter its own cost per call and value of preventing an overdraft | Overview, "For the bank" (`POST /api/bank-case`) |
| Plan a pilot | Sample size for a random half-and-half test, from the measured first-overdraft rate | Same card |

**What is measured vs what is yours.** The catch counts come from our out-of-time backtest (features up to December,
outcome the next year, 2024 and 2025 pooled). Every dollar figure is the bank's own input and starts blank. A "catch" is a
flagged customer who then went overdrawn; it is **not** a prevention. Whether a call prevents it is what the pilot measures.

| Flag the riskiest | First overdrafts caught (2024 / 2025) | Customers called per catch (2024 / 2025) |
|---|---|---|
| 2% | 21% / 29% | 6.4 / 4.3 |
| 5% | 41% / 49% | 7.9 / 6.3 |
| 10% | 59% / 62% | 11.1 / 10.1 |
| 20% | 76% / 76% | 17.0 / 16.3 |
| 30% | 82% / 82% | 23.7 / 22.8 |

The economics depend on what preventing one overdraft is worth. With example inputs of a $12 call, $150 per prevented
overdraft and calls that prevent 30% of what they catch, a 5% flag loses money (break-even is about $275 per prevented
overdraft). That is why the card asks for the bank's own numbers, and why the pilot comes before any rollout.

## 2. Data contract

One row per account per month (`engine.check_monthly_contract` checks all of it and names each problem; nothing is scored if
any fails).

| Column | Meaning | Rule |
|---|---|---|
| `account_id` | Account identifier | integer; one row per account-month |
| `month` | Calendar month | `YYYY-MM` |
| `money_in` | Total credits in the month | number, not missing |
| `min_balance` | Lowest end-of-day balance in the month | number; not above `avg_daily_balance` |
| `avg_daily_balance` | Average of the daily balances | number |
| `days_below_zero` | Days the balance was below $0 | number, 0 or more |

Optional: `money_out`, `month_end_balance` and the spending breakdown columns the full app uses. History: the trough needs
12 or more months per account; accounts with 3 to 11 months are scored by swings in money in; under 3 months are not scored.

The scorer's output has one row per account, most urgent first: `tier`, `tier_label`, `action`, `trough`, `riskier_than_share`,
`lowest_balance`, `average_balance`, `months_of_history`, `haircut`. Tiers and actions are the app's whole-book tiers.

## 3. Model-risk mapping (US SR 11-7 and Canada's OSFI E-23)

| Expectation | What exists | Gap |
|---|---|---|
| Model inventory and documentation | `docs/MODEL_CARD.md` in the E-23 inventory format; `docs/SPEC.md` defines every number | Owner, validator and approval fields to be filled by the bank |
| Conceptual soundness, development evidence | Definitions in code and spec; out-of-time backtests on three years; confounder control; multiple-testing correction; calibration | Evidence is on re-dated 1990s Czech data, mostly cash income |
| Outcomes analysis and backtesting | `evidence.json`: trough by year, calibration, capacity trade-off, survival, champion vs challenger | Needs the bank's own data and a longer history |
| Ongoing monitoring with thresholds | 10 monitors (drift, accuracy, calibration, fairness, data quality) with stated thresholds | Thresholds are our choices; automate a monthly run and alerting; the bank approves limits |
| Independent validation, effective challenge | An independent re-implementation of the judges' runway formula agrees on 36,000 cases (`tests/test_formula_all_accounts.py`) | That checks the formula, not the risk model: a validator who did not build it must re-run `python evidence.py` and challenge the choices |
| Governance, change control, testing | 130+ fast tests plus UI, slow and contract tests; CI on every change; a change log (`docs/HANDOFF.md`) | Approval workflow, versioned releases, access control |
| Limitations and use restrictions | Stated in the model card: advisor decision support, not an automated credit decision | Keep them in force; add the bank's own |
| Data quality and lineage | Data checks on every build; the data contract above | Lineage back to the bank's source systems |

## 4. Fairness and fair lending

- **Done:** gender and age are never inputs; flag rates by gender sit inside the four-fifths band in both years tested (ratios
  1.12 and 0.86); the catch-rate gap flips direction and is not significant in either; two fairness checks are in monitoring.
- **Needed before any real use:** disparate-impact testing on the bank's own population across the groups its regulators
  require; a review of whether any input is a proxy; documented reasons for each action.
- **The loan-approval rule is a review flag, never an automatic decline.** If a bank used it in any credit decision, fair-lending
  rules (for example ECOA and Regulation B in the US) would apply and need legal and compliance review. It holds 17% of
  loans and 77 good loans in our data: review means talk first, not reject.

## 5. Pilot

1. **Shadow mode, about 3 months:** score the whole book monthly with no customer contact; compare flags with real overdrafts;
   check the monitors stay inside their limits on the bank's data.
2. **Controlled test:** a random half of flagged customers get the call and alert; the other half business as usual. Size it
   from the card. Detecting a 25% drop (80% power, 5% significance) needs about 900 flagged customers per group at a 2% flag,
   1,300 at 5%, 2,100 at 10% and 3,400 at 20%: a smaller, riskier flag needs fewer people because more of them go overdrawn.
   Add a 12-month follow-up. Measure first-overdraft rate, fees, complaints and call time.
3. **Decide:** scale only if the drop is real and the break-even holds on the bank's own numbers.

## 6. Not built yet, and why

| Item | Why it is not here |
|---|---|
| Sign-in, roles and an audit log | Needs the bank's identity system; adding our own would be a placeholder |
| Scheduled monthly runs | Needs the bank's scheduler and warehouse access (the trough exists as one SQL query, `sql/trough.sql`) |
| A learning loop (log what the advisor did and what happened) | Needs persistent storage, privacy rules and consent decisions that belong to the bank |
| Replication on a second dataset | Needs a suitable transaction-level dataset; the strongest version is the bank's own |
| A natural-language "Ask Runway" | Would need the AI module (a separate lane) and a verification step as strict as the existing number check |
