# Runway: a liquidity early warning for Tangerine (Devpost write-up draft)

Every number below is recomputed from the raw data by `python evidence.py` (see `evidence.json`).

## The question
Banks judge a customer's resilience by averages: average balance, months of runway. But overdrafts don't happen
at the average; they happen at the low point of the month. **Who is about to have their first overdraft even though
they look fine on average, why, and what should the bank do about it?**

## Who it's for
A bank's customer-care and risk advisors. The customer benefits: they get a cushion offered *before* their first
overdraft instead of a fee after it.

## What we built
Runway is an engine plus an advisor dashboard (React, FastAPI, Python; Streamlit backup):
1. **Know the customer:** the judges' exact numbers (I, S, B, H, F, P, runway), our realistic numbers, and the
   **liquidity trough**: lowest balance ÷ average balance over 6 months.
2. **Take a shock:** a twist card in plain English → shock settings shown as chips → the judges' runway, our
   realistic runway (EI capped at $729/week and stopping after 6 months, pensions kept, in-month dip respected), and a
   **calibrated Monte Carlo** (2,000 futures built from the customer's own months).
3. **Diagnose, then act:** for each customer the engine names the cause, most urgent first, and the action that fits it,
   sized from their own numbers: already overdrawn → a recovery plan; **money in falling → call first** (income check, EI,
   payment holiday); a heavy new loan → a loan review (payment date or a longer term); big swings → auto-save good months;
   and always a **cushion sized to their own dip** (overdraft protection or an auto-transfer) with a personal alert.
4. **Make a plan:** that first action, the cushion, the smallest monthly cuts that avoid overdraft (a linear program), and
   backup actions ranked by months gained.
5. **A verdict for every twist:** "Yes / No / Only on paper / Fragile", the biggest reason in months (each realistic
   choice flipped back to the standard assumption), and the simulated range of when money runs out. "Fragile" catches
   customers the averages call safe but whose usable savings are so thin that most simulated futures fail.
6. **AI that never calculates:** Gemini (on Google Cloud Vertex AI) reads twist cards, briefs the advisor with the first action, and drafts a message to the customer in
   **English or French**. Every number it writes is checked against the engine; otherwise a template is used. A hard
   time limit means the demo can't stall.

## What we found
1. **The low point predicts first overdrafts.** Flag the 10% with the lowest trough and you catch **34 of 55 (62%)**
   first overdrafts in 2025, tested on data the model never saw. The flagged group's risk is **12.8–17.9×** everyone
   else's, in **each of 2023, 2024 and 2025** (AUC 0.84–0.86). It survives controls for balance size, account age and
   unemployment (**odds ratio 16.8, 95% CI 9.5–29.7**) and multiple-testing correction (**37 of 45** ideas tested survive).
2. **Customers steer back, which is why naive simulations fail.** After a month at their own low, money in beats money
   out the next month **36 percentage points more often** than after a normal month; with the same months in random
   order it is only **18 points**. **87–91% of customers** show it, in both years. A simulation that replays months randomly can't steer back: it predicted **15%** would go overdrawn
   when **1.6%** did. Calibrated on 2024 and checked on 2025, ours predicts **1.6% vs 1.6%** (AUC 0.88, Brier 0.0142 vs 0.0158 for the base rate).
3. **The fix is cheap.** A cushion sized to each flagged customer's own typical dip fully covers **27 of 34** caught
   first overdrafts, and only **$78K of $2.9M** in limits is ever used. A personal alert warns **23 of 34** a median
   **3 months early** (a $100 alert: 1 of 34), pinging only 22% of flagged customers who never needed it.
4. **The riskiest aren't poor; they're running hot.** The flagged 10% bring in a median **$16,809 a month vs $7,322**,
   carry a loan **37% vs 13%** of the time, and are almost never pensioners (**0.3% vs 20%**). Where they live, district
   salaries and joint accounts make no difference (tested and corrected for multiple comparisons).
5. **A first overdraft is a warning for the next one.** Customers overdrawn in one year were overdrawn again the next
   **47% (2024) and 60% (2025)** of the time, vs **1.6–1.8%** for everyone else.
6. **The cause decides the action, and one cause hides in plain sight.** Inside the flagged 10%, customers whose money
   in fell 25%+ overdrew **20% vs 8%** of other flagged customers in 2025 (same direction in 2024, too few to be sure),
   so they are called first. Adding these reasons to the score did **not** catch more (33 vs 34 of 55), so they choose
   the action rather than replace the score. And a loan granted in the last 12 months is invisible to any runway built on
   past spending: **186** customers at Dec 2024. Our demo customer 93172 got a **$166,958** loan the same month her
   balance hit $238; counting its **$4,638/month** payment drops her realistic runway from **26.7 to 2.4 months**.
7. **Why a lender cares:** every one of the **76** borrowers who was ever overdrawn defaulted; **27** loans
   ($3.48M) went to customers already overdrawn, and all 27 defaulted.
8. **Where the standard formula misleads:** it pays EI forever (39% "last a year" vs 22% if EI stops at 6 months),
   cuts pensions in a layoff (740 pensioners), ignores the EI cap (57% of customers), and its medians call 1,181
   customers deficit-spenders when 97.5% of them actually end up with more money.

## What we don't claim (said first)
- The trough and the plain lowest balance are statistically tied; our claim is that **the low point beats both runway
  formulas**.
- Weak steering predicted overdrafts within the riskiest 10% in 2025 but not 2024: reported, not claimed.
- "Bills leave before the main deposit" was our idea for a "move the bill date" product. It was **protective**
  (0.4–0.5% vs 2.2% overdrew), so we dropped the product. A combined model didn't beat the trough, so we didn't ship it.
- Re-dated 1990s Czech bank data, not real Tangerine customers. Most money in is cash, so a job loss assumes all
  non-pension money in stops (a slider shows this assumption). Loan status D is partly "in debt" by definition.
  This is an early-warning signal, not a cause.

## Sources
- PKDD'99 Discovery Challenge Financial dataset (real anonymized bank data), CTU Prague Relational Dataset Repository:
  https://relational.fel.cvut.cz/dataset/Financial
- Employment Insurance regular benefits (55%, weekly maximum): https://www.canada.ca/en/services/benefits/ei/ei-regular-benefit.html
- EI 2026 maximum weekly benefit ($729) from canada.ca (EI regular benefits page above)
- Google Gemini (gemini-3.5-flash) on Google Cloud Vertex AI: https://cloud.google.com/vertex-ai
