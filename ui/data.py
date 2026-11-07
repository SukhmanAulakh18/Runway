"""Cached data loading. Everything that touches all 4,500 accounts is computed once and reused."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

import ai
import engine as E

ASOF = {"Today (Dec 2025)": None, "Dec 2024": "2024-12", "Dec 2023": "2023-12"}
ROOT = Path(__file__).resolve().parent.parent


@st.cache_resource
def load_all():
    d = E.load()
    disp = pd.read_csv(E.DATA / "dispositions.csv")
    clients = pd.read_csv(E.DATA / "clients.csv", parse_dates=["birth_date"])
    people = disp.merge(clients, on="client_id")
    ev_path = ROOT / "evidence.json"
    ev = json.loads(ev_path.read_text()) if ev_path.exists() else None
    accounts = sorted(d["monthly"].account_id.unique().tolist())
    return d, people, ev, accounts


@st.cache_resource
def ai_backend():
    return ai.init()


@st.cache_resource
def wl(asof):
    d = load_all()[0]
    dd = d if asof is None else {"monthly": d["monthly"][d["monthly"].month <= asof], "loans": d["loans"]}
    w = E.watchlist(dd)
    w["ever_negative"] = (dd["monthly"].groupby("account_id").days_below_zero.sum() > 0).reindex(w.index)
    if asof is not None:   # Time Machine reveal: did they go below zero in the next 12 months?
        nxt = d["monthly"][(d["monthly"].month > asof) & (d["monthly"].month <= f"{int(asof[:4]) + 1}-12")]
        w["overdraft_next_12m"] = (nxt.groupby("account_id").days_below_zero.sum() > 0).reindex(w.index)
    return w


@st.cache_resource
def pcurve(sc_items):
    return E.portfolio_curve(load_all()[0], E.Scenario(**dict(sc_items)))


@st.cache_resource
def trough_table(asof):
    return E.ltr_table(load_all()[0], asof=asof)


@st.cache_resource
def dip_days():
    return E.load_dip_days()   # None if transactions.csv is absent; ~5 s once
