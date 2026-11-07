"""Watchlist tab: advisor view ranked by trough ratio, Time Machine reveal, and the bank-wide view.

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
    W = wl(ASOF_VAL)
    early = st.toggle("Early warning only: hide accounts that have already gone below zero", value=True, key="wl_early")
    if early:
        W = W[~W.ever_negative]
    W = W[W.scorable]   # needs 12+ months of history, as in the validated backtest
    top = W.head(50).copy()
    st.markdown(f"#### Accounts to review first" + (f" · as of {ASOF_VAL}" if ASOF_VAL else ""))
    st.caption("Ranked by Liquidity Trough Ratio (lowest balance ÷ average balance, last 6 months). "
               "Click a row to open that customer.")
    if ASOF_VAL:
        hit = top.overdraft_next_12m.fillna(False)
        st.markdown(f"**Time Machine reveal:** of these 50 accounts, **{int(hit.sum())}** went below zero in the following 12 months, "
                    f"against {W.overdraft_next_12m.fillna(False).mean():.1%} of the {len(W):,} accounts shown in this view"
                    + (" (none had ever been below zero before)." if early else "."))
    st.session_state.wl_ids = top.index.tolist()
    show = pd.DataFrame({"account_id": top.index, "Trough ratio": top.ltr * 100, "Lowest balance": top.min_balance,
                         "Average balance": top.avg_balance, "Standard runway (EI)": top.answer_key_runway_ei,
                         "Realistic runway (EI)": top.realistic_runway_ei, "Why flagged": top.reasons})
    if ASOF_VAL:
        show["Overdraft next 12 months"] = top.overdraft_next_12m.map({True: "yes", False: "no"}).fillna("no data").values
    st.dataframe(show, hide_index=True, width="stretch", key="wl_table", on_select=open_from_watchlist,
                 selection_mode="single-row",
                 column_config={"Trough ratio": st.column_config.NumberColumn(format="%.1f%%"),
                                "Lowest balance": st.column_config.NumberColumn(format="$%.0f"),
                                "Average balance": st.column_config.NumberColumn(format="$%.0f")})
    st.markdown("#### Bank view: if the current shock hit every customer")
    pc = pcurve(tuple(sorted(sc.__dict__.items())))
    fb = go.Figure()
    fb.add_trace(go.Scatter(x=pc.month, y=pc.standard * 100, name="Standard formula", line=dict(color=SLATE, dash="dot", width=3)))
    fb.add_trace(go.Scatter(x=pc.month, y=pc.realistic * 100, name="Realistic (EI capped and ending, pension kept, dip-aware)", line=dict(color=ORANGE, width=3)))
    fb.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white", yaxis_ticksuffix="%",
                     yaxis_title="customers still above zero", xaxis_title="months after the shock", legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fb, width="stretch")
    m6 = pc[pc.month == 6].iloc[0]
    st.caption(f"Shock from the Shock tab (change it there). At 6 months the standard formula says {m6.standard:.0%} of all "
               f"{len(ACCOUNTS):,} customers are still above zero; the realistic engine says {m6.realistic:.0%}.")
