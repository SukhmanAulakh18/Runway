"""Take a shock tab: twist-card reader, presets, sliders, both runways, why they differ, Monte Carlo fan chart.

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
    left, right = st.columns([1, 1.25])
    with left:
        st.text_area("Read a twist card", key="card_text", height=90,
                     placeholder="e.g. They lose their job (EI at 55%) and their household bills go up 15% in the same month.")
        b1, b2 = st.columns(2)
        b1.button("Read card", on_click=read_card, type="primary", width="stretch")
        b2.button("Reset", on_click=reset, width="stretch")
        st.caption("Presets")
        pc = st.columns(3)
        pc[0].button("Laid off, EI 55%, 6 mo", on_click=preset, args=("This customer was laid off. EI pays 55% of their usual income for 6 months.",), width="stretch")
        pc[1].button("Furnace: 1 mo spending", on_click=preset, args=("The furnace dies, and the repair costs a full month of their typical spending.",), width="stretch")
        pc[2].button("Job loss + bills 15%", on_click=preset, args=("They lose their job (EI at 55%) and their household bills go up 15% in the same month.",), width="stretch")
        if st.session_state.parsed:
            s, source, _ = st.session_state.parsed
            chips = []
            if s["job_loss"]:
                chips.append(f"Job loss · EI {s['ei_rate']:.0%} for {s['ei_months']} months")
            if s["return_to_work_month"]:
                chips.append(f"New job in month {s['return_to_work_month']}")
            if s["income_cut"]:
                chips.append(f"Income −{s['income_cut']:.0%}")
            if s["bills_increase_pct"]:
                chips.append(f"Bills +{s['bills_increase_pct']:.0%}")
            if s["spending_increase"]:
                chips.append(f"Spending +${s['spending_increase']:,.0f}/mo")
            if s["one_off_cost"]:
                chips.append(f"One-off ${s['one_off_cost']:,.0f}")
            if s["one_off_months_of_spending"]:
                chips.append(f"One-off = {s['one_off_months_of_spending']:g} mo of spending")
            st.markdown(f"<span class='muted'>Understood ({source}):</span> " + "".join(f"<span class='chip'>{c}</span>" for c in chips or ["no shock found"]),
                        unsafe_allow_html=True)
        with st.expander("Adjust the shock", expanded=True):
            st.toggle("Job loss", key="job_loss")
            cc = st.columns(2)
            cc[0].slider("EI pays (% of usual income)", 0, 100, key="ei_rate", disabled=not st.session_state.job_loss)
            cc[1].slider("EI lasts (months)", 0, 12, key="ei_months", disabled=not st.session_state.job_loss)
            cc = st.columns(2)
            cc[0].toggle("Apply 2026 EI cap ($729/wk)", key="ei_cap", disabled=not st.session_state.job_loss)
            cc[1].number_input("New job in month (0 = none)", 0, 24, key="rtw", disabled=not st.session_state.job_loss)
            st.slider("Share of non-pension inflows that is pay (assumption)", 0, 100, key="emp_share",
                      disabled=not st.session_state.job_loss,
                      help="Most money in here is cash deposits and transfers; we can't see which part is wages.")
            st.slider("Pay cut without job loss (%)", 0, 100, key="income_cut", disabled=st.session_state.job_loss)
            st.slider("Household bills / rent up (%)", 0, 100, key="bills_pct")
            cc = st.columns(2)
            cc[0].number_input("Extra monthly spending ($)", -20000, 20000, step=50, key="spend_inc")
            cc[1].number_input("One-off cost ($)", 0, 500000, step=100, key="one_off")
            st.slider("One-off cost in months of typical spending", 0.0, 6.0, step=0.5, key="one_off_months")
    with right:
        c1, c2 = st.columns(2)
        c1.markdown("<div class='card'><div class='muted'>Standard (answer key)</div>"
                    f"<div class='big key'>{key_res['label']}</div>"
                    f"<div class='muted'>income ${key_res['income_after']:,.0f} · spending ${key_res['spending_after']:,.0f}"
                    f"<br>buffer left ${key_res['buffer_left']:,.0f}</div></div>", unsafe_allow_html=True)
        c2.markdown("<div class='card'><div class='muted'>Realistic (Runway)</div>"
                    f"<div class='big real'>{real_res['label']}</div>"
                    f"<div class='muted'>income ${real_res['income_after']:,.0f} · spending ${real_res['spending_after']:,.0f}"
                    f"<br>usable buffer ${real_res['usable_buffer']:,.0f}</div></div>", unsafe_allow_html=True)
        reasons = E.explain_difference(p, r, sc)
        if reasons:
            st.markdown("**Why the two numbers differ**")
            for x in reasons:
                st.markdown(f"- {x}")
        if sim["insufficient_history"]:
            st.warning(f"Only {sim['history_months']} months of history: treat the simulation as rough.")
        st.markdown(f"**Chance they make it 6 months: {sim['p_survive_6']:.0%}** · 12 months: {sim['p_survive_12']:.0%}"
                    f"  <span class='muted'>({sim['n_paths']:,} simulations replaying their own last {sim['history_months']} months)</span>",
                    unsafe_allow_html=True)
        f = go.Figure()
        f.add_trace(go.Scatter(x=sim["months"], y=sim["p90"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
        f.add_trace(go.Scatter(x=sim["months"], y=sim["p10"], fill="tonexty", fillcolor="rgba(232,111,0,0.18)",
                               line=dict(width=0), name="80% of outcomes"))
        f.add_trace(go.Scatter(x=sim["months"], y=sim["p50"], line=dict(color=ORANGE, width=3), name="Typical path"))
        f.add_hline(y=sim["dip"], line_dash="dot", line_color=SLATE, annotation_text="overdraft risk zone (typical dip)")
        f.add_hline(y=0, line_color="#c43d3d", line_width=1)
        if st.session_state.job_loss and st.session_state.ei_months:
            f.add_vline(x=st.session_state.ei_months + 0.5, line_dash="dash", line_color=INK, annotation_text="EI ends")
        f.update_layout(title="Month-by-month balance after the shock", height=360, margin=dict(l=10, r=10, t=50, b=10),
                        plot_bgcolor="white", yaxis_tickprefix="$", xaxis_title="Months after the shock",
                        legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(f, width="stretch")
        st.caption(f"Bank's view (like a credit-exposure profile): expected overdraft at month 6 ${sim['ee'][5]:,.0f}; "
                   f"in the worst 5% of outcomes ${sim['pfe95'][5]:,.0f} or more.")
