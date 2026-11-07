# CTO review: is Runway a winner? (Sat Nov 7, evening)

Reviewer stance: senior judge / CTO at a bank. Every number here was re-run on the real Tangerine data.
Scoring weights: Discovery 35%, Data Use 25%, Communication 25%, Impact 15%.

## Verdict

**Go. It can win the track, but only if we stop adding features and fix how we talk about probabilities.**
The engine and the evidence are stronger than most datathon entries will be. The risks are overclaiming,
a dense UI, and burning the night on a React rewrite.

| Criterion | Grade | Why |
|---|---|---|
| Discovery (35%) | **A-** | The trough finding holds out of time over 3 years (AUC 0.84-0.86, 14.6×), survives confounders (OR 16.8) and BH correction (28/29). 76 of 76 defaulters were overdrawn; 27 loans went to already-overdrawn customers, all defaulted. That's a real, bank-relevant insight. |
| Data Use (25%) | **A-** | Integrity audit (10 checks pass), quirks handled explicitly (cash economy, opening month, pensioners, minors, stale accounts). Answer key reproduced exactly (20111 → 3.4 / 4.0 / 3.4). |
| Communication (25%) | **C+** | Two runways plus a trough plus a Kalman chart plus a simulation is too much for a 5-minute table. Until today the UI called an uncalibrated number a "chance". |
| Impact (15%) | **B** | An advisor watchlist with a Time Machine reveal is a product a bank could actually pilot. |

## What I found (strict)

### Fixed today (engine and AI lanes, all tests green: 62 fast, 5 slow, 6 UI)

| # | Severity | Finding | Evidence | Fix |
|---|---|---|---|---|
| 1 | **Critical** | **Monte Carlo was not a probability.** As a forecast it said 13.5% of customers would break in 2025; 1.6% did. The top decile said 58%; 8.8% happened. Its Brier score (0.056) was *worse than guessing the base rate* (0.016). The Shock tab shows this number as "Chance they make it 6 months". | out-of-time backtest, now in `evidence.json → sim_calibration` | Ranking was excellent (AUC 0.86), so: Platt calibration fitted 2023→2024, validated 2024→2025. Calibrated mean 1.55% vs 1.61% observed, Brier 0.0152 (beats base 0.0158), AUC 0.863. New `engine.overdraft_risk()` and `calibrate_break()`. |
| 2 | **Critical** | Time Machine lookahead in Streamlit (handoff #1): in Dec 2024 mode the runways, simulation and plan used 2025 data. | 93172 showed 6.6 months | `ui/context.py` cuts the data at `asof`. 93172 Dec 2024 now: standard "no shortfall (120+)", trough riskiest 1.6%, low $238, which is the pitch. |
| 3 | High | Watchlist "realistic runway (EI)" kept paying EI forever; the Know tab stops it after 6 months. Different on 23.5% of accounts (median 3.6 months apart). A judge clicking a row would see two numbers. | stress check [1] | Watchlist uses `realistic_runway_vec` (same function family as Know). New test. |
| 4 | High | An LLM returning `"return_to_work_month": "4"` (string) passed `_sanitize` and would crash the simulation mid-demo. Gemini output was not schema-constrained (handoff #6). | probe | Coerced to an int 1-24 or None; `response_schema` added. Contract test between the AI and engine lanes. |
| 5 | Medium | Kalman: q sits on the grid floor (= "no trend") for 52% of accounts, and the first months' band is huge (handoff #2). | stress check [5] | `net_flow_filter` now returns `has_trend` and `band_from`. **Recommendation: cut the Kalman chart from the demo.** |

### Still open (ranked)

| # | Severity | Finding | What to do | Owner |
|---|---|---|---|---|
| 6 | **Critical (wording)** | Under a shock, `p_survive_6` is a *scenario result*, not a calibrated chance. `ui/pages/shock.py` still says "Chance they make it 6 months", and the plan facts are called `chance_6_months_pct`. | Say "7 of 10 simulated futures last 6 months". Show the calibrated `overdraft_risk` as the only "% chance", and only for no shock. | P3 |
| 7 | High | **"Money in" is not pay.** 74.9% of money in is cash deposits, 19% transfers, 5.2% pension. A job loss assumes all non-pension money in stops (`employment_share = 1`). It's the biggest assumption in the model. | Say it in the first 20 seconds of Q&A; keep the slider visible. | pitch |
| 8 | High | The simulation starts from the 6-month **average** balance (B), not today's balance. For 22.7% of accounts today's balance is >25% above B; for 9.7% it's >25% below. Starting from the latest balance raised AUC 0.866 → 0.878 in backtest. | Switch start to latest `month_end_balance`, refit the calibration, re-run `-m slow`. About 1 hour. Not done today: it moves validated numbers. | P1 (E8) |
| 9 | Medium | The optimiser protects a **pointwise** 10th-percentile path. No customer follows that path, so "safe in a bad outcome" overstates joint survival. | Say "keeps each month above the line in 9 of 10 futures", or solve the LP over sampled paths. | P1 |
| 10 | Medium | Realistic runway (12-month window) vs simulation (24-month history): they agree on 95.2% of 400 accounts. Handoff #4 is lower priority than it looked. | Leave it. | |
| 11 | Low | Loan payment P uses "running at end of 2025" even in the Time Machine. That's the judges' definition and `profile()` must not change. | Mention only if asked. | |
| 12 | Low | `ai._sanitize` caps EI at 12 months; EI regular benefits max out at 45 weeks (~10.4 months). | Cap at 10. | P3 |

## Is the maths "quant level"? Direct answers

- **Monte Carlo:** block bootstrap of the customer's own months, seeded, 2,000 paths. Sound design. Now also *validated and calibrated out of time*, which is the step most teams skip and the one a bank risk team asks about first.
- **Optimiser:** a real linear program (HiGHS) with a receding-horizon story. Fine; fix the wording (#9).
- **Statistics:** out-of-time backtests, bootstrap CIs, Fisher exact, confounder logit, Benjamini-Hochberg. Stronger than needed. Don't add more tests; *say* the ones we have.
- **The trough's honest framing:** it's a liquidity "distance to zero" measure (same spirit as Merton's distance to default). That's why balance size was controlled for. Say it before a judge does.
- **A candidate finding (test it before pitching):** the raw simulation overshoots ~8× because real customers don't behave like a random walk. They correct course near their low point. The trough flags the people for whom that self-correction is failing. If it holds, it ties the Monte Carlo and the trough into one story.
- **C++: no.** One simulation takes ~10 ms; calibrating over 3,417 accounts takes ~30 s. C++ adds build risk and zero points.
- **More AI: no.** AI's job is to read the twist card and phrase the plan, with numbers verified. That's the right, defensible scope for a bank. Turn on Gemini (S1) and stop there.

## Datathon services: use / skip

| Service | Decision | Use it for |
|---|---|---|
| **Google Cloud ($25)** | **Use** | Gemini on Vertex AI for the twist card (S1, `GOOGLE_CLOUD_PROJECT`), and Cloud Run for a live link judges can open. One container. Claim closes 5 PM. |
| **ElevenLabs (Creator, 1 month)** | **Use, video only** | Voiceover for the 2-minute demo video (Communication 25%). Not inside the product. |
| IBM watsonx / Granite | Skip | Aimed at the "Before the Breach" track. A second LLM adds risk, not points. |
| Lovable (Pro, 100 credits) | Skip (maybe) | Only if the React teammate is far behind at 10 PM: scaffold the shell from `docs/FRONTEND.md`, then delete anything that computes money. |
| Backboard ($10) | Skip | Nothing in our product needs LLM memory/routing. |
| n8n Cloud | Skip | No workflow automation in scope. |
| **Sponsor booths (Tangerine, Accenture)** | **Use, 15 minutes** | Ask a Tangerine person: "Would an advisor trust a realistic runway that differs from the formula, if we show both?" and "Is an overdraft early warning useful to you?" Quote the answer in the pitch (Impact). |

## React pivot: decision

React is approved with a midnight go/no-go (HANDOFF). As CTO I'd tighten it. Points come from insight and
communication, not the framework. **Streamlit stays primary.** React ships only if it passes the go/no-go
checklist in `docs/FRONTEND.md` §7 on 5 accounts by midnight. Otherwise show it as "advisor UI preview".
The API draft is ready and tested but held out of the repo until then.

## Pitch (60 seconds, in this order)

1. Demo mode: 93172, Dec 2024. "The standard formula says no shortfall. Her balance averaged $18.5K but dipped to $238. We flagged her in the riskiest 2%. In January she was overdrawn."
2. "That signal predicted first overdrafts out of time, three years running: 14.6× the risk. It survives controls for balance size and correction for the 29 ideas we tested."
3. "Overdrafts matter: all 76 defaulted borrowers had been overdrawn; 27 loans went to customers already overdrawn, and every one defaulted."
4. "And our probabilities are real probabilities: we backtested our Monte Carlo, found it 8× too pessimistic, and calibrated it on 2024. On 2025 it predicted 1.5%; 1.6% happened."
5. "Pick any account and any twist card."

Limits, said first in Q&A: re-dated 1990s Czech data (not Tangerine customers); money in is mostly cash, not pay;
status D is partly "in debt" by definition; it's an early-warning signal, not causal.

## Next 6 hours (in order)

1. P3: fix the "chance" wording (#6) and turn on Gemini (S1). 30 minutes.
2. P2: Know tab: summary sentence first, one chart, add the calibrated risk card from `engine.overdraft_risk`. Drop the Kalman chart.
3. P1: E8, start the simulation at the latest balance and refit the calibration (#8). Test the "self-correction" finding before it goes in the pitch.
4. Everyone: rehearse the live twist on 10 accounts (E7), including 20176 (pensioner) and 56072 (16-year-old owner).
5. 8 PM hard deadline: Devpost draft + Tangerine track.
