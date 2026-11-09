"""'Customers like this': the nearest past customers and what happened next. Never looks ahead, and the pool is the same
population as the three-year backtest."""
import numpy as np
import pandas as pd
import pytest

import engine as E

pytestmark = pytest.mark.skipif(not (E.DATA / "monthly_summary.csv").exists(),
                                reason="needs the Tangerine data (never committed); runs locally before every merge")


@pytest.fixture(scope="module")
def d():
    return E.load()


def test_cohort_is_the_year_that_is_already_over():
    assert E.like_cohort_month(None) == "2024-12"        # today: judged on 2025
    assert E.like_cohort_month("2024-12") == "2023-12"   # Dec 2024 view: judged on 2024 only
    assert E.like_cohort_month("2023-12") == "2022-12"


@pytest.mark.parametrize("cm,accounts,events", [("2022-12", 1556, 18), ("2023-12", 2213, 34), ("2024-12", 3417, 55)])
def test_pool_matches_the_three_year_backtest(d, cm, accounts, events):
    c = E.like_cohort(d, cm)
    assert (len(c), int(c.overdrawn.sum())) == (accounts, events)


def test_pool_never_uses_the_future(d):
    """Everyone in the Dec 2023 pool was never overdrawn up to Dec 2023, and the outcome comes from 2024 alone."""
    c = E.like_cohort(d, "2023-12")
    m = d["monthly"]
    before = m[(m.month <= "2023-12") & m.account_id.isin(c.index)].groupby("account_id").days_below_zero.sum()
    assert (before == 0).all()
    hit_2024 = (m[(m.month.str[:4] == "2024") & m.account_id.isin(c.index)].groupby("account_id").days_below_zero.sum() > 0)
    assert (hit_2024.reindex(c.index) == c.overdrawn).all()


def test_like_this_picks_the_nearest_and_counts_them():
    cohort = pd.DataFrame({"pct": [0.01, 0.02, 0.50, 0.90], "log_bal": [9.0, 9.0, 9.0, 9.0], "swing": [0.3, 0.3, 0.3, 0.3],
                           "overdrawn": [True, False, False, False]}, index=[1, 2, 3, 4])
    r = E.like_this(cohort, {"pct": 0.015, "log_bal": 9.0, "swing": 0.3}, "2023-12", k=2)
    assert {e["account_id"] for e in r["examples"]} == {1, 2}      # only the low-point rank differs, so the two closest ranks win
    assert (r["k"], r["overdrawn"], r["share"]) == (2, 1, 0.5)
    assert r["base_rate"] == 0.25 and r["cohort"] == "Dec 2023 → 2024"
    assert E.like_this(cohort, {"pct": np.nan, "log_bal": 9.0, "swing": 0.3}, "2023-12") is None


def test_riskiest_customer_looks_riskier_than_the_pool(d):
    m = d["monthly"]; dd = {"monthly": m[m.month <= "2024-12"], "loans": d["loans"]}
    lt = E.liquidity_trough(93172, dd, table=E.ltr_table(dd))
    a = dd["monthly"][dd["monthly"].account_id == 93172]
    cm = E.like_cohort_month("2024-12")
    r = E.like_this(E.like_cohort(d, cm), E.like_query(a, lt, 93172), cm)
    assert r["k"] == E.LIKE_K and r["cohort"] == "Dec 2023 → 2024" and r["share"] > 2 * r["base_rate"]
