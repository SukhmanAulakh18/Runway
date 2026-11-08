"""Resilience engine for the Tangerine track.

Part 1 (profile) and the runway formula follow the judges' definitions in the
track README exactly, so live-twist numbers match their answer key.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(os.environ.get("RUNWAY_DATA", Path(__file__).resolve().parent / "data"))  # folder with the Tangerine CSVs
END_OF_DATA = pd.Timestamp("2025-12-31")
RUNWAY_CAP = 120.0


def load(data_dir: Path = DATA) -> dict[str, pd.DataFrame]:
    ms = pd.read_csv(data_dir / "monthly_summary.csv").sort_values(["account_id", "month"])
    loans = pd.read_csv(data_dir / "loans.csv", parse_dates=["loan_start"])
    loans["loan_end"] = [s + pd.DateOffset(months=int(d)) for s, d in zip(loans.loan_start, loans.duration_months)]
    loans["running_end_2025"] = loans.loan_end > END_OF_DATA  # equals status C/D in this data
    return {"monthly": ms, "loans": loans}


@dataclass
class Profile:
    account_id: int
    income: float          # I: median money_in
    fixed_costs: float     # F: median(household_bills + insurance + loan_payments)
    spending: float        # S: median money_out
    buffer: float          # B: mean avg_daily_balance over last 6 rows
    household_bills: float # H: median household_bills
    loan_payment: float    # P: monthly_payment if loan running at end of 2025
    months_of_data: int
    breakdown: dict = field(default_factory=dict)


def profile(acct: int, d: dict[str, pd.DataFrame]) -> Profile:
    m = d["monthly"]
    a = m[m.account_id == acct].sort_values("month")
    if a.empty:
        raise KeyError(f"account_id {acct} not found")
    fixed = a.household_bills + a.insurance + a.loan_payments
    loan = d["loans"][d["loans"].account_id == acct]
    pay = float(loan.monthly_payment.iloc[0]) if (len(loan) and loan.running_end_2025.iloc[0]) else 0.0
    breakdown = {c: float(a[c].median()) for c in [
        "household_bills", "insurance", "loan_payments", "bank_fees",
        "cash_withdrawals_genuine", "card_withdrawals", "transfers_out_other",
        "cash_deposits", "transfers_in", "pension_in", "interest_in"]}
    return Profile(
        account_id=acct,
        income=float(a.money_in.median()),
        fixed_costs=float(fixed.median()),
        spending=float(a.money_out.median()),
        buffer=float(a.tail(6).avg_daily_balance.mean()),
        household_bills=float(a.household_bills.median()),
        loan_payment=pay,
        months_of_data=len(a),
        breakdown=breakdown,
    )


@dataclass
class Shock:
    income_factor: float = 1.0      # e.g. 0.55 for job loss with EI at 55%
    bills_increase_pct: float = 0.0 # e.g. 0.15 for household bills +15% (applied to H)
    spending_increase: float = 0.0  # extra monthly spending in dollars
    one_off_cost: float = 0.0       # dollars, e.g. a repair
    one_off_months_of_spending: float = 0.0  # e.g. 1.0 = "a full month of typical spending"


def runway(p: Profile, s: Shock = Shock()) -> dict:
    """Judges' runway formula, rounded to 1 decimal, capped at 120."""
    income_after = s.income_factor * p.income
    spending_after = p.spending + s.bills_increase_pct * p.household_bills + s.spending_increase
    one_off = s.one_off_cost + s.one_off_months_of_spending * p.spending
    buffer_left = p.buffer - one_off
    gap = spending_after - income_after
    if buffer_left <= 0:
        value, label = 0.0, "0 (buffer wiped out)"
    elif gap <= 0:
        value, label = RUNWAY_CAP, "no shortfall (120+)"
    else:
        value = round(min(buffer_left / gap, RUNWAY_CAP), 1)
        label = f"{value} months"
    return {"runway": value, "label": label, "income_after": income_after,
            "spending_after": spending_after, "one_off": one_off,
            "buffer_left": buffer_left, "monthly_gap": gap}


# The three example twist cards from the README
TWISTS = {
    "job_loss_ei55": Shock(income_factor=0.55),
    "furnace_1mo_spending": Shock(one_off_months_of_spending=1.0),
    "job_loss_plus_bills15": Shock(income_factor=0.55, bills_increase_pct=0.15),
}


def all_profiles(d: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Vectorised version of profile() for every account."""
    m = d["monthly"].copy()
    m["fixed"] = m.household_bills + m.insurance + m.loan_payments
    g = m.groupby("account_id")
    out = pd.DataFrame({
        "I": g.money_in.median(), "F": g.fixed.median(), "S": g.money_out.median(),
        "H": g.household_bills.median(), "n_months": g.size(),
        "B": g.tail(6).groupby("account_id").avg_daily_balance.mean(),
    })
    run = d["loans"].loc[d["loans"].running_end_2025, ["account_id", "monthly_payment"]].set_index("account_id")
    out["P"] = run.monthly_payment.reindex(out.index).fillna(0.0)
    return out


def runway_vec(df: pd.DataFrame, s: Shock) -> pd.Series:
    inc = s.income_factor * df.I
    spend = df.S + s.bills_increase_pct * df.H + s.spending_increase
    left = df.B - (s.one_off_cost + s.one_off_months_of_spending * df.S)
    gap = spend - inc
    r = np.where(left <= 0, 0.0, np.where(gap <= 0, RUNWAY_CAP, np.minimum(left / gap.where(gap > 0, np.nan), RUNWAY_CAP)))
    return pd.Series(np.round(r, 1), index=df.index)


# ---------------------------------------------------------------------------
# v2: realistic runway, Monte Carlo simulation, plan
# Choices below were selected out-of-time (features <= 2024, outcome = any
# negative-balance day in 2025): realistic AUC 0.841 vs answer key 0.783,
# difference +0.058 [95% CI +0.026, +0.090], n = 3,668, 129 events.
# ---------------------------------------------------------------------------
EI_RATE = 0.55
EI_WEEKLY_MAX_2026 = 729.0                      # canada.ca, claims from Dec 28, 2025
EI_MONTHLY_MAX = EI_WEEKLY_MAX_2026 * 52 / 12   # about $3,159
WINDOW = 12                                     # months of recent history for typical flows


@dataclass
class Realistic:
    account_id: int
    income: float           # mean money_in, last 12 months
    protected_income: float # pension + interest: keeps coming after a job loss
    earned_income: float    # income that a job loss would stop
    spending: float         # mean money_out, last 12 months
    essential: float        # household bills + insurance + loan payments + bank fees
    flexible: float         # everything else (cash and card withdrawals, other transfers)
    transfers_out_other: float
    loan_payments: float
    household_bills: float
    buffer: float           # same as the answer key: mean avg_daily_balance, last 6 rows
    dip: float              # typical gap between average and lowest balance within a month
    window_months: int
    loan_adjust: float = 0.0  # loan payment owed from now on minus the window's average (a new loan's payment isn't in history yet)
    spending_history: float = 0.0  # mean money_out actually seen in the window (spending minus loan_adjust), for plain sentences


def _acct(acct: int, d: dict) -> pd.DataFrame:
    a = d["monthly"][d["monthly"].account_id == acct].sort_values("month")
    if a.empty:
        raise KeyError(f"account_id {acct} not found")
    return a


def loan_payment_due(acct: int, d: dict, month: str) -> float:
    """Monthly loan payment owed after `month` (YYYY-MM): the loan started on or before it and runs past it.
    Uses only the start date and term, known when the loan was granted, so it is safe in the Time Machine."""
    L = d["loans"][d["loans"].account_id == acct]
    if L.empty:
        return 0.0
    l = L.iloc[0]
    end_of_month = pd.Period(month).end_time
    return float(l.monthly_payment) if (l.loan_start <= end_of_month and l.loan_end > end_of_month) else 0.0


def realistic_profile(acct: int, d: dict, window: int = WINDOW) -> Realistic:
    a = _acct(acct, d)
    w = a.tail(window)
    income = float(w.money_in.mean())
    protected = float((w.pension_in + w.interest_in).mean())
    # Forward-looking loan payment: a loan granted in the last months is barely in the 12-month average (93172: $0 in
    # history, $4,638/month owed from Jan 2025); one that just ended no longer costs anything.
    loan_now = loan_payment_due(acct, d, a.month.iloc[-1])
    loan_adjust = loan_now - float(w.loan_payments.mean())
    essential = float((w.household_bills + w.insurance + w.loan_payments + w.bank_fees).mean()) + loan_adjust
    spending = float(w.money_out.mean()) + loan_adjust
    return Realistic(
        account_id=acct, income=income, protected_income=protected,
        earned_income=max(income - protected, 0.0), spending=spending,
        essential=essential, flexible=max(spending - essential, 0.0),
        transfers_out_other=float(w.transfers_out_other.mean()),
        loan_payments=loan_now,
        household_bills=float(w.household_bills.mean()),
        buffer=float(a.tail(6).avg_daily_balance.mean()),
        dip=float((w.avg_daily_balance - w.min_balance).median()),
        window_months=len(w), loan_adjust=loan_adjust, spending_history=float(w.money_out.mean()),
    )


@dataclass
class Scenario:
    """A shock as the realistic engine understands it (superset of Shock)."""
    job_loss: bool = False
    ei_rate: float = EI_RATE        # share of earned income EI replaces
    ei_months: int = 6              # how long EI is paid in the simulation
    ei_cap: bool = True             # apply the 2026 weekly maximum
    income_cut: float = 0.0         # non-job-loss pay cut, e.g. 0.2 = earned income down 20%
    bills_increase_pct: float = 0.0
    spending_increase: float = 0.0  # dollars per month (negative = a cut)
    one_off_cost: float = 0.0
    one_off_months_of_spending: float = 0.0
    return_to_work_month: int | None = None  # simulation only
    employment_share: float = 1.0   # assumed share of non-pension inflows that a job loss stops

    def to_answer_key_shock(self) -> Shock:
        factor = self.ei_rate if self.job_loss else (1.0 - self.income_cut)
        return Shock(income_factor=factor, bills_increase_pct=self.bills_increase_pct,
                     spending_increase=self.spending_increase, one_off_cost=self.one_off_cost,
                     one_off_months_of_spending=self.one_off_months_of_spending)


def ei_benefit(earned: float, rate: float = EI_RATE, cap: bool = True) -> float:
    b = rate * max(earned, 0.0)
    return min(b, EI_MONTHLY_MAX) if cap else b


def realistic_runway(r: Realistic, sc: Scenario) -> dict:
    if sc.job_loss:
        wage = sc.employment_share * r.earned_income
        income_after = r.protected_income + (r.earned_income - wage) + ei_benefit(wage, sc.ei_rate, sc.ei_cap)
    else:
        income_after = r.protected_income + (1 - sc.income_cut) * r.earned_income
    spending_after = r.spending + sc.bills_increase_pct * r.household_bills + sc.spending_increase
    one_off = sc.one_off_cost + sc.one_off_months_of_spending * r.spending
    usable = r.buffer - one_off - r.dip
    gap = spending_after - income_after
    # EI stops after ei_months (the standard formula pays it forever)
    ei_now = ei_benefit(sc.employment_share * r.earned_income, sc.ei_rate, sc.ei_cap) if sc.job_loss else 0.0
    gap_after_ei = gap + ei_now
    ei_ends = bool(sc.job_loss and ei_now > 0 and sc.ei_months > 0)
    if usable <= 0:
        value, label = 0.0, "0 (buffer wiped out)"
    elif not ei_ends:
        if gap <= 0:
            value, label = RUNWAY_CAP, "no shortfall (120+)"
        else:
            value = round(min(usable / gap, RUNWAY_CAP), 1)
            label = "120+ months" if value >= RUNWAY_CAP else f"{value} months"
    else:
        t_ei = usable / gap if gap > 0 else np.inf
        if t_ei <= sc.ei_months:
            value = round(t_ei, 1)
        else:
            left = usable - sc.ei_months * max(gap, 0.0)
            value = round(min(sc.ei_months + left / gap_after_ei, RUNWAY_CAP), 1) if gap_after_ei > 0 else RUNWAY_CAP
        label = ("no shortfall (120+)" if value >= RUNWAY_CAP and gap_after_ei <= 0 else
                 "120+ months" if value >= RUNWAY_CAP else f"{value} months")
    return {"runway": value, "label": label, "income_after": income_after,
            "spending_after": spending_after, "one_off": one_off, "usable_buffer": usable,
            "monthly_gap": gap, "ei_monthly": ei_benefit(sc.employment_share * r.earned_income, sc.ei_rate, sc.ei_cap) if sc.job_loss else 0.0,
            "ei_capped": sc.job_loss and sc.ei_cap and sc.ei_rate * sc.employment_share * r.earned_income > EI_MONTHLY_MAX,
            "gap_after_ei": gap_after_ei if ei_ends else None}


def explain_difference(p: Profile, r: Realistic, sc: Scenario) -> list[str]:
    """Plain-English reasons the two runways differ, computed from the numbers."""
    out = []
    if p.spending > p.income and r.income > r.spending:
        out.append(f"The answer key uses medians, so typical money out (${p.spending:,.0f}) looks bigger than "
                   f"typical money in (${p.income:,.0f}). Over the last {r.window_months} months, ${r.income - r.spending:,.0f} "
                   f"more came in than went out on average: inflows are lumpy, not short.")
    if sc.job_loss and sc.ei_cap and sc.ei_rate * sc.employment_share * r.earned_income > EI_MONTHLY_MAX:
        out.append(f"EI is capped at $729/week in 2026 (about ${EI_MONTHLY_MAX:,.0f}/month), so this customer "
                   f"gets ${EI_MONTHLY_MAX:,.0f}, not {sc.ei_rate:.0%} of their non-pension inflows "
                   f"(${sc.ei_rate * sc.employment_share * r.earned_income:,.0f}).")
    if sc.job_loss and sc.ei_months > 0:
        out.append(f"EI stops after {sc.ei_months} months. The standard formula keeps paying it forever.")
    if sc.job_loss and r.income > 0 and r.protected_income / r.income > 0.5:
        out.append(f"{r.protected_income / r.income:.0%} of money in is pension or interest. A layoff doesn't stop a pension, "
                   f"but the standard formula cuts it to {sc.ei_rate:.0%}.")
    elif sc.job_loss and r.protected_income > 1:
        out.append(f"${r.protected_income:,.0f}/month of pension and interest keeps coming after a job loss.")
    if r.dip > 1:
        out.append(f"Within a typical month the balance dips ${r.dip:,.0f} below its average, so that much of "
                   f"the buffer isn't really usable.")
    if abs(r.spending - p.spending) / max(p.spending, 1) > 0.15:
        out.append(f"Recent money out (last {r.window_months} months, ${r.spending:,.0f}/month) differs from the "
                   f"all-history median (${p.spending:,.0f}).")
    return out


def _sim_paths(acct: int, d: dict, sc: Scenario, months: int, n_paths: int, history: int = 24,
               block: int = 3, seed: int | None = None):
    """Simulated month-end balances (n_paths x months) under the shock: blocks of the customer's own recent months."""
    r = realistic_profile(acct, d)
    h = _acct(acct, d).tail(history)
    inc = h.money_in.to_numpy(); out = h.money_out.to_numpy()
    prot = (h.pension_in + h.interest_in).to_numpy(); hb = h.household_bills.to_numpy()
    n = len(h); b = block if n >= block else 1
    rng = np.random.default_rng(acct if seed is None else seed)
    nb = int(np.ceil(months / b))
    starts = rng.integers(0, n - b + 1, size=(n_paths, nb))
    idx = (starts[:, :, None] + np.arange(b)).reshape(n_paths, nb * b)[:, :months]
    inc_t, out_t, prot_t, hb_t = inc[idx], out[idx], prot[idx], hb[idx]
    earned_t = np.clip(inc_t - prot_t, 0, None)
    t = np.arange(months)[None, :]
    if sc.job_loss:
        wage_share = sc.employment_share
        ei = ei_benefit(wage_share * r.earned_income, sc.ei_rate, sc.ei_cap)
        income = prot_t + (1 - wage_share) * earned_t + np.where(t < sc.ei_months, ei, 0.0)
        if sc.return_to_work_month is not None:
            income = np.where(t >= sc.return_to_work_month, inc_t, income)
    else:
        income = prot_t + (1 - sc.income_cut) * earned_t
    spend = out_t + sc.bills_increase_pct * hb_t + sc.spending_increase + r.loan_adjust   # loan payment owed from now on
    # Start from today's balance (latest month-end), not the 6-month average B: out of time this lifts AUC 0.863 -> 0.877
    # and Brier 0.0152 -> 0.0145 after calibration (evidence.json -> sim_calibration). The standard formula keeps B.
    start = float(h.month_end_balance.iloc[-1]) - sc.one_off_cost - sc.one_off_months_of_spending * r.spending
    return start + np.cumsum(income - spend, axis=1), start, r, n


MAKE_IT_MONTHS = 6   # the twist cards' horizon ("EI for 6 months... do they make it?")


def verdict(p: Profile, key_res: dict, real_res: dict, r: Realistic, sc: Scenario, sim: dict | None = None) -> dict:
    """Plain answer to "do they make it?" and what drives the realistic runway, in months (attribution).

    Each driver flips one realistic choice back to the standard formula's assumption and re-runs realistic_runway.
    direction -1 = our choice shortens the runway, +1 = it lengthens it. months = the size, or None when one side sits
    at the 120-month cap (then it "makes the difference" rather than a number of months).
    One-at-a-time attribution: effects don't add up when choices interact (said in Q&A); direction and ranking hold.
    """
    std, real = key_res["runway"], real_res["runway"]
    drivers = []
    def effect(name, what, alt_r, alt_sc):
        alt = realistic_runway(alt_r, alt_sc)["runway"]
        diff = real - alt
        if abs(diff) < 0.05:
            return
        capped = alt >= RUNWAY_CAP or real >= RUNWAY_CAP
        drivers.append({"driver": name, "what": what, "direction": 1 if diff > 0 else -1,
                        "months": None if capped else round(diff, 1)})
    if abs(r.spending - p.spending) > 1 or abs(r.income - p.income) > 1:
        effect("Recent months", f"their last {r.window_months} months average ${r.income:,.0f} in and ${r.spending:,.0f} out "
               f"(all-history medians: ${p.income:,.0f} and ${p.spending:,.0f})",
               replace(r, income=p.income, spending=p.spending, earned_income=max(p.income - r.protected_income, 0.0)), sc)
    if sc.job_loss and sc.ei_cap:
        effect("EI cap", f"EI is capped at $729 a week (about ${EI_MONTHLY_MAX:,.0f} a month)", r, replace(sc, ei_cap=False))
    if sc.job_loss and sc.ei_months > 0:
        effect("EI ends", f"EI stops after {sc.ei_months} months", r, replace(sc, ei_months=10_000))
    if sc.job_loss and r.protected_income > 1:
        effect("Pension keeps coming", f"${r.protected_income:,.0f} a month of pension and interest keeps coming",
               replace(r, protected_income=0.0, earned_income=r.income), sc)
    if r.dip > 1:
        effect("In-month dip", f"the balance dips ${r.dip:,.0f} within a typical month", replace(r, dip=0.0), sc)
    drivers.sort(key=lambda x: -1e9 if x["months"] is None else -abs(x["months"]))
    answer = "yes" if real >= MAKE_IT_MONTHS else ("paper" if std >= MAKE_IT_MONTHS else "no")
    # Averages can say yes while the low point says no: if most simulated futures fail, the honest answer is "fragile".
    if answer == "yes" and sim is not None and sim["p_survive_6"] < 0.5:
        answer = "fragile"
    if answer == "fragile":
        headline = (f"Fragile. On average money in covers money out, but only ${max(real_res['usable_buffer'], 0):,.0f} of usable "
                    f"savings is left, so most futures run out within {MAKE_IT_MONTHS} months.")
    elif answer == "yes":
        headline = ("Yes. Money in still covers money out after this shock." if real >= RUNWAY_CAP
                    else f"Yes. Realistically they last {real_res['label']}.")
    elif answer == "paper":
        headline = f"Only on paper. The standard formula says {key_res['label']}; realistically {real_res['label']}."
    else:
        headline = ("No. This shock wipes out their usable savings straight away." if real <= 0
                    else f"No. Realistically they run out in about {real_res['label']} ({key_res['label']} on the standard formula).")
    want = 1 if answer == "yes" else -1   # fragile / no / paper: name what shortens the runway
    top = next((x for x in drivers if x["direction"] == want), None)
    if real <= 0 and r.buffer - r.dip <= 0:
        reason = f"Their usable savings were already gone before the shock (average balance {'-' if r.buffer < 0 else ''}${abs(r.buffer):,.0f})."
    elif top:
        reason = (f"The biggest reason: {top['what']}." if top["months"] is None
                  else f"The biggest reason: {top['what']} ({top['months']:+.1f} months).")
    else:
        reason = None
    futures = f"{round(sim['p_survive_6'] * 10)} of 10 simulated futures last 6 months." if sim else None
    if sim and sim.get("months_to_zero_p50") is not None:
        hi = sim.get("months_to_zero_p90")
        futures += (f" Most likely they run out around month {sim['months_to_zero_p50']:.0f} "
                    f"(between month {sim['months_to_zero_p10']:.0f} and {f'{hi:.0f}' if hi is not None else 'beyond 24'} in 8 of 10 futures).")
    if sim and answer in ("no", "paper") and sim["p_survive_6"] >= 0.7:   # the two methods look apart: say why
        futures += (f" The simulation is more hopeful because it starts from today's balance (${sim['start']:,.0f}), not the 6-month average."
                    if sim["start"] > r.buffer else " The simulation is more hopeful because their good months often make up for the bad ones.")
    return {"answer": answer, "headline": headline, "reason": reason, "futures": futures, "drivers": drivers,
            "threshold_months": MAKE_IT_MONTHS}


def simulate(acct: int, d: dict, sc: Scenario, months: int = 24, n_paths: int = 2000,
             history: int = 24, block: int = 3, seed: int | None = None) -> dict:
    """Monte Carlo: replay blocks of the customer's own recent months under the shock.

    Seeded by account_id so the same customer and shock always give the same answer.
    Under a shock, p_survive_* are shares of simulated futures (a scenario), not calibrated chances: see overdraft_risk().
    """
    bal, start, r, n = _sim_paths(acct, d, sc, months, n_paths, history, block, seed)
    usable = bal - r.dip
    broke = (usable < 0) | (start - r.dip < 0)
    first = np.where(broke.any(axis=1), broke.argmax(axis=1) + 1, months + 1)
    def p_survive(k): return float((first > k).mean())
    exposure = np.clip(r.dip - bal, 0, None)   # how far the in-month low point goes below zero
    return {
        "ee": exposure.mean(axis=0).tolist(), "pfe95": np.percentile(exposure, 95, axis=0).tolist(),
        "insufficient_history": n < 18, "paths_p10_net": None,
        "months": list(range(1, months + 1)),
        "p10": np.percentile(bal, 10, axis=0).tolist(),
        "p50": np.percentile(bal, 50, axis=0).tolist(),
        "p90": np.percentile(bal, 90, axis=0).tolist(),
        "start": start, "dip": r.dip,
        "p_survive_6": p_survive(6), "p_survive_12": p_survive(12),
        "median_months_to_zero": float(np.median(first)) if (first <= months).mean() >= 0.5 else None,
        # range of when futures run out (months; None = beyond the horizon): a band, not a single number
        "months_to_zero_p10": (float(np.percentile(first, 10)) if np.percentile(first, 10) <= months else None),
        "months_to_zero_p50": (float(np.percentile(first, 50)) if np.percentile(first, 50) <= months else None),
        "months_to_zero_p90": (float(np.percentile(first, 90)) if np.percentile(first, 90) <= months else None),
        "n_paths": n_paths, "history_months": n,
    }


# Calibration: the raw simulation is ~8x too pessimistic out of time (it predicts 13.5% of customers break in
# 2025 vs 1.6% who did), because replayed months wander like a random walk while real customers correct course.
# Its ranking is good (AUC 0.88), so a 2-parameter logistic (Platt) map turns it into a probability.
# Fitted on 2023-12 -> 2024 by evidence.sim_calibration(); validated on 2024-12 -> 2025 (see evidence.json).
SIM_CAL_A, SIM_CAL_B = -3.3602, 0.4574


def calibrate_break(p_raw: float) -> float:
    """Raw simulated P(break within 12 months) -> calibrated P(first overdraft within 12 months)."""
    p = min(max(float(p_raw), 1e-3), 1 - 1e-3)
    return float(1 / (1 + np.exp(-(SIM_CAL_A + SIM_CAL_B * np.log(p / (1 - p))))))


REPEAT_TIERS = [(1, 7, "1-7 days"), (8, 10_000, "8+ days")]


def repeat_rates(m: pd.DataFrame, year: int) -> dict:
    """Out of time: among accounts overdrawn in year-1 (complete both years), share overdrawn again in `year`, by tier
    of days below zero. Use year = the Time Machine year (2025 for today) so no future data is used."""
    a = m[m.month.between(f"{year - 1}-01", f"{year - 1}-12")].groupby("account_id")
    b = m[m.month.between(f"{year}-01", f"{year}-12")].groupby("account_id")
    full = a.size()[a.size() == 12].index.intersection(b.size()[b.size() == 12].index)
    prev, again = a.days_below_zero.sum().reindex(full), b.days_below_zero.sum().reindex(full) > 0
    out = {"year": year, "never_overdrawn_rate": float(again[prev == 0].mean())}
    for lo, hi, name in REPEAT_TIERS:
        sel = prev.between(lo, hi)
        out[name] = {"rate": float(again[sel].mean()), "accounts": int(sel.sum())}
    return out


def repeat_overdraft(acct: int, d: dict, rates: dict) -> dict | None:
    """For a customer overdrawn in the last 12 months: the tested share of similar customers overdrawn again next year."""
    days = int(_acct(acct, d).tail(12).days_below_zero.sum())
    if days == 0:
        return None
    name = next(n for lo, hi, n in REPEAT_TIERS if lo <= days <= hi)
    return {"days_below_zero_12m": days, "tier": name, "rate": rates[name]["rate"], "similar_accounts": rates[name]["accounts"],
            "tested_on": f"{rates['year'] - 1} -> {rates['year']}", "never_overdrawn_rate": rates["never_overdrawn_rate"]}


# ---------------------------------------------------------------------------
# Survival: WHEN does a first overdraft come? Kaplan-Meier by trough group over 24 months, never-overdrawn customers
# scored at December. A cohort's 24-month follow-up must end by the view date (no lookahead): today uses the cohort
# scored Dec 2023 (followed 2024-2025); the Dec 2024 view uses Dec 2022 (followed 2023-2024). evidence.json -> survival.
# ---------------------------------------------------------------------------
SURV_GROUPS = [(0.10, "riskiest 10%"), (0.30, "next 20%"), (1.01, "everyone else")]
SURV_HORIZON = 24


def survival_cohort(d: dict, score_month: str, horizon: int = SURV_HORIZON) -> pd.DataFrame:
    """One row per never-overdrawn, scorable customer at `score_month`: months to first overdraft (or censoring), group."""
    m = d["monthly"]; past = m[m.month <= score_month]
    g = past.groupby("account_id"); nh = g.size(); clean = g.days_below_zero.sum() == 0
    t = ltr_table(d, asof=score_month)
    pop = [a for a in t.index if nh.get(a, 0) >= LTR_MIN_HISTORY and clean.get(a, False)]
    start = pd.Period(score_month) + 1
    fut = m[(m.month > score_month) & m.account_id.isin(pop)][["account_id", "month", "days_below_zero"]].copy()
    fut["k"] = (pd.PeriodIndex(fut.month, freq="M") - start).map(lambda x: x.n) + 1
    fut = fut[fut.k <= horizon]
    ev = fut[fut.days_below_zero > 0].groupby("account_id").k.min()
    last = fut.groupby("account_id").k.max()
    rank = t.loc[pop].ltr.rank(pct=True)
    group = [next(name for cut, name in SURV_GROUPS if r <= cut) for r in rank]
    avg = past[past.account_id.isin(pop)].groupby("account_id").tail(6).groupby("account_id").avg_daily_balance.mean()
    D = pd.DataFrame({"time": ev.reindex(pop).fillna(last.reindex(pop)).fillna(0).astype(float),
                      "event": ev.reindex(pop).notna().astype(int).values, "group": group, "rank": rank.values,
                      "log_balance": np.log(avg.reindex(pop).clip(lower=1)).values, "history": nh.reindex(pop).astype(float).values}, index=pop)
    return D[D.time > 0]


def survival_curves(D: pd.DataFrame, horizon: int = SURV_HORIZON) -> dict:
    """Kaplan-Meier share overdrawn by month 0..horizon for each trough group (censoring handled)."""
    from statsmodels.duration.survfunc import SurvfuncRight
    out = {}
    for _, name in SURV_GROUPS:
        g = D[D.group == name]
        sf = SurvfuncRight(g.time, g.event)
        surv = pd.Series(sf.surv_prob, index=sf.surv_times)
        curve = [float(1 - (surv[surv.index <= k].iloc[-1] if (surv.index <= k).any() else 1.0)) for k in range(horizon + 1)]
        out[name] = {"customers": int(len(g)), "first_overdrafts": int(g.event.sum()), "overdrawn_by_month": curve}
    return out


def survival_score_month(asof: str | None) -> str:
    """Latest December cohort whose 24-month follow-up is complete by the view date."""
    year = int(asof[:4]) if asof else int(END_OF_DATA.year)
    return f"{year - 2}-12"


def when_overdraft(pct_rank: float | None, curves: dict, score_month: str) -> dict | None:
    """'Among customers like this, X% had a first overdraft within 6 / 12 / 24 months' (their trough group's curve)."""
    if pct_rank is None:
        return None
    name = next(n for cut, n in SURV_GROUPS if pct_rank <= cut)
    c = curves[name]["overdrawn_by_month"]
    return {"group": name, "within_6": c[6], "within_12": c[12], "within_24": c[24], "customers": curves[name]["customers"],
            "cohort": f"scored {score_month}, followed {int(score_month[:4]) + 1}-{int(score_month[:4]) + 2}"}


def overdraft_risk(acct: int, d: dict) -> dict:
    """Calibrated chance of a first overdraft in the next 12 months if nothing changes (no shock).

    Only a forecast for the population it was validated on: 12+ months of history and never overdrawn.
    Under a shock, use simulate()'s share of surviving futures instead; that is a scenario, not a forecast.
    """
    a = _acct(acct, d)
    raw = 1 - simulate(acct, d, Scenario())["p_survive_12"]
    in_pop = bool(len(a) >= LTR_MIN_HISTORY and (a.days_below_zero == 0).all())
    return {"p_12m": calibrate_break(raw), "p_raw": float(raw), "validated_population": in_pop}


# ---------------------------------------------------------------------------
# Dip-focused action: the product that follows from the trough finding.
# Backtest (evidence.json -> impact): flag the riskiest 10% at Dec 2024; a buffer sized at each customer's
# typical dip fully covers 27 of 34 caught first overdrafts in 2025, with $78K actually drawn on $2.9M of limits;
# an alert at the customer's own dip level fires before 23 of 34 of them (median 3 months early), a $100 alert 1 of 34.
# A cushion from the last 6 months' lowest balance is $0 for exactly these customers (they were never negative).
# ---------------------------------------------------------------------------
BUFFER_CONSERVATIVE_Q = 0.75   # risk-appetite option for the buffer: the knee of the coverage-vs-limits curve
DIP_DAY_RELIABLE = 0.70   # share of months within +-5 days of the usual dip day to call the timing reliable


def cushion(acct: int, d: dict, dip_table: pd.DataFrame | None = None) -> dict:
    """Dip-focused plan for one customer: buffer size, personal alert level, top-up now, usual dip day."""
    a = _acct(acct, d)
    r = realistic_profile(acct, d)
    last = float(a.month_end_balance.iloc[-1])
    w = a.tail(WINDOW)
    out = {"buffer": r.dip,                        # overdraft protection / auto-transfer limit = typical in-month dip
           # conservative option: the dip of a 1-in-4 bad month. Backtest (evidence.json -> buffer_confidence): covers
           # 85-90% of caught first overdrafts vs 75-79% for the median, for ~$5K more actually drawn; higher levels add
           # limits, not coverage. The median stays the default because it was fixed before those years were tested.
           "buffer_conservative": float((w.avg_daily_balance - w.min_balance).quantile(BUFFER_CONSERVATIVE_Q)),
           "alert_level": r.dip,                   # below this, a normal month can take the balance under $0
           "top_up_now": max(r.dip - last, 0.0),   # move this to chequing now to be covered this month
           "last_balance": last, "as_of": a.month.iloc[-1],
           "dip_day": None, "dip_day_share": None, "dip_day_reliable": False}
    if dip_table is not None:
        t = dip_table[(dip_table.account_id == acct) & (dip_table.month <= a.month.iloc[-1])].tail(WINDOW)
        if len(t) >= 6:
            day = int(t.day.median())
            share = float((t.day.sub(day).abs() <= 5).mean())
            out.update(dip_day=day, dip_day_share=share, dip_day_reliable=share >= DIP_DAY_RELIABLE)
    return out


def load_standing_orders(data_dir: Path = DATA) -> pd.DataFrame | None:
    """standing_orders.csv: an undated end-of-2025 snapshot. Use for today's view only, never in backtests (lookahead)."""
    f = data_dir / "standing_orders.csv"
    return pd.read_csv(f) if f.exists() else None


# ---------------------------------------------------------------------------
# Diagnosis -> next best action. The trough says WHO; these say WHY and WHAT TO DO.
# Tested out of time (evidence.json -> diagnoses): adding these signals to the trough did not catch more first
# overdrafts at a 10% flag rate (33-34 of 55 either way), so they are not a new score. Inside the flagged 10% they do
# separate risk: "money in fell" overdrew 13.5% (2024) and 20.3% (2025) vs 9-10% for all flagged, so they order the calls.
# Rejected: "bills leave before the main deposit" was PROTECTIVE (0.4-1.0% vs 1.6%), so no "move the bill date" action.
# ---------------------------------------------------------------------------
INCOME_DROP = 0.75        # money in, last 3 months vs the 9 before, at or below this ratio
NEW_LOAN_BURDEN = 0.30    # new loan (last 12 months) payment as a share of typical money in
SWING_THRESHOLD = 0.47    # sd of monthly net flow / average balance; top 10% in 2023 (0.472) and 2024 (0.469)


def diagnosis_signals(acct: int, d: dict) -> dict | None:
    """The numbers behind each diagnosis, from the last 12 months only (None if under 12 months of history)."""
    a = _acct(acct, d)
    if len(a) < 12:
        return None
    w = a.tail(12); last3, prev9 = w.tail(3), w.head(9)
    month = a.month.iloc[-1]
    L = d["loans"][d["loans"].account_id == acct]
    new_loan = None
    if len(L) and L.iloc[0].loan_start.strftime("%Y-%m") > (pd.Period(month) - 12).strftime("%Y-%m") and loan_payment_due(acct, d, month) > 0:
        l = L.iloc[0]
        new_loan = {"payment": float(l.monthly_payment), "amount": float(l.amount), "duration_months": int(l.duration_months),
                    "start": l.loan_start.strftime("%Y-%m-%d"), "share_of_money_in": float(l.monthly_payment / max(w.money_in.median(), 1.0))}
    net = (w.money_in - w.money_out)
    return {"money_in_last3": float(last3.money_in.mean()), "money_in_prev9": float(prev9.money_in.mean()),
            "money_in_ratio": float(last3.money_in.mean() / prev9.money_in.mean()) if prev9.money_in.mean() > 0 else None,
            "new_loan": new_loan,
            "swing": float(net.std() / max(abs(w.avg_daily_balance.mean()), 1.0)), "net_sd": float(net.std()),
            "good_month_surplus": float(net[net > 0].median()) if (net > 0).any() else 0.0,
            "days_below_zero_12m": int(w.days_below_zero.sum())}


def diagnose(acct: int, d: dict, cushion_res: dict | None = None) -> dict | None:
    """Every diagnosis that applies, most urgent first, each with the action a bank can take, sized from own numbers."""
    s = diagnosis_signals(acct, d)
    if s is None:
        return None
    c = cushion_res or cushion(acct, d)
    out = []
    if s["days_below_zero_12m"] > 0:
        out.append({"code": "repeat", "title": "Already overdrawn this year",
                    "why": f"Below $0 on {s['days_below_zero_12m']} days in the last 12 months.",
                    "action": "Overdraft recovery plan: turn what they owe into fixed monthly instalments and set the alert at "
                              f"${c['alert_level']:,.0f}, so it fires before the next dip.",
                    "numbers": {"days_below_zero_12m": s["days_below_zero_12m"], "alert_level": c["alert_level"]}})
    if s["money_in_ratio"] is not None and s["money_in_ratio"] <= INCOME_DROP:
        drop = 1 - s["money_in_ratio"]
        out.append({"code": "income_drop", "title": "Money in is falling",
                    "why": f"Money in fell {drop:.0%}: ${s['money_in_last3']:,.0f} a month over the last 3 months vs "
                           f"${s['money_in_prev9']:,.0f} before.",
                    "action": "Call first, this week: ask about job or income changes, explain EI, and offer a payment "
                              "holiday on any loan before the first overdraft.",
                    "numbers": {"drop": drop, "money_in_last3": s["money_in_last3"], "money_in_prev9": s["money_in_prev9"]}})
    nl = s["new_loan"]
    if nl and nl["share_of_money_in"] >= NEW_LOAN_BURDEN:
        longer = nl["amount"] / (nl["duration_months"] + 12)      # loans.csv: amount = months x payment, so no interest term
        out.append({"code": "new_loan", "title": "New loan is a heavy load",
                    "why": f"A loan from {nl['start']} costs ${nl['payment']:,.0f} a month, {nl['share_of_money_in']:.0%} of typical money in.",
                    "action": f"Loan review: move the payment date to just after their deposits, or extend the term by 12 months "
                              f"(${nl['payment']:,.0f} -> ${longer:,.0f} a month).",
                    "numbers": {"payment": nl["payment"], "share_of_money_in": nl["share_of_money_in"], "payment_if_extended": longer}})
    if s["swing"] >= SWING_THRESHOLD:
        save = 0.5 * s["good_month_surplus"]
        out.append({"code": "swing", "title": "Cash flow swings hard",
                    "why": f"Month to month, money in minus out swings by about ${s['net_sd']:,.0f}, large next to their balance.",
                    "action": f"Auto-save in good months: move half of a good month's surplus (about ${save:,.0f}) into the "
                              f"${c['buffer']:,.0f} cushion until it is full.",
                    "numbers": {"net_sd": s["net_sd"], "auto_save": save, "buffer": c["buffer"]}})
    out.append({"code": "dip", "title": "Dips close to $0 inside the month",
                "why": f"The balance typically falls ${c['buffer']:,.0f} below its average within a month.",
                "action": f"No-risk steps first: an alert when the balance drops below ${c['alert_level']:,.0f}, then an automatic "
                          f"transfer of ${c['buffer']:,.0f} from savings. A small overdraft limit only after a call."
                          + (f" Move ${c['top_up_now']:,.0f} to chequing now." if c["top_up_now"] > 0 else ""),
                "numbers": {"buffer": c["buffer"], "alert_level": c["alert_level"], "top_up_now": c["top_up_now"]}})
    for g in out:   # a few words for the advisor call list
        g["short"] = SHORT_ACTION[g["code"]]
    return {"primary": out[0], "all": out, "signals": s}


SHORT_ACTION = {"repeat": "Recovery plan", "income_drop": "Call this week", "new_loan": "Loan review",
                "swing": "Auto-save good months", "dip": "Alert + auto-transfer"}

# Tangerine's published overdraft protection terms (tangerine.ca fee schedule and FAQ, checked Nov 2026):
# $5 per use, charged at most once a month, plus 19% a year on the overdrawn balance. Customers must apply for it.
TANGERINE_OD_FEE, TANGERINE_OD_RATE = 5.0, 0.19
NSF_FEE_CAP = 10.0   # federal cap on a non-sufficient-funds fee, personal accounts, since March 12, 2026


def overdraft_cost(amount: float, months: float = 1.0) -> dict:
    """What it would cost the customer to use a limit of `amount` fully for `months`, at Tangerine's terms."""
    fee = TANGERINE_OD_FEE * np.ceil(months)
    interest = amount * TANGERINE_OD_RATE * months / 12
    return {"fee": float(fee), "interest": float(interest), "total": float(fee + interest), "months": months, "amount": float(amount)}


def committed_outflows(acct: int, orders: pd.DataFrame | None) -> dict | None:
    """Money that leaves every month by standing order (household bills, insurance, loan, leasing, other): it can't be cut."""
    if orders is None:
        return None
    rows = orders[orders.account_id == acct]
    if rows.empty:
        return None
    by = rows.groupby(rows.purpose.fillna("other")).amount.sum().sort_values(ascending=False)
    return {"total": float(rows.amount.sum()), "orders": int(len(rows)), "by_purpose": {k: float(v) for k, v in by.items()}}


def load_dip_days(data_dir: Path = DATA) -> pd.DataFrame | None:
    """Day of the month each account's balance is lowest, per month, from transactions.csv (None if absent).
    About 5 s and 1M rows: callers cache it once."""
    f = data_dir / "transactions.csv"
    if not f.exists():
        return None
    tx = pd.read_csv(f, usecols=["account_id", "date", "balance"])
    tx["month"] = tx.date.str[:7]
    low = tx.loc[tx.groupby(["account_id", "month"]).balance.idxmin(), ["account_id", "month", "date"]]
    return pd.DataFrame({"account_id": low.account_id.to_numpy(), "month": low.month.to_numpy(),
                         "day": low.date.str[8:10].astype(int).to_numpy()}).sort_values(["account_id", "month"], ignore_index=True)


def make_plan(acct: int, d: dict, sc: Scenario) -> dict:
    """Goal plan + backup plan, every number from this customer's own data."""
    p = profile(acct, d)
    r = realistic_profile(acct, d)
    # Goal: milestones toward surviving 6 months of a job loss on (capped) EI.
    ei_income = r.protected_income + ei_benefit(r.earned_income)
    gap_on_ei = max(r.spending - ei_income, 0.0)
    have = max(r.buffer, 0.0)
    surplus = r.income - r.spending
    steady = 0.5 * surplus if surplus > 0 else 0.0                    # save half the monthly surplus
    stretch = steady + 0.10 * r.flexible                              # plus a 10% cut to unlabelled outflows
    milestones = []
    for name, amount in [("Starter: cover the monthly dip + 1 month on EI", r.dip + 1 * gap_on_ei),
                         ("Core: 3 months on EI", r.dip + 3 * gap_on_ei),
                         ("Full: 6 months on EI", r.dip + 6 * gap_on_ei)]:
        need = max(amount - have, 0.0)
        milestones.append({"name": name, "target": amount, "need": need, "done": need == 0,
                           "months_steady": (need / steady) if (need > 0 and steady > 0) else None,
                           "months_stretch": (need / stretch) if (need > 0 and stretch > 0) else None})
    goal = {"have": have, "monthly_gap_on_ei": gap_on_ei, "monthly_surplus": surplus,
            "steady_saving": steady, "stretch_saving": stretch, "milestones": milestones,
            "benchmark_3mo_spending": 3 * r.spending,
            "deficit_to_close": (-surplus if surplus < 0 else 0.0)}
    # Backup levers under the chosen shock
    base = realistic_runway(r, sc)["runway"]
    levers = []
    def lever(name, how, delta_spend):
        s2 = Scenario(**{**sc.__dict__, "spending_increase": sc.spending_increase + delta_spend})
        new = realistic_runway(r, s2)["runway"]
        levers.append({"action": name, "how": how, "monthly_saving": -delta_spend,
                       "runway": new, "gain": round(new - base, 1) if new < RUNWAY_CAP else None})
    if sc.job_loss:
        levers.append({"action": "Apply for EI in week one", "how": "Benefits are paid from the claim date, not the layoff date",
                       "monthly_saving": 0.0, "runway": base, "gain": 0.0})
    for pct in (0.10, 0.20, 0.50):
        if r.flexible > 0:
            lever(f"Reduce unlabelled outflows {int(pct*100)}%" + (" (survival budget)" if pct == 0.5 else ""), "Cash/card withdrawals and other transfers (purpose unknown)",
                  -pct * r.flexible)
    if r.loan_payments > 1:
        lever("Ask the lender for a payment deferral", f"Loan payments of ${r.loan_payments:,.0f}/month paused",
              -r.loan_payments)
    if r.transfers_out_other > 1:
        lever("Pause other transfers out", "Unlabelled transfers to other banks", -r.transfers_out_other)
    combo = -(0.20 * r.flexible + r.loan_payments)
    if combo < 0:
        lever("Combined: 20% reduction + loan deferral", "Both levers together", combo)
    return {"cushion": cushion(acct, d), "goal": goal, "backup": {"base_runway": base, "levers": levers},
            "profile": p, "realistic": r}


# ---------------------------------------------------------------------------
# v3: Liquidity Trough Ratio, Kalman filter, constrained-optimal cut schedule, watchlist
# LTR evidence (first-time overdrafts, accounts never negative before): AUC 0.841 / 0.844 / 0.860
# predicting 2023 / 2024 / 2025; lowest 10% LTR -> 9.9% vs 0.68% in 2025 (14.6x, 95% CI 8.6-24.8).
# ---------------------------------------------------------------------------
LTR_WINDOW = 6
LTR_MIN_HISTORY = 12   # months; newer accounts' opening month fakes a deep trough (validated backtests used full years)


def ltr_table(d: dict, window: int = LTR_WINDOW, asof: str | None = None) -> pd.DataFrame:
    """Liquidity Trough Ratio for every account: lowest balance / average daily balance, last `window` months.
    `asof` ("YYYY-MM") rewinds time: only months up to and including it are used (Time Machine)."""
    m = d["monthly"].sort_values(["account_id", "month"])
    if asof:
        m = m[m.month <= asof]
    w = m.groupby("account_id").tail(window).groupby("account_id")
    t = pd.DataFrame({"min_balance": w.min_balance.min(), "avg_balance": w.avg_daily_balance.mean(),
                      "neg_days_recent": w.days_below_zero.sum(), "n_months": m.groupby("account_id").size()})
    t["ltr"] = np.where(t.avg_balance > 0, t.min_balance / t.avg_balance, -1.0)
    t["scorable"] = t.n_months >= LTR_MIN_HISTORY
    t["ltr_pct_rank"] = t.ltr.where(t.scorable).rank(pct=True)   # 0 = most fragile; NaN = too new to score
    return t


def liquidity_trough(acct: int, d: dict, table: pd.DataFrame | None = None, asof: str | None = None) -> dict:
    t = ltr_table(d, asof=asof) if table is None else table
    row = t.loc[acct]
    ok = bool(row.scorable)
    return {"ltr": float(row.ltr), "min_balance": float(row.min_balance), "avg_balance": float(row.avg_balance),
            "pct_rank": float(row.ltr_pct_rank) if ok else None, "bottom_10": ok and bool(row.ltr_pct_rank <= 0.10),
            "neg_days_recent": int(row.neg_days_recent), "scorable": ok, "n_months": int(row.n_months),
            "haircut": float(1 - row.ltr) if row.ltr >= 0 else 1.0}   # banker's framing: share of the average gone at the low point


def kalman_level(y: np.ndarray, q_grid: np.ndarray | None = None) -> dict:
    """Local-level Kalman filter: y_t = mu_t + eps_t, mu_t = mu_{t-1} + eta_t.

    Signal-to-noise q = var(eta)/var(eps) chosen by concentrated maximum likelihood over a grid.
    Returns the filtered underlying level and its standard deviation for each month.
    """
    y = np.asarray(y, float)
    n = len(y)
    q_grid = np.logspace(-5, 1, 61) if q_grid is None else q_grid
    best = None
    for q in q_grid:
        a, P = y[0], 1e7          # diffuse start
        v2F, logF, lev, var = [], [], [a], [P]
        for t in range(1, n):
            Pp = P + q
            F = Pp + 1.0
            v = y[t] - a
            K = Pp / F
            a, P = a + K * v, Pp * (1 - K)
            v2F.append(v * v / F); logF.append(np.log(F)); lev.append(a); var.append(P)
        s2 = np.mean(v2F[1:]) if n > 2 else np.var(y)
        ll = -0.5 * np.sum(logF[1:]) - 0.5 * (n - 2) * np.log(max(s2, 1e-9))
        if best is None or ll > best[0]:
            best = (ll, q, s2, np.array(lev), np.array(var))
    _, q, s2, lev, var = best
    return {"level": lev, "sd": np.sqrt(np.maximum(var * s2, 0)), "q": float(q), "obs_sd": float(np.sqrt(s2))}


def net_flow_filter(acct: int, d: dict) -> dict:
    a = _acct(acct, d)
    net = (a.money_in - a.money_out).to_numpy()
    k = kalman_level(net)
    lvl, sd = k["level"], k["sd"]
    drift = None
    if len(lvl) > 7 and sd[-1] > 0:
        drift = float((lvl[-1] - lvl[-7]) / max(sd[-1], 1.0))   # change over 6 months, in filter s.d.
    return {"month": a.month.tolist(), "net": net.tolist(), "level": lvl.tolist(), "sd": sd.tolist(),
            "q": k["q"], "obs_sd": k["obs_sd"], "drift_sd": drift,
            "has_trend": bool(k["q"] > 1e-5 * 1.0001),   # q on the grid floor = month-to-month swings are noise
            "band_from": 2}                               # first 2 months' sd is the diffuse start, don't draw it


def optimize_cuts(acct: int, d: dict, sc: Scenario, horizon: int = 12, max_cut_share: float = 0.5,
                  pessimistic: bool = True, n_paths: int = 2000) -> dict:
    """Constrained-optimal cut schedule: one linear program over the next `horizon` months, solved once.
    (Re-solving it every month as new data arrives would make it a receding-horizon / MPC policy; that is a
    production step, not done here, and its stability is not analysed.)

    Finds the longest stretch T <= horizon for which the balance can be kept above the overdraft line
    (the customer's typical in-month dip) in a bad (10th percentile) or typical (median) outcome, and the
    smallest total reduction in money out that achieves it:
        minimise sum(u_t)  s.t.  bal[t] + sum_{s<=t} u_s >= dip,  0 <= u_t <= u_max,  t = 1..T
    u_max = max_cut_share x (unlabelled outflows + loan payments): bills and insurance are never cut.
    """
    from scipy.optimize import linprog
    # Month-by-month 10th (or 50th) percentile of the simulated balances. Balances are running totals, so months move
    # together: checked on 300 accounts, these cuts keep a median 90% of WHOLE futures safe (never under 75%).
    # share_of_futures_protected reports the exact share for this customer instead of assuming it.
    paths, _, r, _ = _sim_paths(acct, d, sc, horizon, n_paths)
    bal = np.percentile(paths, 10 if pessimistic else 50, axis=0)
    need = r.dip - bal
    ok = need <= 0
    base_months = int(np.argmin(ok)) if not ok.all() else horizon          # protected with no cuts
    umax = max_cut_share * (r.flexible + r.loan_payments)
    L = np.tril(np.ones((horizon, horizon)))
    best = {"months": base_months, "cuts": [0.0] * base_months}
    for T in range(horizon, base_months, -1):
        res = linprog(c=np.ones(T), A_ub=-L[:T, :T], b_ub=-need[:T], bounds=[(0, umax)] * T, method="highs")
        if res.status == 0:
            best = {"months": T, "cuts": res.x.tolist()}
            break
    cuts = np.array(best["cuts"])
    T = len(cuts)
    achieved = float(((paths[:, :T] + np.cumsum(cuts)) >= r.dip).all(axis=1).mean()) if T else None
    return {"base_months": base_months, "protected_months": best["months"], "horizon": horizon,
            "share_of_futures_protected": achieved,   # of all simulated futures, for the protected months
            "cuts": cuts.tolist(), "total": float(cuts.sum()),
            "avg_monthly_cut": float(cuts.mean()) if len(cuts) else 0.0, "max_monthly_cut": umax,
            "path": bal.tolist(), "protected_path": (bal[:len(cuts)] + np.cumsum(cuts)).tolist() if len(cuts) else [],
            "dip": r.dip, "outcome": "a bad case (9 in 10 futures do better)" if pessimistic else "a typical case (median future)"}


def realistic_vec(d: dict, window: int = WINDOW, ei_rate: float = EI_RATE) -> pd.DataFrame:
    """Realistic runway under a job loss on capped EI, for every account (watchlist)."""
    m = d["monthly"].sort_values(["account_id", "month"])
    w = m.groupby("account_id").tail(window)
    g = w.groupby("account_id")
    inc, out = g.money_in.mean(), g.money_out.mean()
    prot = g.pension_in.mean() + g.interest_in.mean()
    earned = (inc - prot).clip(lower=0)
    dip = (w.avg_daily_balance - w.min_balance).groupby(w.account_id).median()
    B = m.groupby("account_id").tail(6).groupby("account_id").avg_daily_balance.mean()
    usable = B - dip
    gap = out - (prot + np.minimum(ei_rate * earned, EI_MONTHLY_MAX))
    rw = np.where(usable <= 0, 0.0, np.where(gap <= 0, RUNWAY_CAP, np.minimum(usable / gap.where(gap > 0), RUNWAY_CAP)))
    return pd.DataFrame({"realistic_runway_ei": np.round(rw, 1)}, index=inc.index)


# ---------------------------------------------------------------------------
# The whole book: every customer gets one tier and one kind of action, so the bank sees its full workload,
# not only the advisor's call list. Priority order; data up to `asof` only (no lookahead).
# ---------------------------------------------------------------------------
BOOK_TIERS = {
    "overdrawn": ("Already overdrawn this year", "Recovery plan: fixed instalments + alert at their own danger level"),
    "act": ("Act now: riskiest 10% by trough", "Advisor contact, matched to the cause (call, auto-save, alert, loan review)"),
    "new_hot": ("New and swinging: top 10% of new accounts", "Welcome check-in call + personal alert"),
    "watch": ("Watch: next 20%", "Automatic personal alert only, no call"),
    "stable": ("Stable", "Nothing: standard service"),
    "new": ("Too new to score", "Standard alerts until there is enough history"),
}
# New accounts (3-11 months) can't be scored by the trough (it needs 12 months, and its out-of-time AUC on new accounts
# is 0.55-0.71). Swings in money in are: chosen on 2023 and 2024 (most overdrafts caught at a 10% flag of 4 candidates, both
# years: 5 of 15, 13 of 28), confirmed on 2025:
# the top 10% catch 13 of 32 first overdrafts, 18.6% vs 3.0% (evidence.json -> new_accounts).
NEW_MIN_MONTHS, NEW_SWING_SHARE = 3, 0.10


def new_account_swing(d: dict, asof: str | None = None) -> pd.DataFrame:
    """For accounts with 3-11 months up to `asof`: sd of monthly money in (opening month dropped), its percentile among
    new accounts, and the flag (top 10%)."""
    m = d["monthly"] if asof is None else d["monthly"][d["monthly"].month <= asof]
    m = m.sort_values(["account_id", "month"])
    n = m.groupby("account_id").size()
    new = n[(n >= NEW_MIN_MONTHS) & (n < LTR_MIN_HISTORY)].index
    w = m[m.account_id.isin(new)]
    w = w[w.groupby("account_id").cumcount() > 0]                       # the opening month starts near $0
    sd = w.groupby("account_id").money_in.std().reindex(new)
    sd = sd.fillna(sd.median())
    rank = sd.rank(pct=True)
    return pd.DataFrame({"money_in_sd": sd, "pct_rank": rank, "flag": rank > 1 - NEW_SWING_SHARE})
WATCH_SHARE = 0.30   # act = riskiest 10%, watch = the next 20% (pct rank 0.10-0.30)


def book_tiers(d: dict, asof: str | None = None) -> pd.Series:
    """One tier per account (keys of BOOK_TIERS), most urgent first, from data up to `asof`."""
    t = ltr_table(d, asof=asof)
    m = d["monthly"] if asof is None else d["monthly"][d["monthly"].month <= asof]
    overdrawn = m.sort_values(["account_id", "month"]).groupby("account_id").tail(12).groupby("account_id").days_below_zero.sum() > 0
    r = t.ltr_pct_rank
    hot = new_account_swing(d, asof).flag.reindex(t.index).fillna(False).to_numpy(dtype=bool)
    tier = np.select([overdrawn.reindex(t.index).fillna(False).to_numpy(), ~t.scorable.to_numpy() & hot, ~t.scorable.to_numpy(),
                      (r <= 0.10).to_numpy(), (r <= WATCH_SHARE).to_numpy()],
                     ["overdrawn", "new_hot", "new", "act", "watch"], default="stable")
    return pd.Series(tier, index=t.index, name="tier")


def watchlist(d: dict) -> pd.DataFrame:
    """Advisor view: every account ranked by liquidity trough, with plain reason codes."""
    P = all_profiles(d)
    t = ltr_table(d)
    out = P[["I", "S", "B", "H"]].join(t)
    out["realistic_runway_ei"] = realistic_runway_vec(d, Scenario(job_loss=True))   # same as realistic_runway()
    out["answer_key_runway_ei"] = runway_vec(P, Shock(income_factor=0.55))
    last = d["monthly"].groupby("account_id").month.max()
    def reasons(r):
        x = []
        if not r.scorable:
            x.append(f"Too new to score ({int(r.n_months)} months)")
        elif r.ltr_pct_rank <= 0.10:
            x.append("Balance dips close to zero (lowest 10% trough)")
        if r.neg_days_recent > 0:
            x.append(f"{int(r.neg_days_recent)} days below zero in last 6 months")
        if r.realistic_runway_ei < 3:
            x.append("Under 3 months on EI")
        if r.answer_key_runway_ei >= 6 and r.realistic_runway_ei < 3:
            x.append("Standard runway looks fine; realistic doesn't")
        if r.H == 0:
            x.append("No labelled bill payments")
        return "; ".join(x)
    out["reasons"] = out.apply(reasons, axis=1)
    out["last_activity"] = last
    return out.sort_values(["scorable", "ltr", "realistic_runway_ei"], ascending=[False, True, True])


def what_happened_next(acct: int, d: dict, asof: str, months: int = 12) -> pd.DataFrame:
    """Time Machine reveal: the months after `asof` (days below zero, lowest balance)."""
    a = _acct(acct, d)
    nxt = a[a.month > asof].head(months)
    return nxt[["month", "days_below_zero", "min_balance", "avg_daily_balance"]].reset_index(drop=True)



# ---------------------------------------------------------------------------
# v4: credit view (overdraft -> default) and the bank-wide portfolio curve
# Evidence: all 76 defaulted loans had an overdraft at some point, none of the 606 others did.
# 27 loans went to accounts already overdrawn: all 27 defaulted (Fisher p = 1.6e-28) vs 49/655 others.
# Among 588 borrowers never overdrawn before the loan, the pre-loan trough predicts default (AUC 0.775).
# ---------------------------------------------------------------------------
LOAN_REVIEW_TROUGH = 0.10   # same "riskiest 10%" cutoff as the watchlist: nothing is fit on loan outcomes


def loan_check(acct: int, d: dict, table: pd.DataFrame | None = None) -> dict | None:
    """Would a review rule at loan approval have held this customer's loan? Uses only months before the loan month:
    hold if ever overdrawn, or in the riskiest 10% of all customers by liquidity trough (12+ months to score).
    Backtest over all 682 loans: evidence.json -> loan_policy."""
    L = d["loans"][d["loans"].account_id == acct]
    if L.empty:
        return None
    l = L.iloc[0]
    prev = (l.loan_start.to_period("M") - 1).strftime("%Y-%m")
    t = ltr_table(d, asof=prev) if table is None else table
    pre = d["monthly"][(d["monthly"].account_id == acct) & (d["monthly"].month <= prev)]
    over = bool((pre.days_below_zero > 0).any())
    scorable = bool(acct in t.index and t.loc[acct].scorable)
    rank = float(t.loc[acct].ltr_pct_rank) if scorable else None
    top = bool(scorable and rank <= LOAN_REVIEW_TROUGH)
    reasons = (["already overdrawn before the loan"] if over else []) + ([f"in the riskiest {rank:.1%} of customers by trough"] if top else [])
    return {"loan_start": l.loan_start.strftime("%Y-%m-%d"), "amount": float(l.amount), "data_up_to": prev,
            "hold": over or top, "reasons": reasons, "overdrawn_before": over, "trough_rank": rank, "scorable": scorable}


def loan_risk(acct: int, d: dict) -> dict | None:
    """Credit view for one account: the loan, and what the account looked like before it was granted."""
    L = d["loans"]
    row = L[L.account_id == acct]
    if row.empty:
        return None
    l = row.iloc[0]
    a = _acct(acct, d)
    start = l.loan_start.strftime("%Y-%m")
    before = a[a.month < start]
    tail = before.tail(LTR_WINDOW)
    pre_ltr = float(tail.min_balance.min() / tail.avg_daily_balance.mean()) if len(tail) and tail.avg_daily_balance.mean() > 0 else None
    pre_I = float(before.money_in.median()) if len(before) else None
    return {"loan_start": l.loan_start.strftime("%Y-%m-%d"), "amount": float(l.amount), "monthly_payment": float(l.monthly_payment),
            "duration_months": int(l.duration_months), "status": l.status, "status_meaning": l.status_meaning,
            "defaulted": bool(l.defaulted), "months_before_loan": int(len(before)),
            "overdrawn_before_loan": bool((before.days_below_zero > 0).any()),
            "pre_loan_ltr": pre_ltr, "pre_loan_min_balance": float(tail.min_balance.min()) if len(tail) else None,
            "payment_to_money_in": (float(l.monthly_payment) / pre_I) if pre_I else None,
            "ever_overdrawn": bool((a.days_below_zero > 0).any())}


def loan_adjust_vec(d: dict, last_month: pd.Series, window_mean_payment: pd.Series) -> pd.Series:
    """Vectorised realistic_profile().loan_adjust: payment owed after each account's last month minus its window average."""
    L = d["loans"].set_index("account_id").reindex(last_month.index)
    end = pd.PeriodIndex(last_month, freq="M").end_time
    running = (L.loan_start <= end) & (L.loan_end > end)
    return L.monthly_payment.where(running, 0.0).fillna(0.0) - window_mean_payment


def realistic_runway_vec(d: dict, sc: Scenario, window: int = WINDOW) -> pd.Series:
    """Realistic runway (EI capped and ending, pension kept, dip-aware) for every account under one scenario."""
    m = d["monthly"].sort_values(["account_id", "month"])
    w = m.groupby("account_id").tail(window)
    g = w.groupby("account_id")
    inc, out, hb = g.money_in.mean(), g.money_out.mean(), g.household_bills.mean()
    out = out + loan_adjust_vec(d, g.month.max(), g.loan_payments.mean())   # same forward loan payment as realistic_profile
    prot = g.pension_in.mean() + g.interest_in.mean()
    earned = (inc - prot).clip(lower=0)
    dip = (w.avg_daily_balance - w.min_balance).groupby(w.account_id).median()
    B = m.groupby("account_id").tail(6).groupby("account_id").avg_daily_balance.mean()
    wage = sc.employment_share * earned
    ei = np.minimum(sc.ei_rate * wage, EI_MONTHLY_MAX) if sc.ei_cap else sc.ei_rate * wage
    if sc.job_loss:
        income = prot + (earned - wage) + ei
    else:
        income = prot + (1 - sc.income_cut) * earned
        ei = ei * 0
    spend = out + sc.bills_increase_pct * hb + sc.spending_increase
    usable = B - sc.one_off_cost - sc.one_off_months_of_spending * out - dip
    gap = spend - income
    gap2 = gap + ei
    ends = sc.job_loss and sc.ei_months > 0
    t1 = np.where(gap > 0, usable / gap.where(gap > 0), np.inf)
    if ends:
        left = usable - sc.ei_months * gap.clip(lower=0)
        t2 = np.where(gap2 > 0, sc.ei_months + left / gap2.where(gap2 > 0), np.inf)
        rw = np.where(t1 <= sc.ei_months, t1, t2)
    else:
        rw = t1
    rw = np.where(usable <= 0, 0.0, np.minimum(rw, RUNWAY_CAP))
    return pd.Series(np.round(rw, 1), index=inc.index)


def portfolio_curve(d: dict, sc: Scenario, months: int = 24) -> pd.DataFrame:
    """Bank-wide view: share of all customers still above the line, month by month, standard vs realistic."""
    P = all_profiles(d)
    key = runway_vec(P, sc.to_answer_key_shock())
    real = realistic_runway_vec(d, sc).reindex(P.index)
    t = np.arange(0, months + 1)
    return pd.DataFrame({"month": t, "standard": [(key >= x).mean() for x in t],
                         "realistic": [(real >= x).mean() for x in t]})
