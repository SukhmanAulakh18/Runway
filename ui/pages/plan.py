"""Make a plan tab: goal milestones, backup levers, optimised cut schedule, AI-written plan with number check.

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
    plan = E.make_plan(acct, d, sc)
    g = plan["goal"]
    levers = plan["backup"]["levers"]
    st.markdown("#### Goal plan: build a cushion for a job loss on EI")
    st.caption(f"Monthly shortfall if they lost their job today (capped EI, pension kept): ${g['monthly_gap_on_ei']:,.0f}. "
               f"Saved now: ${g['have']:,.0f}.")
    rows = []
    for m in g["milestones"]:
        prog = min(g["have"] / m["target"], 1.0) if m["target"] > 0 else 1.0
        rows.append({"Milestone": m["name"], "Target": m["target"], "Still needed": m["need"], "Progress": prog,
                     "Months (save half your surplus)": "done" if m["done"] else ("-" if m["months_steady"] is None else f"{m['months_steady']:.0f}"),
                     "Months (+10% cut)": "done" if m["done"] else ("-" if m["months_stretch"] is None else f"{m['months_stretch']:.0f}")})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch",
                 column_config={"Target": st.column_config.NumberColumn(format="$%.0f"),
                                "Still needed": st.column_config.NumberColumn(format="$%.0f"),
                                "Progress": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.0f%%")})
    if g["deficit_to_close"] > 0:
        st.info(f"Recently ${g['deficit_to_close']:,.0f}/month more has gone out than come in on average. "
                "Step one is closing that gap; the stretch column assumes a 10% cut to unlabelled outflows.")
    st.markdown("#### Backup plan: if the shock hits")
    st.caption(f"Realistic runway under this shock: {plan['backup']['base_runway']} months")
    if levers:
        lv = pd.DataFrame(levers)
        fl = go.Figure(go.Bar(y=lv.action, x=lv.runway, orientation="h", marker_color=[SLATE] + [ORANGE] * (len(lv) - 1)
                              if lv.action.iloc[0].startswith("Apply") else ORANGE,
                              text=[f"{x} mo" for x in lv.runway], textposition="outside"))
        fl.update_layout(title="Runway after each action", height=60 + 45 * len(lv), margin=dict(l=10, r=40, t=40, b=10),
                         plot_bgcolor="white", xaxis_title="months", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fl, width="stretch")
    st.markdown("#### Optimised plan: the smallest monthly cuts that keep them out of overdraft")
    oc = st.columns(2)
    bad = oc[0].radio("Plan for", ["a bad outcome (10th percentile)", "a typical outcome (median)"], key="opt_outcome", horizontal=True) .startswith("a bad")
    cap = oc[1].slider("Most we'd ask them to cut (% of unlabelled outflows + loan payment)", 10, 100, 50, step=10, key="opt_cap")
    opt = E.optimize_cuts(acct, d, sc, max_cut_share=cap / 100, pessimistic=bad)
    if opt["protected_months"] > opt["base_months"]:
        st.success(f"Without changes they stay out of overdraft for **{opt['base_months']} months** in {opt['outcome']}. "
                   f"With the optimised cuts: **{opt['protected_months']} months**, averaging **${opt['avg_monthly_cut']:,.0f}/month**.")
    elif opt["base_months"] >= opt["horizon"]:
        st.success(f"No cuts needed: they stay out of overdraft for all {opt['horizon']} months in {opt['outcome']}.")
    else:
        st.warning(f"In {opt['outcome']}, cuts of up to ${opt['max_monthly_cut']:,.0f}/month can't protect month "
                   f"{opt['base_months'] + 1}. They need a bridge first: claim EI immediately, ask the lender about a deferral, "
                   "or arrange overdraft protection before the shock.")
    if opt["cuts"]:
        fo = go.Figure()
        mths = list(range(1, len(opt["path"]) + 1))
        fo.add_trace(go.Scatter(x=mths, y=opt["path"], name="Without changes", line=dict(color=SLATE, dash="dot")))
        fo.add_trace(go.Scatter(x=list(range(1, len(opt["protected_path"]) + 1)), y=opt["protected_path"], name="With optimised cuts", line=dict(color=ORANGE, width=3)))
        fo.add_trace(go.Bar(x=list(range(1, len(opt["cuts"]) + 1)), y=opt["cuts"], name="Cut that month", marker_color="rgba(232,111,0,0.35)"))
        fo.add_hline(y=opt["dip"], line_dash="dot", line_color="#c43d3d", annotation_text="overdraft line (typical dip)")
        fo.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white", yaxis_tickprefix="$",
                         xaxis_title="Months after the shock", legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fo, width="stretch")
    st.caption("Linear program (scipy HiGHS): minimise total cuts subject to the projected balance staying above the overdraft line "
               "each month; bills and insurance are never cut. Re-solved every month with new data, it's a receding-horizon plan.")
    best = max([l for l in levers if l.get("gain")], key=lambda l: l["gain"], default=None)
    nxt = next((m for m in g["milestones"] if not m["done"]), None)
    facts = {"realistic_runway": real_res["label"], "answer_key_runway": key_res["label"],
             "next_milestone": ({"name": nxt["name"], "need": round(nxt["need"]),
                                 "months": round(nxt["months_stretch"] or nxt["months_steady"] or 0) or None} if nxt else None),
             "saving": round(g["stretch_saving"]), "best_lever": ({"action": best["action"], "runway": best["runway"]} if best else None),
             "chance_6_months_pct": round(sim["p_survive_6"] * 100),
             "optimised_plan": {"months_safe_without_changes": opt["base_months"], "months_safe_with_cuts": opt["protected_months"],
                                "average_monthly_cut": round(opt["avg_monthly_cut"])}}
    if st.button("Write the plan for the customer", type="primary"):
        text, source = ai.write_plan(facts)
        st.session_state.plan_text = (acct, text, source)
    if st.session_state.get("plan_text") and st.session_state.plan_text[0] == acct:
        _, text, source = st.session_state.plan_text
        st.markdown(f"<div class='card'>{text}<div class='muted' style='margin-top:8px'>Written by: {source}</div></div>",
                    unsafe_allow_html=True)
