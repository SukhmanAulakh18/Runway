"""Widget state and callbacks. Programmatic widget changes must happen in callbacks (before widgets are drawn)."""
import streamlit as st

import ai
import engine as E

DEFAULTS = dict(job_loss=False, ei_rate=55, ei_months=6, ei_cap=True, rtw=0, income_cut=0,
                bills_pct=0, spend_inc=0, one_off=0, one_off_months=0.0, emp_share=100)


def init_state(first_account: int):
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)
    st.session_state.setdefault("parsed", None)
    st.session_state.setdefault("acct", first_account)
    st.session_state.setdefault("asof_label", "Today (Dec 2025)")


def apply_settings(s: dict, source: str, text: str):
    st.session_state.update(job_loss=s["job_loss"], ei_rate=int(round(s["ei_rate"] * 100)), ei_months=s["ei_months"],
                            rtw=s["return_to_work_month"] or 0, income_cut=int(round(s["income_cut"] * 100)),
                            bills_pct=int(round(s["bills_increase_pct"] * 100)), spend_inc=int(s["spending_increase"]),
                            one_off=int(s["one_off_cost"]), one_off_months=float(s["one_off_months_of_spending"]))
    st.session_state.parsed = (s, source, text)


def read_card():
    text = st.session_state.get("card_text", "").strip()
    if text:
        s, source = ai.parse_twist(text)
        apply_settings(s, source, text)


def preset(text):
    st.session_state.card_text = text
    read_card()


def reset():
    st.session_state.update(DEFAULTS)
    st.session_state.parsed = None


def open_from_watchlist():
    sel = st.session_state.get("wl_table")
    rows = sel.selection.rows if sel is not None else []
    if rows:
        st.session_state.acct = int(st.session_state.wl_ids[rows[0]])


def scenario() -> E.Scenario:
    ss = st.session_state
    return E.Scenario(job_loss=ss.job_loss, ei_rate=ss.ei_rate / 100, ei_months=int(ss.ei_months), ei_cap=ss.ei_cap,
                      income_cut=ss.income_cut / 100, bills_increase_pct=ss.bills_pct / 100,
                      spending_increase=float(ss.spend_inc), one_off_cost=float(ss.one_off),
                      one_off_months_of_spending=float(ss.one_off_months),
                      return_to_work_month=(int(ss.rtw) if ss.rtw else None), employment_share=ss.emp_share / 100)
