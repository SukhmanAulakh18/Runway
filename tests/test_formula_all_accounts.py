"""The judges' runway formula, re-implemented independently and compared with the engine on every account.

The second implementation shares no code with engine.py: plain Python from the raw CSVs (no pandas), medians from the
`statistics` module, and "loan still running at the end of 2025" read from the loan's status letter (C or D) instead of the
engine's date arithmetic. 4,500 accounts x 8 scenarios (no shock, the three README twists, four mixes) = 36,000 cases.
"""
import csv
import statistics
from collections import defaultdict

import pytest

import engine as E

pytestmark = pytest.mark.skipif(not (E.DATA / "monthly_summary.csv").exists(),
                                reason="needs the Tangerine data (never committed); runs locally before every merge")

SHOCKS = {
    "no shock": E.Shock(),
    "job loss (EI 55%)": E.Shock(income_factor=0.55),
    "furnace: one month of spending": E.Shock(one_off_months_of_spending=1.0),
    "job loss + bills +15%": E.Shock(income_factor=0.55, bills_increase_pct=0.15),
    "mix 1": E.Shock(income_factor=0.7, bills_increase_pct=0.10),
    "mix 2": E.Shock(spending_increase=300.0),
    "mix 3": E.Shock(income_factor=0.55, one_off_cost=3000.0),
    "mix 4": E.Shock(income_factor=0.8, bills_increase_pct=0.2, spending_increase=150.0, one_off_months_of_spending=0.5),
}


def _independent_inputs():
    rows = defaultdict(list)
    with open(E.DATA / "monthly_summary.csv", newline="") as f:
        for r in csv.DictReader(f):
            rows[int(r["account_id"])].append(r)
    running = {}
    with open(E.DATA / "loans.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["status"] in ("C", "D"):                    # README: payment counts only if the loan runs past the end of 2025
                running[int(r["account_id"])] = float(r["monthly_payment"])
    out = {}
    for acct, rs in rows.items():
        rs.sort(key=lambda r: r["month"])
        f = lambda k: [float(r[k]) for r in rs]            # noqa: E731
        out[acct] = {"I": statistics.median(f("money_in")), "S": statistics.median(f("money_out")),
                     "H": statistics.median(f("household_bills")),
                     "B": statistics.fmean(f("avg_daily_balance")[-6:]), "P": running.get(acct, 0.0)}
    return out


def _independent_runway(x, s):
    income_after = s.income_factor * x["I"]
    spending_after = x["S"] + s.bills_increase_pct * x["H"] + s.spending_increase
    left = x["B"] - (s.one_off_cost + s.one_off_months_of_spending * x["S"])
    gap = spending_after - income_after
    if left <= 0:
        return 0.0
    if gap <= 0:
        return 120.0
    return round(min(left / gap, 120.0), 1)


@pytest.fixture(scope="module")
def checked():
    d = E.load()
    ind = _independent_inputs()
    vec = E.all_profiles(d)
    return d, ind, vec


def test_runway_matches_an_independent_implementation_on_36000_cases(checked):
    d, ind, vec = checked
    assert len(ind) == 4500 and set(ind) == set(int(a) for a in vec.index)
    mismatches, cases = [], 0
    for name, s in SHOCKS.items():
        engine_vec = E.runway_vec(vec, s)
        for acct, x in ind.items():
            cases += 1
            if _independent_runway(x, s) != float(engine_vec.loc[acct]):
                mismatches.append((acct, name, _independent_runway(x, s), float(engine_vec.loc[acct])))
    assert cases == 36000
    assert not mismatches, f"{len(mismatches)} of {cases} cases differ, e.g. {mismatches[:3]}"


def test_per_account_profile_matches_too(checked):
    """engine.profile() (the path the app uses for one customer) agrees with the independent inputs on a sample."""
    d, ind, _ = checked
    for acct in sorted(ind)[::45]:                           # 100 accounts, spread across the id range
        p = E.profile(acct, d)
        x = ind[acct]
        assert (p.income, p.spending, p.household_bills, p.loan_payment) == pytest.approx((x["I"], x["S"], x["H"], x["P"]))
        assert p.buffer == pytest.approx(x["B"])
        for s in SHOCKS.values():
            assert E.runway(p, s)["runway"] == _independent_runway(x, s)


def test_edge_cases_are_covered_and_counted(checked):
    """The awkward accounts exist in the data and the formula handles them: none gets a NaN or a negative runway."""
    _, ind, vec = checked
    no_income = sum(1 for x in ind.values() if x["I"] == 0)
    no_spending = sum(1 for x in ind.values() if x["S"] == 0)
    wiped = sum(1 for x in ind.values() if x["B"] <= 0)
    print(f"edge cases: {no_income} with no money in, {no_spending} with no money out, {wiped} with a buffer at or below zero")
    for s in SHOCKS.values():
        r = E.runway_vec(vec, s)
        assert r.notna().all() and (r >= 0).all() and (r <= 120).all()
