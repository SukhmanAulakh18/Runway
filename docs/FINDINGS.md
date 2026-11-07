# What we found, in plain words

All numbers are re-created from the raw data by `python evidence.py` and shown on the app's "Why trust it" tab.

## 1. Healthy on average, close to zero at the low point (the headline)

Some customers have a good **average** balance but keep **dipping close to $0**. We measure this with the **Liquidity Trough Ratio**: lowest balance ÷ average balance, over the last 6 months.

- Among **3,417 customers who had never gone below zero**, the 10% with the lowest ratio had their **first overdraft in 2025 9.9% of the time**, against **0.68%** for everyone else: **14.6× the risk**.
- It works in **three separate years** (predicting 2023, 2024 and 2025) and with 3, 6 or 12-month windows.
- It spots first overdrafts better than either runway number. (On AUC, a ranking score where 0.5 is a coin flip: trough 0.86, our runway 0.76, the standard runway 0.69.)

## 2. An overdraft is the line between repaid and defaulted loans

- **Every** borrower who was ever overdrawn defaulted: **76 of 76**. **None** of the 606 others did.
- **27 loans ($3.48M) went to customers already overdrawn.** All 27 defaulted, versus 49 of the other 655.
- **Measured before the loan existed,** the trough still predicts default: the lowest 20% defaulted **19.5%** of the time, versus **3.2%**.
- **212 customers without a loan have been overdrawn** (122 in 2025). Nobody flags them before they ask for credit.
- *Caveat:* status D means "in debt", so part of that link is built into the definition. The before-the-loan results don't have that problem.

## 3. Where the standard runway formula misleads

- **EI never ends in the formula.** The twist card says "for 6 months", but the formula keeps paying. It says 39% of customers last a year after a layoff; with EI ending at 6 months, it's 22%.
- **It lays off retirees.** 740 customers (16%) live on pensions, yet the formula cuts their pension to 55% in a layoff.
- **EI has a cap.** It's $729 a week in 2026, so for 57% of customers EI pays less than the formula assumes.
- **Medians mislabel people.** The formula says 1,181 customers spend more than they earn; 97.5% of them actually end up with more money.
- **Bank-wide,** if a layoff with 6 months of EI hit everyone: the formula says 65% still have money at month 6; realistically it's 41%.

## 4. A trap we caught

A brand-new account's first month starts at its first deposit, which looks like a scary dip. So we only score customers with **12+ months of history**. With that rule, the Time Machine watchlist (as of Dec 2024) caught **14 first-time overdrafts in its top 50**, against a 1.7% base rate.

## The demo customer: account 93172

| When | What happened |
|---|---|
| Sep 2024 | Balance dips to **$238** while the 6-month average is **$18,503**. The standard runway says "no shortfall". |
| Dec 6, 2024 | The bank lends **$166,958** at $4,638/month, **1.5× their typical monthly money in** |
| Jan–Feb 2025 | **21 days below zero** |
| Today | The loan is **in debt** (status D) |

## Limits (we say these first)

- It's 1990s Czech bank data, re-dated and converted to CAD, not real Tangerine customers.
- Most money moves as cash, so "money in" isn't the same as pay.
- Loans have no default dates, so we don't predict *when* a loan defaults.
- The trough is partly mechanical (accounts near zero cross it more easily). Its value is catching customers that both runways call healthy.
