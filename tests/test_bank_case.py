"""For the bank: capacity trade-off, break-even, pilot size, data contract and batch scoring."""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

import engine as E

ROOT = Path(__file__).resolve().parent.parent
EV = json.load(open(ROOT / "evidence.json"))
CAP = EV["capacity"]
HAS_DATA = (E.DATA / "monthly_summary.csv").exists()
needs_data = pytest.mark.skipif(not HAS_DATA, reason="needs the Tangerine data (never committed); runs locally before every merge")


def test_pilot_sample_size_matches_statsmodels_and_grows_as_the_effect_shrinks():
    from statsmodels.stats.power import NormalIndPower
    from statsmodels.stats.proportion import proportion_effectsize
    for p, r in ((0.10, 0.25), (0.15, 0.30), (0.05, 0.20)):
        ref = NormalIndPower().solve_power(effect_size=proportion_effectsize(p, p * (1 - r)), alpha=0.05, power=0.8, ratio=1.0)
        assert E.pilot_sample_size(p, r) == pytest.approx(ref, rel=0.10)
    assert E.pilot_sample_size(0.10, 0.10) > E.pilot_sample_size(0.10, 0.25) > E.pilot_sample_size(0.10, 0.50)


def test_capacity_trade_off_is_consistent_and_its_10pct_row_is_the_headline_backtest():
    headline = {str(r["predicted_year"]): r for r in EV["trough"]["by_year"]}
    for year, rows in CAP["by_year"].items():
        assert [r["flag_share"] for r in rows] == CAP["cuts"]
        assert [r["caught"] for r in rows] == sorted(r["caught"] for r in rows)          # a bigger flag never catches fewer
        ten = next(r for r in rows if r["flag_share"] == 0.10)
        assert (ten["flagged"], ten["caught"], ten["events"]) == (headline[year]["low10_n"], headline[year]["low10_events"], headline[year]["new_overdrafts"])
    for year in E.CAPACITY_YEARS:                                                         # and it gets less precise (more calls per catch)
        prec = [r["caught"] / r["flagged"] for r in CAP["by_year"][year]]
        assert prec == sorted(prec, reverse=True)


def test_bank_case_arithmetic_and_inputs():
    row = {"flag_share": 0.1, "flagged": 100, "caught": 10, "events": 20, "accounts": 1000}
    cap = {"by_year": {"2024": [row], "2025": [row]}}
    b = E.bank_case(cap, 10000, 0.1, cost_per_call=10, value_per_prevented=500, prevent_rate=0.5)
    c = b["chosen"]
    assert (c["calls_per_year"], c["catches_per_year"], c["calls_per_catch"], c["catch_share"], c["precision"]) == (1000, 100, 10, 0.5, 0.1)
    assert (b["cost"], b["break_even_value_per_prevented"], b["value"], b["net"]) == (10000, 200, 25000, 15000)   # 1,000 calls x $10 over 50 prevented
    assert "cost" not in E.bank_case(cap, 10000, 0.1)                                      # no costs entered: only the measured part
    assert b["pilot"]["total"] == 2 * b["pilot"]["per_arm"]
    with pytest.raises(ValueError):
        E.bank_case(cap, 10000, 0.07)


def _ok():
    return pd.DataFrame({"account_id": [1, 1], "month": ["2024-01", "2024-02"], "money_in": [100.0, 100.0],
                         "min_balance": [10.0, 20.0], "avg_daily_balance": [50.0, 60.0], "days_below_zero": [0, 0]})


def test_data_contract_accepts_a_good_file_and_names_each_problem():
    assert E.check_monthly_contract(_ok()) == []
    assert "missing columns: min_balance" in E.check_monthly_contract(_ok().drop(columns="min_balance"))[0]
    bad = _ok(); bad.loc[1, "month"] = "2024-13"
    assert any("YYYY-MM" in p for p in E.check_monthly_contract(bad))
    assert any("duplicate" in p for p in E.check_monthly_contract(pd.concat([_ok(), _ok().iloc[:1]])))
    nan = _ok(); nan.loc[0, "money_in"] = None
    assert any("money_in" in p for p in E.check_monthly_contract(nan))
    inv = _ok(); inv.loc[0, "min_balance"] = 999.0
    assert any("above the average" in p for p in E.check_monthly_contract(inv))
    assert E.check_monthly_contract(_ok().iloc[0:0]) == ["the file has no rows"]


@needs_data
def test_real_file_meets_the_contract_and_batch_scoring_matches_the_engine(tmp_path):
    d = E.load()
    assert E.check_monthly_contract(d["monthly"]) == []
    out = E.score_book(d["monthly"], "2024-12")
    want = E.book_tiers(d, "2024-12")
    assert len(out) == len(want) == 4500
    assert out.set_index("account_id").tier.sort_index().equals(want.sort_index())       # same tiers as the app's whole-book view
    assert (out.tier == "act").sum() == 278 and out.tier.iloc[0] == "overdrawn"           # most urgent first
    # the command line: a good file scores, a broken one is refused with a non-zero exit code
    good = tmp_path / "good.csv"; d["monthly"].head(2000).to_csv(good, index=False)
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "score_book.py"), str(good), "--out", str(tmp_path / "o.csv")],
                         capture_output=True, text=True)
    assert run.returncode == 0 and (tmp_path / "o.csv").exists() and "Scored" in run.stdout
    broken = tmp_path / "bad.csv"; d["monthly"].drop(columns="min_balance").head(50).to_csv(broken, index=False)
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "score_book.py"), str(broken)], capture_output=True, text=True)
    assert run.returncode == 1 and "missing columns" in run.stdout


@needs_data
@pytest.mark.slow
def test_capacity_section_reproduces_from_the_data():
    import evidence
    assert evidence.capacity(E.load()) == CAP
