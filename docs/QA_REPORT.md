# Runway QA report: every page, every kind of customer, every Time Machine date

Run on November 8, 2026, against the app built from branch `p1/edge-states` (`main` plus the fixes below).
Purpose: make sure what the judges see is correct, complete and readable, not only that the engine is right.

## 1. What was tested

**Engine and API sweep.** 67 accounts (60 random + 93172, 20111, 20176, 97909, 21284, 55447, 82420) × 3 dates
(Today = Dec 2025, Dec 2024, Dec 2023) = 201 customer-dates, each through `/api/customer`, `/api/shock`
(job loss + bills +15%) and `/api/plan`.

| Result | Count |
|---|---|
| Server errors or NaN / infinite values | **0** |
| Account didn't exist yet at that date (correct 404) | 14 |
| Tiers seen | stable 107, new 28, watch 26, act 17, overdrawn 6, new and swinging 3 |
| No personal forecast (too new, or overdrawn before) | 40 (about 20% of views) |

**Page run-through in the browser.** Every screen opened with every fold expanded, checked for broken values
(NaN, undefined, null, "$-", "n/a"), empty charts, script errors and WCAG 2 A/AA violations (axe-core):

| Screen | Customers / dates checked | Broken values | Empty charts | Accessibility |
|---|---|---|---|---|
| 01 Who's at risk | Today, Dec 2024, Dec 2023 | 0 | 0 | 0 violations |
| 02 Know the customer | 93172 (Dec 2024: act now; Dec 2023: too new), 20111 (overdrawn), 97909 (stable), 21284 (new and swinging), 85080 (overdrawn before, no forecast) | 0 | 0 | 0 |
| 03 Stress test | the same six, plus the README combo on 20111 | 0 | 0 | 0 |
| 04 Make a plan | the same six | 0 | 0 | 0 |
| 05 Why trust it | Today, Dec 2024, Dec 2023 | 0 | 0 of 4 | 0 |
| Pitch mode | all 5 steps with the arrow keys | 0 | 0 | no script errors |

**Live link.** `scripts/smoke.py` against https://runway-1085585470420.us-central1.run.app: 8 of 8.

**Automated tests.** 125 fast, 6 UI, 14 slow (unchanged engine); CI mode 49 pass / 76 skip / 0 fail.

## 2. What was wrong, and what we changed

| # | Where | Problem a judge would see | Fix |
|---|---|---|---|
| 1 | Know the customer, forecast card | **"n/a"** for any customer without a personal forecast (93172 at Dec 2023; about 1 view in 5). Looked broken. | Shows the tier's tested rate instead: "Customers in their tier: overdrawn the next year, **2.4%**", with the real reason and the cohort it was tested on (a year already over, so no lookahead). |
| 2 | Same card | Wrong reason: customers overdrawn *before* (e.g. 85080 today) were told "Needs 12+ months of history". | The reason now matches: "they were overdrawn before, and the forecast is tested on customers never overdrawn". |
| 3 | Know the customer, trough card | A big "85%" next to "Needs 12+ months of history" read as a contradiction. | "Not ranked yet: 10 of the 12 months needed to compare fairly". |
| 4 | Any page, account not open yet | Bare "Account 77040 has no data up to 2023-12". | "Account 77040 opened after 2023-12: switch the Time Machine to a later date." (or "isn't in the data: try 93172…") |
| 5 | Make a plan, headline | "safe for all 12 months in **a a** bad case" | "safe for all 12 months, even in a bad case" |
| 6 | Make a plan, headline | "12 months instead of **0**" | "12 months instead of less than 1" |
| 7 | Who's at risk, job-loss chart | Always today's data, but didn't say so; in a Dec 2023 view it quietly showed 2025 numbers. | Subtitle now says "on today's data (Dec 2025) whatever the Time Machine is set to". |

Earlier today (already on `main`): every customer's tier badge on Know the customer; the "Our runway vs the judges'
formula" card on Why trust it (out-of-time AUC 0.84 vs 0.78 and three formula holes were only on the Streamlit backup).

Engine and findings: **no change**. Every fix is in what the screen says, plus one lookup in the API (the tier's
tested rate, from the same cohort the whole-book card already uses). Two new tests pin fixes 1, 2 and 4.

## 3. What is on screen, and is it worth it

| Screen | Keeps its place because | Weak spot (keep out of the pitch) |
|---|---|---|
| 01 Who's at risk | The finding in one line; the whole book (10% of customers → 58–68% of next year's overdrafts); the call list; the loan rule | "Who the riskiest are" also appears on Why trust it |
| 02 Know the customer | The 4-step story strip, tier badge, both runways, the cause and the action, "When?", the loan check | none |
| 03 Stress test | The verdict + biggest reason is the best answer to the live twist; the AI/rules disagreement flag | Exposure profile (uncalibrated; folded away) |
| 04 Make a plan | Cause first, free steps first, real Tangerine cost, the backtested cushion and risk appetite | The cuts chart can ask for large cuts (93172: about $3,787 a month); "needs a bridge first" under a shock is honest but not a pitch moment |
| 05 Why trust it | Runway vs formula, model health, 3-year backtest, calibration, survival, challenger, fairness, failures and limits | Dense (about 2,000 words); point at the headline cards only |

## 4. Where we stand

- **Engine and findings:** correct and unchanged; every number reproduces from `python evidence.py`.
- **What the judges see:** every feature we built is on its screen; after this run no page shows a broken value,
  an "n/a", a contradiction or a wrong reason, for any kind of customer or date we tried.
- **Live:** the public link serves the checked build (redeployed after this fix; see `docs/DEPLOY.md`).
- **Rating:** 8.7 / 10 overall (Discovery 8.5, Data use 9.5, Communication 8 → 8.3 with these fixes, Impact 8.5).
  On substance, likely top 3 in the Tangerine track with a real shot at 1st; that's a judgement, not a measurement.
- **What still decides it:** rehearsal. Pitch mode five times; the live twist on 93172, 20111 and 20176; and,
  new from this run, try one judge-style surprise: a young account in Dec 2023 (it now explains itself instead of "n/a").
