# Handoff: review, decisions and next fixes (Sat Nov 7, 5 PM)

Read this before starting any task. It records what a full review of the repo found, what the team decided, and what's left. Every number below was re-run on the real data.

## Verified (don't re-check)
- `pytest -q`: 57 passed. `pytest -q -m ui`: 6 passed.
- Answer key matches the README: account 20111 → **3.4** (job loss EI 55%), **4.0** (furnace), **3.4** (job loss + bills 15%).
- Trough finding: 14.6× risk (2025), AUC 0.841 / 0.844 / 0.860 over three years.
- Confounder check (E4): adjusted odds ratio **16.8** (95% CI 9.5–29.7) after balance size, account age, district unemployment.
- BH correction (E3): **28 of 29** tests survive at q = 0.10.
- Overdraft → default: 76 of 76; 27 loans granted while already overdrawn, all defaulted (Fisher p = 1.6e-28).
- EI 2026: 55% up to **$729/week** (max insurable earnings $68,900), up to 45 weeks. Source: canada.ca.
- Speed: simulate ~10 ms, optimize_cuts ~0.3 s. No need for C++.

## Decisions
1. **React frontend is approved, Streamlit stays as the backup.** Plan: `docs/REACT_PLAN.md`. React talks to `api.py` (FastAPI). Neither React nor `api.py` computes money.
2. **Midnight go/no-go:** React must run the full live twist on 5 accounts with zero errors, or we demo Streamlit.
3. **No C++, no new AI backends** (no IBM, Lovable, Backboard). Gemini via Vertex AI only (Google Cloud credits claimed). ElevenLabs only for the video voiceover.
4. **Deploy:** Cloud Run, one container (FastAPI also serves the built React files), Sunday morning.

## Must fix (judges will see these)
| # | Bug | Owner | Fix |
|---|---|---|---|
| 1 | **Time Machine lookahead.** In Dec 2024 mode only the trough rewinds; runway cards, simulation and plan use data through Dec 2025. 93172 shows 6.6 months instead of "no shortfall" (the pitch line). | P1 | Streamlit: in `ui/context.py`, when `asof` is set, pass `{"monthly": d["monthly"][month <= asof], "loans": d["loans"]}` to profile / realistic_profile / simulate / make_plan / optimize_cuts / loan_risk. `api.py` already does this. |
| 2 | **Kalman chart band is ±$67M in month 1** (diffuse start), which squashes the chart. q also hits the grid floor (1e-5) for most accounts, which means "no trend". | P2 (`know.py`) | Skip the first 2 months when drawing the band. If `q <= 1e-5`, caption "No trend: month-to-month swings are noise around ~$X a month" instead of calling it a signal. Or drop the chart from the demo. |
| 3 | **Pitch claim that didn't survive our own BH test:** "trough beats raw lowest balance (0.860 vs 0.840)". | Everyone | Remove from pitch, Q&A, FINDINGS. Say instead: "It catches people the runway calls healthy; it survives correction across 28 tests and adjustment for balance size." |

## Should fix
| # | Issue | Owner | Fix |
|---|---|---|---|
| 4 | Realistic runway and Monte Carlo disagree (20111 job loss: realistic 1.3 months, simulation median month 3, 15% make 6 months). Realistic uses a 12-month window; simulate replays 24. | P1 | Same window for both, then make the simulation the headline and call the deterministic number "simple estimate". |
| 5 | Trough is a rank, not a probability. | P1 | Logistic fit: trough → P(first overdraft in next 12 months), trained 2023→2024, validated 2025, with Brier score + calibration bars. Card then says "X% chance of first overdraft in 12 months". |
| 6 | Gemini output not schema-constrained. | P3 | Pass `response_schema` with the field types in `parse_twist`. |
| 7 | Every page imports unused modules (ai, pcurve, preset, ...). | page owners | Clean before the repo goes public. |
| 8 | Know tab too dense for a 5-second read. | P2 | Summary sentence first (F2), one chart visible, rest in an expander; chart titles state the takeaway (F4). |

## New files from this review
- `api.py` / `openapi.json`: drafted and tested, but **held back from the repo** until frontend work starts (see `docs/FRONTEND.md`).
- `docs/REACT_PLAN.md`: stack, screens, owners, timeline.

## Pitch order
1. 93172 in the Time Machine (Dec 2024): averaged $18.5K, standard runway "no shortfall", but dipped to $238; flagged riskiest 2%; overdrawn 13 days in January.
2. 14.6× across three years; survives controls (OR 16.8) and multiple-testing correction.
3. Overdrafts matter: 76 of 76 overdrawn borrowers defaulted; 27 loans ($3.5M) went to already-overdrawn customers, all defaulted.
4. "Pick any account and any twist."

Limits to say first: 1990s Czech data re-dated (not Tangerine customers); money in ≠ pay (mostly cash); status D is partly "in debt" by definition; it's an early-warning signal, not causal.

## Log (newest last; one line per merged change, both lanes)
| Date | Lane | Change |
|---|---|---|
| Nov 7 | engine | Time Machine lookahead fixed in Streamlit (`ui/context.py` cuts data at `asof`; `Context.d_full` only for the reveal). 93172 Dec 2024 now reads "no shortfall (120+)", trough rank 1.6%, low $238. |
| Nov 7 | engine | Monte Carlo calibration: raw sim predicted 13.5% would break in 2025 vs 1.6% actual. New `engine.calibrate_break`, `engine.overdraft_risk` (Platt, fit 2023→2024, validated 2025: Brier 0.0152 vs base 0.0158, AUC 0.863). `evidence.json` → `sim_calibration`. |
| Nov 7 | engine | Watchlist `realistic_runway_ei` now equals the Know/Shock realistic runway (EI ends after 6 months); was different on 23.5% of accounts. `net_flow_filter` adds `has_trend`, `band_from` (handoff #2). |
| Nov 7 | ai | `_sanitize` coerces `return_to_work_month` (string from an LLM crashed the simulation); Gemini twist call uses `response_schema` (handoff #6). New contract test between lanes. |
