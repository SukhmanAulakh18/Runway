"""Know the customer tab: standard vs realistic runway, trough card, credit view, Time Machine reveal, charts.

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
    base_key = E.runway(p, E.Shock())
    base_real = E.realistic_runway(r, E.Scenario())
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='card'><div class='muted'>Standard (answer key)</div>"
                    f"<div class='big key'>{base_key['label']}</div><div class='muted'>runway with no shock</div></div>",
                    unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"": ["Typical money in (I)", "Fixed costs (F)", "Typical spending (S)", "Buffer (B)",
                                        "Household bills (H)", "Loan payment (P)"],
                                   "Monthly $": [p.income, p.fixed_costs, p.spending, p.buffer, p.household_bills, p.loan_payment]})
                     .style.format({"Monthly $": "${:,.0f}"}), hide_index=True, width="stretch")
    with c2:
        st.markdown("<div class='card'><div class='muted'>Realistic (Runway)</div>"
                    f"<div class='big real'>{base_real['label']}</div><div class='muted'>runway with no shock</div></div>",
                    unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"": ["Money in (12-mo average)", "  of which pension + interest", "  of which other inflows",
                                        "Money out (12-mo average)", "  labelled bills, insurance, loan, fees", "  unlabelled (purpose unknown)", "Buffer", "Typical monthly dip"],
                                   "Monthly $": [r.income, r.protected_income, r.earned_income, r.spending, r.essential,
                                                 r.flexible, r.buffer, r.dip]})
                     .style.format({"Monthly $": "${:,.0f}"}), hide_index=True, width="stretch")
    with c3:
        if lt and not lt["scorable"]:
            st.markdown("<div class='card'><div class='muted'>Liquidity trough</div>"
                        f"<div class='big key'>too new</div><div class='muted'>{lt['n_months']} months of history; scored from 12 months</div></div>",
                        unsafe_allow_html=True)
        elif lt:
            badge = "riskiest 10%" if lt["bottom_10"] else f"riskier than {100 - lt['pct_rank'] * 100:.0f}% of accounts" if lt["pct_rank"] < 0.5 else "lower risk half"
            st.markdown("<div class='card'><div class='muted'>Liquidity trough" + (f" · as of {ASOF_VAL}" if ASOF_VAL else "") + "</div>"
                        f"<div class='big real'>{lt['ltr'] * 100:.1f}%</div><div class='muted'>lowest balance ÷ average, last 6 months · {badge}</div></div>",
                        unsafe_allow_html=True)
        if lt:
            st.markdown(f"Lowest balance **${lt['min_balance']:,.0f}** against an average of **${lt['avg_balance']:,.0f}** (last 6 months).")
            if EV and "trough" in EV:
                yr = EV["trough"]["by_year"][-1]
                st.caption(f"In backtests, the riskiest 10% by this ratio had a first overdraft the next year "
                           f"{yr['low10_rate']:.1%} of the time vs {yr['rest_rate']:.2%} for everyone else ({yr['risk_ratio']:.1f}×).")
    if ASOF_VAL:
        nxt = E.what_happened_next(acct, d, ASOF_VAL, 12)
        if len(nxt):
            st.markdown(f"**Time Machine reveal: what happened after {ASOF_VAL}**")
            fr = go.Figure()
            fr.add_trace(go.Bar(x=nxt.month, y=nxt.days_below_zero, name="Days below zero", marker_color="#c43d3d", yaxis="y2", opacity=0.6))
            fr.add_trace(go.Scatter(x=nxt.month, y=nxt.min_balance, name="Lowest balance", line=dict(color=ORANGE, width=3)))
            fr.add_hline(y=0, line_color="#c43d3d", line_width=1)
            fr.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white", yaxis_tickprefix="$",
                             yaxis2=dict(overlaying="y", side="right", title="days below zero", showgrid=False),
                             legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fr, width="stretch")
    if LR:
        st.markdown("**Credit view**")
        cc = st.columns(4)
        cc[0].metric("Loan", f"${LR['amount']:,.0f}", f"granted {LR['loan_start']}", delta_color="off")
        cc[1].metric("Monthly payment", f"${LR['monthly_payment']:,.0f}",
                     (f"{LR['payment_to_money_in']:.0%} of typical money in before the loan" if LR["payment_to_money_in"] else None), delta_color="off")
        cc[2].metric("Trough before the loan", f"{LR['pre_loan_ltr'] * 100:.1f}%" if LR["pre_loan_ltr"] is not None else "n/a",
                     (f"lowest balance ${LR['pre_loan_min_balance']:,.0f}" if LR["pre_loan_min_balance"] is not None else None), delta_color="off")
        cc[3].metric("Status today", LR["status"], LR["status_meaning"], delta_color="off")
        if LR["overdrawn_before_loan"]:
            st.warning("This customer was already overdrawn before the loan was granted. In this data, all 27 such loans defaulted.")
    last24 = a_rows.tail(24)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=last24.month, y=last24.avg_daily_balance, name="Average balance", line=dict(color=INK)))
    fig.add_trace(go.Scatter(x=last24.month, y=last24.min_balance, name="Lowest balance", line=dict(color=ORANGE, dash="dot")))
    fig.add_hline(y=0, line_color="#c43d3d", line_width=1)
    fig.update_layout(title="Balance over the last 24 months: the gap between the lines is the dip",
                      height=320, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=-0.2),
                      plot_bgcolor="white", yaxis_tickprefix="$")
    st.plotly_chart(fig, width="stretch")
    kf = E.net_flow_filter(acct, d)
    lv, sd = np.array(kf["level"]), np.array(kf["sd"])
    fk = go.Figure()
    fk.add_trace(go.Bar(x=kf["month"], y=kf["net"], name="Monthly net flow (in − out)", marker_color="#d9dde5"))
    fk.add_trace(go.Scatter(x=kf["month"], y=lv + 2 * sd, line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fk.add_trace(go.Scatter(x=kf["month"], y=lv - 2 * sd, fill="tonexty", fillcolor="rgba(29,36,51,0.12)", line=dict(width=0), name="±2 s.d."))
    fk.add_trace(go.Scatter(x=kf["month"], y=lv, line=dict(color=INK, width=3), name="Underlying level (Kalman filter)"))
    fk.update_layout(title="Underlying monthly net flow: the line is the signal, the bars are the noise", height=320,
                     margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white", yaxis_tickprefix="$", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fk, width="stretch")
    drift = f"{kf['drift_sd']:+.1f} s.d. over 6 months" if kf["drift_sd"] is not None else "n/a"
    st.caption(f"Local-level Kalman filter, signal-to-noise q = {kf['q']:.2g} chosen by maximum likelihood; month-to-month noise ≈ "
               f"${kf['obs_sd']:,.0f}. Underlying level now ${lv[-1]:,.0f} ± ${2 * sd[-1]:,.0f}; drift {drift}.")
    comp = last24[["month", "cash_deposits", "transfers_in", "pension_in", "interest_in"]].set_index("month")
    fig2 = go.Figure([go.Bar(x=comp.index, y=comp[c], name=n) for c, n in
                      [("cash_deposits", "Cash deposits"), ("transfers_in", "Transfers in"), ("pension_in", "Pension"), ("interest_in", "Interest")]])
    fig2.update_layout(barmode="stack", title="Where the money comes from", height=280, margin=dict(l=10, r=10, t=50, b=10),
                       legend=dict(orientation="h", y=-0.25), plot_bgcolor="white", yaxis_tickprefix="$",
                       colorway=[INK, ORANGE, "#2f8f6b", SLATE])
    st.plotly_chart(fig2, width="stretch")
