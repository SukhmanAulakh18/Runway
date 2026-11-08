"""Builds the shared Context for one customer: every number the pages show, computed once per click."""
from dataclasses import dataclass, field

import pandas as pd

import engine as E
from ui.data import dip_days, repeat_table, standing_orders, trough_table


@dataclass
class Context:
    d: dict
    EV: dict | None
    accounts: list
    acct: int
    asof: str | None
    p: E.Profile
    r: E.Realistic
    sc: E.Scenario
    key_res: dict
    real_res: dict
    a_rows: pd.DataFrame
    lt: dict | None
    LR: dict | None
    sim: dict
    age: int | None
    flags: list = field(default_factory=list)
    d_full: dict | None = None   # uncut data, only for the Time Machine reveal (what happened after asof)
    risk: dict | None = None     # engine.overdraft_risk: calibrated chance of a first overdraft in 12 months
    cushion: dict | None = None  # engine.cushion: buffer, personal alert level, top-up now, usual dip day
    committed: dict | None = None  # engine.committed_outflows: standing orders (today only; None when asof is set)
    repeat: dict | None = None  # engine.repeat_overdraft: overdrawn in the last 12 months -> tested repeat rate
    diagnosis: dict | None = None  # engine.diagnose: why they're at risk and the matched action, most urgent first


def build_context(d, people, EV, accounts, acct, asof, sc) -> Context:
    d_full = d
    if asof:   # Time Machine: every number uses only what the bank knew at asof (no lookahead)
        d = {"monthly": d["monthly"][d["monthly"].month <= asof], "loans": d["loans"]}
    p, r = E.profile(acct, d), E.realistic_profile(acct, d)
    a_rows = d["monthly"][d["monthly"].account_id == acct].sort_values("month")
    tt = trough_table(asof)
    lt = E.liquidity_trough(acct, d, table=tt) if acct in tt.index else None
    LR = E.loan_risk(acct, d)
    if LR and asof:   # the loan's outcome (repaid / in debt / defaulted) is end-of-2025 knowledge: hide it in the Time Machine
        LR = {**LR, "status": None, "status_meaning": "outcome hidden in Time Machine mode", "defaulted": None}
    who = people[people.account_id == acct]
    owner = who[who.type == "owner"]
    ref = pd.Timestamp(f"{asof}-28") if asof else E.END_OF_DATA
    age = int((ref - owner.birth_date.iloc[0]).days // 365.25) if len(owner) else None

    flags = []   # plain-English warnings a judge might trip over (no money is computed here)
    if LR and LR["overdrawn_before_loan"]:
        flags.append("Loan granted while already overdrawn")
    if (a_rows.days_below_zero > 0).any():
        flags.append("Has been overdrawn before")
    if lt and lt["bottom_10"]:
        flags.append("Liquidity trough in the riskiest 10%" + (f" (as of {asof})" if asof else ""))
    if p.household_bills == 0:
        flags.append("No labelled bill payments: a bills shock changes nothing in the standard formula")
    if p.buffer <= 0:
        flags.append("Savings already at or below zero")
    elif p.buffer < p.spending:
        flags.append("Less than one month of spending saved")
    if a_rows.month.max() < (asof or "2025-12"):
        flags.append(f"No activity recorded after {a_rows.month.max()}")
    if p.spending > p.income and r.income > r.spending:
        flags.append("Medians say money out > money in; averages say the opposite")
    if r.income > 0 and r.protected_income / r.income > 0.5:
        flags.append(f"{r.protected_income / r.income:.0%} of money in is pension: a layoff doesn't apply")
    if len(who) > 1:
        flags.append("Joint account (2 people)")
    if age is not None and age < 18:
        flags.append(f"Owner is {age}: job-loss and EI shocks may not apply")

    return Context(d=d, EV=EV, accounts=accounts, acct=acct, asof=asof, p=p, r=r, sc=sc,
                   key_res=E.runway(p, sc.to_answer_key_shock()), real_res=E.realistic_runway(r, sc),
                   a_rows=a_rows, lt=lt, LR=LR, sim=E.simulate(acct, d, sc), age=age, flags=flags, d_full=d_full,
                   risk=E.overdraft_risk(acct, d), cushion=(cu := E.cushion(acct, d, dip_table=dip_days())),
                   diagnosis=E.diagnose(acct, d, cushion_res=cu),
                   committed=None if asof else E.committed_outflows(acct, standing_orders()),
                   repeat=E.repeat_overdraft(acct, d, repeat_table(int(asof[:4]) if asof else 2025)))   # Dec 2024 view: rates from 2023 -> 2024 only
