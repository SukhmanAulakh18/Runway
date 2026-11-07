"""Why trust it tab: every finding from evidence.json, with intervals, caveats and limits.

Owner: see docs/TASKS.md. Rule: this file only displays. Every number comes from engine.py (via the context `c`).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ai
import engine as E
from ui.data import pcurve, trough_table, wl
from ui.state import open_from_watchlist, preset, read_card, reset
from ui.style import INK, ORANGE, PAPER, SLATE


def render(c):
    """Draw this tab. `c` is the shared Context built in ui/context.py."""
    d, EV, acct, p, r, sc = c.d, c.EV, c.acct, c.p, c.r, c.sc
    key_res, real_res, a_rows, lt, LR, ASOF_VAL, ACCOUNTS, sim = (
        c.key_res, c.real_res, c.a_rows, c.lt, c.LR, c.asof, c.accounts, c.sim)
    if not EV or "trough" not in EV:
        st.warning("Run `python evidence.py` to generate evidence.json.")
    else:
        T, mi, ei, oot = EV["trough"], EV["mislabel"], EV["ei_cap"], EV["out_of_time"]
        y25 = T["by_year"][-1]
        st.markdown("#### 1. Healthy on average, fragile at the low point")
        st.markdown(f"Among {y25['accounts']:,} accounts that had **never** gone below zero, the 10% with the lowest Liquidity Trough Ratio "
                    f"had a first overdraft in 2025 **{y25['low10_rate']:.1%}** of the time ({y25['low10_events']} of {y25['low10_n']}), "
                    f"versus **{y25['rest_rate']:.2%}** for everyone else: **{y25['risk_ratio']:.1f}× the risk** "
                    f"(95% CI {y25['rr_ci95'][0]:.1f}–{y25['rr_ci95'][1]:.1f}).")
        st.dataframe(pd.DataFrame([{"Predicting": r_["predicted_year"], "Accounts": r_["accounts"], "First overdrafts": r_["new_overdrafts"],
                                    "AUC": round(r_["auc"], 3), "Riskiest 10%": f"{r_['low10_rate']:.1%}", "Everyone else": f"{r_['rest_rate']:.2%}",
                                    "Risk ratio": f"{r_['risk_ratio']:.1f}×"} for r_ in T["by_year"]]), hide_index=True)
        st.caption(f"Same result in three separate years. 2025 AUC 95% CI {T['ltr_auc_2025_ci95'][0]:.3f}–{T['ltr_auc_2025_ci95'][1]:.3f}; "
                   "window of 3 / 6 / 12 months gives AUC " + " / ".join(f"{x['auc']:.3f}" for x in T["sensitivity_window"]) + ".")
        ex = T["example_93172"]
        st.markdown(f"**Example, account 93172:** in September 2024 its balance dipped to ${ex['lowest_balance']:,.0f} while its July–December average was "
                    f"${ex['avg_balance_jul_dec_2024']:,.0f} (ratio {ex['ltr']:.1%}); the standard runway said no shortfall. On December 6 the bank granted a "
                    f"$166,958 loan at $4,638/month, about 1.5× its typical monthly money in. January 2025: {ex['jan_2025_days_below_zero']} days below zero; "
                    f"February: {ex['feb_2025_days_below_zero']}. The loan is now in debt (status D). Try it: Time Machine → Dec 2024 → 93172.")
        if "loans" in EV:
            Lo = EV["loans"]; ps = Lo["pre_loan_signal"]
            st.markdown("#### Overdraft is the line between repaid and defaulted loans")
            st.markdown(f"All **{Lo['overdrawn_and_defaulted']} of {Lo['overdrawn_borrowers']}** borrowers who were ever overdrawn defaulted; "
                        f"**{Lo['never_overdrawn_defaulted']} of {Lo['never_overdrawn_borrowers']}** who never were did. "
                        f"**{Lo['pre_loan_overdrawn']} loans** (${Lo['pre_loan_overdrawn_amount'] / 1e6:.2f}M) went to customers who were *already* overdrawn: "
                        f"all {Lo['pre_loan_overdrawn_defaulted']} defaulted, against {Lo['others_defaulted']} of {Lo['others']} other loans "
                        f"(Fisher exact p = {Lo['fisher_p']:.1e}). {Lo['no_loan_overdrawn']} customers without a loan have also been overdrawn, "
                        f"{Lo['no_loan_overdrawn_2025']} of them in 2025.")
            st.markdown(f"**Measured before the loan existed:** among {ps['loans']} borrowers never overdrawn before their loan, the trough ratio "
                        f"from the 6 months before the loan predicts default (AUC {ps['auc_pre_loan_trough']:.3f}). The lowest 20% defaulted "
                        f"{ps['low20_trough_default']:.1%} of the time ({ps['low20_defaults']} of {ps['low20_n']}) vs {ps['rest_default']:.1%} for the rest.")
            st.caption("Caveat: status D means 'running, client in debt', so part of the overdraft–default link is definitional. "
                       "It also holds for every finished-unpaid (B) loan, the 27 pre-loan overdrafts happened before the loan existed, "
                       "and the pre-loan trough uses only data from before the loan. With 76 defaults, '100%' means every case in this data, not a law.")
        if "formula_holes" in EV:
            fh = EV["formula_holes"]
            st.markdown("#### Where the standard formula misleads")
            st.markdown(f"- **EI never ends in the formula.** It says {fh['ei_forever']['survive12_formula']:.0%} of customers last a year after a layoff; "
                        f"with EI stopping at 6 months it's {fh['ei_forever']['survive12_ei_stops_6']:.0%}, and {fh['ei_forever']['flip_from_no_shortfall']} customers "
                        f"flip from 'no shortfall' to running out.\n"
                        f"- **It lays off retirees.** {fh['pensioners']['accounts']} accounts ({fh['pensioners']['share']:.0%}) live on pensions "
                        f"(owners all {fh['pensioners']['min_owner_age']:.0f}+, pension ≈ {fh['pensioners']['median_pension_share']:.0%} of money in); the formula still cuts them to 55%.\n"
                        f"- **Medians hide bad months:** a typical customer's 90th-percentile month of money out is {fh['bad_month_ratio_p90_over_median']:.1f}× their median month.\n"
                        f"- **Data limits:** {fh['cash_over_80pct_share']:.0%} of accounts get over 80% of money in as cash; {fh['minors']} owners are under 18; "
                        f"{fh['stale_accounts']} accounts have no activity in the final months; district unemployment for 2022 and 2023 correlates "
                        f"{fh['district_unemployment_corr_2022_2023']:.2f}, so we don't use it to size Canadian shocks.")
        st.markdown("#### 2. Head to head on the same customers (first overdrafts in 2025)")
        st.dataframe(pd.DataFrame({"Measure": list(T["head_to_head_2025"].keys()), "AUC": [round(v, 3) for v in T["head_to_head_2025"].values()]}), hide_index=True)
        st.caption("The runway answers 'how long under a shock'; the trough answers 'who is fragile right now'. Runway shows both.")
        ns = T["no_shock_vs_shock"]
        st.markdown("#### 3. Why median vs average depends on the question")
        st.markdown(f"With **no shock**, almost every account shows 'no shortfall', so neither runway can rank anyone (AUC {ns['median_no_shock']:.3f} median, "
                    f"{ns['mean_no_shock']:.3f} average). Under the **EI stress test**, the average-based runway ranks better ({ns['mean_ei_shock']:.3f} vs "
                    f"{ns['median_ei_shock']:.3f}). Medians also flag {mi['flagged_deficit']:,} accounts ({mi['flagged_share']:.0%}) as having more going out than coming in; "
                    f"for {mi['flagged_actually_net_positive']:.1%} of them more came in than went out on average, and {mi['flagged_balance_grew']:.0%} ended with a higher balance.")
        st.markdown("#### 4. The real 2026 EI cap")
        st.markdown(f"EI pays 55% up to $729/week (about ${ei['ei_monthly_max']:,.0f}/month). For **{ei['capped_share']:.0%}** of accounts 55% of money in exceeds the cap; "
                    f"their median runway after a job loss falls from **{ei['capped_median_runway_card']} to {ei['capped_median_runway_real']} months**.")
        st.markdown("#### Limits we know about")
        st.markdown("- Anonymised PKDD'99 Czech bank data, re-dated to 2020–2025 and converted to CAD; not real Tangerine customers.\n"
                    "- Most money moves as cash, so 'money in' isn't pay and 'money out' isn't spending; purposes are unlabelled for about half of transactions.\n"
                    "- Overdraft is the only distress outcome with dates; loan defaults have no event timing, so we don't predict them.\n"
                    "- The trough is partly mechanical (accounts near zero cross it more easily). Its value is spotting accounts the average and the standard runway call healthy.\n"
                    "- EI uses insurable earnings; the pay-share slider makes that assumption explicit.")
