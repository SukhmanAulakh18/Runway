# Findings log (Tangerine: Resilience Rewired)

Every hypothesis tested goes here, pass or fail, so the Benjamini-Hochberg correction is honest.
Data: PKDD'99 Financial dataset as provided (4,500 accounts, 2020-01 to 2025-12).

## Audit notes (Sat ~1:30 PM)
- All files present; row counts match README. No missing values in monthly_summary.
- money_in / money_out components sum exactly to totals.
- 12 to 72 months per account (median 36). 76 accounts end before 2025-12.
- Cash dominates: 74.9% of money in is cash deposits; 76.4% of money out is cash withdrawals.
- Loans: status C/D == still running at end of 2025 by date (checked). 76 defaults of 682 (11.1%).
- Engine reproduces the judges' formulas; scalar and vectorised versions agree.

## Hypotheses tested
| # | Hypothesis | Result | Status |
|---|---|---|---|
| 1 | Median-based "spending > income" flags real deficits | 1,181 accounts flagged (26%); 97.5% of them have positive mean net flow, 90.4% ended with a higher balance | Candidate finding, needs cause analysis + CI |
| 2 | Flagged accounts still have more negative-balance months | 11.9% vs 4.4% (any negative month) | Nuance: lumpy, not broke (liquidity vs solvency) |
| 3 | Out-of-time (features <=2024, outcome = any negative-balance day in 2025; n=3,668, 129 events): which measure predicts distress? | AUC: judges' runway (EI 55%) 0.783; mean-based runway 0.837; 10th pct of monthly min balance 0.874; buffer/spend 0.786; income CV 0.741; prior negative 0.758; low-income-month share 0.703; median gap 0.611; mean gap 0.697 | Candidate; 9 measures compared -> needs bootstrap CIs on AUC differences |

## Explain-it-back
- AUCs are single point estimates on one split; no intervals yet.
- min-balance predictor is partly mechanical (accounts that dipped low before are near zero), so frame it as "measure the trough, not the average", and check it beats prior_neg.
| 4 | Real 2026 EI cap ($729/wk) changes job-loss outcomes | 57.2% capped; their median runway 5.4 -> 3.1 mo; surviving 6 mo 44.5% -> 16.3% (all accounts 64.9% -> 48.8%) | Policy fact, not a predictor |
| 5 | Realistic runway variants vs answer key, out-of-time (1,000 bootstrap) | mean flows +0.054 [+0.030,+0.081]; + cap + pension +0.028 [+0.002,+0.057]; + dip +0.039 [+0.016,+0.065]; last-12m + cap + pension + dip +0.058 [+0.031,+0.089] (AUC 0.841 vs 0.783) | Chosen: last-12m version. 4 variants, all CIs exclude 0 |

## Explain-it-back (v2)
- The EI cap lowers predictive AUC slightly vs uncapped means: expected, because the 2025 outcome is a no-shock overdraft. We keep the cap because it's the law, not because it predicts.
- "Earned income" = money_in minus pension and interest; includes cash deposits, so EI may be overstated for cash-churn customers.
- Simulation replays the customer's own months; it can't produce situations they've never lived through.
| 6 | Reproduce the other analysis (no-shock runways, lowest balance) | Exact: median no-shock 0.626, mean no-shock 0.541, lowest 2024 balance 0.853, prior-6-month low 0.842, never-negative group 4,232/89/0.772. Conflict explained: with no shock ~100% of accounts show no shortfall, so runways can't rank; under the EI shock mean 0.777 > median 0.727 | Resolved |
| 7 | Liquidity Trough Ratio, first-time overdrafts | 2025: 3,417 accts, 55 events, bottom 10% 9.9% vs 0.68%, RR 14.6 [8.5, 24.8], AUC 0.860 [0.809, 0.911]. 2024: AUC 0.844, RR 12.8. 2023: AUC 0.841, RR 17.9. Window 3/6/12: 0.839/0.860/0.859 | Headline finding |
| 8 | Same population head to head (2025) | trough 0.860, lowest balance 0.840, realistic runway 0.759, answer key 0.685; rank-average of runway + trough 0.827 (no gain) | Trough = early warning; runway = stress test |
| 9 | Watchlist top-50 (Time Machine) | Without a history rule, 98-100% of top 50 were <8-month accounts (opening-month artefact): 1/50 hits as of Dec 2023. With 12+ months: 7/50 (vs 1.5% base) as of Dec 2023, 14/50 (vs 1.7%) as of Dec 2024 | Fixed: score only 12+ months |
| 10 | Overdraft vs loan outcome | ever overdrawn: 76/76 defaulted; never: 0/606. Status A/C never overdrawn; B/D all overdrawn | Finding 5 (D partly definitional) |
| 11 | Pre-loan overdraft vs default | 27/27 vs 49/655, Fisher p = 1.6e-28; $3.48M lent | Clean (before the loan) |
| 12 | Pre-loan trough among 588 borrowers never overdrawn before the loan | AUC 0.775; lowest 20% 19.5% (23/118) vs 3.2%; payment/money-in AUC 0.677; both flags 26.3% | Clean chain to default |
| 13 | Formula blind spots | EI forever: survive 12 mo 39.3% -> 21.8%, 257 flip; pensioners 740 (16.4%), owners 59.2+, pension 98% of money in, formula runway 35.4; p90/median money out 1.96; 57 minors; 64.3% >80% cash; district unemployment 2022~2023 r=0.98 | Built into the app |
| 14 | 93172 critique (dip in Sep, Nov average $3,480) | True. Reframed: dip Sep 2024 -> $166,958 loan Dec 6 2024 at 1.5x monthly money in -> 21 days overdrawn Jan-Feb 2025 -> status D | Demo story |
| 15 | Customers steer back after a low month (real months vs the same months in random order, 30 shuffles; months ≤ Dec of the prior year) | Rebuild-after-low gap +0.174 to +0.183 in 2024 and 2025, cutoffs 20%/30%; 87-91% of accounts positive; sign test p ≈ 0 | **Finding**: explains why the raw Monte Carlo over-predicted overdrafts 8× |
| 16 | Weak steering predicts who in the riskiest 10% goes overdrawn | 2025: p = 0.03 (20%), 0.008 (30%). 2024: p = 0.06 (20%), 0.57 and reversed (30%) | **Not replicated: not claimed** (both kept in the extended BH family) |
| 17 | Personal alert false alarms (Dec 2024 → 2025) | Pinged 68 of 307 flagged customers who never went overdrawn (22%), 0.65 pings/customer/year; 23 of 91 alerts preceded a real overdraft (25% vs 1.6% base) | Product evidence |
