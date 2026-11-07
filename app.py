"""Runway: a financial resilience engine (Sheridan Datathon 2026, Tangerine track).

Run:  streamlit run app.py
This file only wires things together: sidebar, shared context, tabs. Each tab lives in ui/pages/.
"""
import numpy as np
import streamlit as st

from ui import style
from ui.context import build_context
from ui.data import ASOF, ai_backend, load_all
from ui.pages import evidence, know, plan, shock, watchlist
from ui.state import init_state, scenario

st.set_page_config(page_title="Runway · resilience engine", page_icon="🍊", layout="wide")
style.apply()

d, people, EV, ACCOUNTS = load_all()
BACKEND = ai_backend()
init_state(ACCOUNTS[0])

with st.sidebar:
    st.markdown("## 🍊 Runway")
    st.caption("How long can this customer last, and what should they do about it?")
    if st.button("Random customer", width="stretch"):
        st.session_state.acct = int(np.random.choice(ACCOUNTS))
    acct = st.number_input("account_id", min_value=int(ACCOUNTS[0]), max_value=int(ACCOUNTS[-1]), step=1, key="acct")
    st.selectbox("Time Machine: view the warning signals as of", list(ASOF.keys()), key="asof_label",
                 help="Rewind the trough indicator and watchlist to an earlier date, then reveal what happened next.")
    st.divider()
    st.markdown(f"<span class='muted'>AI: {BACKEND}</span>", unsafe_allow_html=True)
    st.markdown("<span class='muted'>All numbers come from the engine. AI only reads twist cards and writes the plan; "
                "its numbers are checked before they're shown.</span>", unsafe_allow_html=True)

if acct not in set(ACCOUNTS):
    st.error(f"account_id {acct} isn't in the data. Try {ACCOUNTS[0]} or use Random customer.")
    st.stop()

asof = ASOF[st.session_state.asof_label]
if asof and not (d["monthly"].account_id == acct).loc[d["monthly"].month <= asof].any():
    st.warning(f"account_id {acct} has no activity up to {asof}. Pick another customer or switch the Time Machine to Today.")
    st.stop()

c = build_context(d, people, EV, ACCOUNTS, acct, asof, scenario())

st.markdown(f"### Customer {acct}" + (f" <span class='muted'>· owner aged {c.age}</span>" if c.age else ""), unsafe_allow_html=True)
if c.flags:
    st.markdown(style.flags_html(c.flags), unsafe_allow_html=True)

tabs = st.tabs(["Watchlist", "1 · Know the customer", "2 · Take a shock", "3 · Make a plan", "Why trust it"])
for tab, page in zip(tabs, [watchlist, know, shock, plan, evidence]):
    with tab:
        page.render(c)
