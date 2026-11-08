"""Acceptance tests for Runway. Every expected number was verified on the Tangerine data.

Run all fast tests:      pytest -q
Run the slow ones too:   pytest -q -m "slow or not slow"
Build each module until its tests pass. Data folder: ./data or RUNWAY_DATA.
"""
import math
import numpy as np
import pandas as pd
import pytest

import engine as E

@pytest.fixture(scope="session")
def d():
    return E.load()

@pytest.fixture(scope="session")
def P(d):
    return E.all_profiles(d)

# ---------------------------------------------------------------- Module 1: data
def test_data_loads(d):
    m = d["monthly"]
    assert len(m) == 185_326 and m.account_id.nunique() == 4_500
    assert m.month.min() == "2020-01" and m.month.max() == "2025-12"
    inn = ["cash_deposits", "transfers_in", "pension_in", "interest_in"]
    out = ["household_bills", "insurance", "loan_payments", "bank_fees", "cash_withdrawals_genuine", "card_withdrawals", "transfers_out_other"]
    assert (m[inn].sum(axis=1) - m.money_in).abs().max() < 1e-6
    assert (m[out].sum(axis=1) - m.money_out).abs().max() < 1e-6

def test_loans_running_matches_status(d):
    L = d["loans"]
    assert len(L) == 682 and int(L.defaulted.sum()) == 76
    assert set(L[L.running_end_2025].status) == {"C", "D"}
    assert set(L[~L.running_end_2025].status) == {"A", "B"}

# ---------------------------------------------------------------- Module 2: answer key
def test_profile_20111(d):
    p = E.profile(20111, d)
    assert p.income == pytest.approx(6339.39, abs=0.01)
    assert p.spending == pytest.approx(8599.605, abs=0.01)
    assert p.buffer == pytest.approx(17611.8633, abs=0.01)
    assert p.household_bills == 0
    assert p.loan_payment == pytest.approx(2330.19, abs=0.01)
    assert p.fixed_costs == pytest.approx(2330.06, abs=0.01)

def test_twists_20111(d):
    p = E.profile(20111, d)
    assert E.runway(p, E.Shock(income_factor=0.55))["runway"] == 3.4
    assert E.runway(p, E.Shock(one_off_months_of_spending=1.0))["runway"] == 4.0
    assert E.runway(p, E.Shock(income_factor=0.55, bills_increase_pct=0.15))["runway"] == 3.4

def test_runway_rules():
    p = E.Profile(1, income=1000, fixed_costs=0, spending=900, buffer=500, household_bills=100, loan_payment=0, months_of_data=12)
    assert E.runway(p)["label"] == "no shortfall (120+)"
    assert E.runway(p, E.Shock(one_off_cost=600))["runway"] == 0
    assert E.runway(p, E.Shock(income_factor=0.0))["runway"] == round(500 / 900, 1)
    p2 = E.Profile(2, income=0, fixed_costs=0, spending=1, buffer=10_000, household_bills=0, loan_payment=0, months_of_data=12)
    assert E.runway(p2)["runway"] == 120.0   # capped

def test_vectorised_matches_scalar(d, P):
    for a in P.sample(20, random_state=1).index:
        p = E.profile(a, d)
        for s in E.TWISTS.values():
            assert E.runway(p, s)["runway"] == E.runway_vec(P.loc[[a]], s).iloc[0]

def test_edge_case_counts(d, P):
    assert int((P.H == 0).sum()) == 1225
    assert int((P.B <= 0).sum()) == 23
    assert int((P.B < P.S).sum()) == 181
    assert int((P.I == 0).sum()) == 14
    assert int((P.S == 0).sum()) == 77
    assert int((d["monthly"].groupby("account_id").month.max() < "2025-12").sum()) == 76

def test_twist_distribution(P):
    r = E.runway_vec(P, E.Shock(income_factor=0.55))
    assert r.median() == pytest.approx(8.6, abs=0.05)
    f = E.runway_vec(P, E.Shock(one_off_months_of_spending=1.0))
    assert (f == 120).mean() == pytest.approx(0.755, abs=0.001)

# ---------------------------------------------------------------- Module 3: realistic runway
def test_ei_cap_constant():
    assert E.EI_MONTHLY_MAX == pytest.approx(729 * 52 / 12)
    assert E.ei_benefit(10_000) == pytest.approx(729 * 52 / 12)
    assert E.ei_benefit(1_000) == pytest.approx(550)
    assert E.ei_benefit(10_000, cap=False) == pytest.approx(5_500)

def test_realistic_examples(d):
    sc = E.Scenario(job_loss=True, ei_rate=0.55, ei_months=6, bills_increase_pct=0.15)
    assert E.realistic_runway(E.realistic_profile(20111, d), sc)["runway"] == 1.2   # was 1.3 before forward loan payments (Nov 8)
    assert E.realistic_runway(E.realistic_profile(20133, d), sc)["runway"] == 1.4
    assert E.runway(E.profile(20133, d), sc.to_answer_key_shock())["runway"] == 4.2

def test_employment_share_assumption(d):
    r = E.realistic_profile(20111, d)
    full = E.realistic_runway(r, E.Scenario(job_loss=True))["runway"]
    half = E.realistic_runway(r, E.Scenario(job_loss=True, employment_share=0.5))["runway"]
    assert (full, half) == (1.2, 3.1)   # was (1.3, 3.4) before forward loan payments (Nov 8)

# ---------------------------------------------------------------- Module 4: findings
def test_median_mislabel(d, P):
    g = d["monthly"].groupby("account_id")
    net = g.money_in.mean() - g.money_out.mean()
    grew = g.last().month_end_balance - g.first().month_end_balance
    flag = P.S > P.I
    assert int(flag.sum()) == 1181
    assert (net[flag] > 0).mean() == pytest.approx(0.9754, abs=0.0005)
    assert (grew[flag] > 0).mean() == pytest.approx(0.9043, abs=0.0005)

def test_ei_cap_finding(P):
    capped = 0.55 * P.I > E.EI_MONTHLY_MAX
    assert int(capped.sum()) == 2574
    card = E.runway_vec(P, E.Shock(income_factor=0.55))
    gap = P.S - np.minimum(0.55 * P.I, E.EI_MONTHLY_MAX)
    real = pd.Series(np.round(np.where(P.B <= 0, 0, np.where(gap <= 0, 120, np.minimum(P.B / gap.where(gap > 0), 120))), 1), index=P.index)
    assert card[capped].median() == pytest.approx(5.4) and real[capped].median() == pytest.approx(3.1)

# ---------------------------------------------------------------- Module 5: trough ratio
def _ltr_backtest(m, year, window=6):
    ya, yb = str(year - 1), str(year)
    ca = m[m.month.between(f"{ya}-01", f"{ya}-12")].groupby("account_id").size()
    cb = m[m.month.between(f"{yb}-01", f"{yb}-12")].groupby("account_id").size()
    full = ca[ca == 12].index.intersection(cb[cb == 12].index)
    pre = m[(m.month <= f"{ya}-12") & m.account_id.isin(full)]
    nv = pre.groupby("account_id").days_below_zero.sum(); nv = nv[nv == 0].index
    y = (m[m.month.between(f"{yb}-01", f"{yb}-12") & m.account_id.isin(nv)].groupby("account_id").days_below_zero.sum() > 0).reindex(nv).astype(int)
    h = pre[(pre.month >= f"{ya}-{13 - window:02d}") & pre.account_id.isin(nv)].groupby("account_id")
    return y, (h.min_balance.min() / h.avg_daily_balance.mean()).reindex(nv)

def test_trough_backtest_2025(d):
    from sklearn.metrics import roc_auc_score
    y, ltr = _ltr_backtest(d["monthly"], 2025)
    assert len(y) == 3417 and int(y.sum()) == 55
    low = ltr <= ltr.quantile(0.10)
    assert (int(y[low].sum()), int(low.sum()), int(y[~low].sum())) == (34, 342, 21)
    assert roc_auc_score(y, -ltr) == pytest.approx(0.8605, abs=0.0005)

@pytest.mark.parametrize("year,n,events,auc", [(2023, 1556, 18, 0.8412), (2024, 2213, 34, 0.8440)])
def test_trough_other_years(d, year, n, events, auc):
    from sklearn.metrics import roc_auc_score
    y, ltr = _ltr_backtest(d["monthly"], year)
    assert (len(y), int(y.sum())) == (n, events)
    assert roc_auc_score(y, -ltr) == pytest.approx(auc, abs=0.0005)

def test_example_93172(d):
    a = d["monthly"][d["monthly"].account_id == 93172].set_index("month")
    h = a.loc["2024-07":"2024-12"]
    assert h.avg_daily_balance.mean() == pytest.approx(18502.57, abs=0.01)
    assert h.min_balance.min() == pytest.approx(238.49, abs=0.01)
    assert int(a.loc["2025-01"].days_below_zero) == 13 and int(a.loc["2025-02"].days_below_zero) == 8
    lt = E.liquidity_trough(93172, d, asof="2024-12")
    assert lt["bottom_10"] and lt["pct_rank"] == pytest.approx(0.016, abs=0.002)

def test_trough_needs_12_months(d):
    t = E.ltr_table(d, asof="2024-12")
    assert t[t.n_months < 12].ltr_pct_rank.isna().all()
    assert not E.liquidity_trough(20134, d, asof="2024-12")["scorable"]

def test_watchlist_time_machine(d):
    m = d["monthly"]; asof = "2024-12"
    dd = {"monthly": m[m.month <= asof], "loans": d["loans"]}
    w = E.watchlist(dd)
    w["ever_negative"] = (dd["monthly"].groupby("account_id").days_below_zero.sum() > 0).reindex(w.index)
    w = w[~w.ever_negative & w.scorable]
    nxt = m[(m.month > asof) & (m.month <= "2025-12")]
    hit = (nxt.groupby("account_id").days_below_zero.sum() > 0).reindex(w.index).fillna(False)
    assert len(w) == 3472 and int(hit.head(50).sum()) == 14

# ---------------------------------------------------------------- Module 6: Kalman
def test_kalman_tracks_level():
    rng = np.random.default_rng(0)
    level = np.r_[np.zeros(30), np.full(30, 1000.0)]
    k = E.kalman_level(level + rng.normal(0, 300, 60))
    assert len(k["level"]) == 60
    assert abs(k["level"][-1] - 1000) < 300 and abs(k["level"][25]) < 300

# ---------------------------------------------------------------- Module 7: Monte Carlo
def test_simulation_reproducible_and_sane(d):
    sc = E.Scenario(job_loss=True, bills_increase_pct=0.15)
    a, b = E.simulate(20111, d, sc), E.simulate(20111, d, sc)
    assert a["p50"] == b["p50"]                                  # seeded by account
    assert len(a["p10"]) == 24 and all(lo <= mid <= hi for lo, mid, hi in zip(a["p10"], a["p50"], a["p90"]))
    assert 0 <= a["p_survive_12"] <= a["p_survive_6"] <= 1
    calm = E.simulate(20134, d, E.Scenario())
    assert calm["p_survive_6"] >= a["p_survive_6"]

# ---------------------------------------------------------------- Module 8: optimiser + plan
def test_optimiser_improves_or_explains(d):
    o = E.optimize_cuts(20134, d, E.Scenario(one_off_months_of_spending=1.0))
    assert o["protected_months"] >= o["base_months"]
    assert all(0 <= c <= o["max_monthly_cut"] + 1e-6 for c in o["cuts"])
    if o["cuts"]:
        assert min(o["protected_path"]) >= o["dip"] - 1e-6

def test_plan_shape(d):
    plan = E.make_plan(20133, d, E.Scenario(job_loss=True, bills_increase_pct=0.15))
    ms = plan["goal"]["milestones"]
    assert [m_["target"] for m_ in ms] == sorted(m_["target"] for m_ in ms)
    assert plan["backup"]["levers"]

# ---------------------------------------------------------------- Module 9: AI layer (offline parts)
@pytest.mark.parametrize("text,expect", [
    ("This customer was laid off. EI pays 55% of their usual income for 6 months.", {"job_loss": True, "ei_rate": 0.55, "ei_months": 6}),
    ("The furnace dies, and the repair costs a full month of their typical spending.", {"one_off_months_of_spending": 1.0}),
    ("They lose their job (EI at 55%) and their household bills go up 15% in the same month.", {"job_loss": True, "bills_increase_pct": 0.15}),
    ("Rent goes up by $400 a month and the car needs a $2,500 repair.", {"spending_increase": 400.0, "one_off_cost": 2500.0}),
    ("Their hours are cut by 30% and utilities rise 10%.", {"income_cut": 0.3, "bills_increase_pct": 0.1}),
])
def test_twist_reader_offline(text, expect):
    import ai
    s = ai.parse_twist_offline(text)
    for k, v in expect.items():
        assert s[k] == pytest.approx(v)

def test_number_verifier():
    import ai
    facts = {"runway": "1.4 months", "need": 21744.0}
    assert ai.verify_numbers("You have 1.4 months and need $21,744.", facts)
    assert not ai.verify_numbers("You need $99,999.", facts)

# ---------------------------------------------------------------- slow: bootstrap evidence
@pytest.mark.slow
def test_evidence_out_of_time(d):
    import evidence
    ev = evidence.main(n_boot=200)
    assert ev["out_of_time"]["auc_realistic"] == pytest.approx(0.8412, abs=0.0005)
    assert ev["out_of_time"]["auc_answer_key"] == pytest.approx(0.7829, abs=0.0005)
    assert ev["trough"]["head_to_head_2025"]["Liquidity Trough Ratio"] == pytest.approx(0.8605, abs=0.0005)


# ---------------------------------------------------------------- v4: EI that ends, credit view, bank view, Finding 5
def test_realistic_ei_ends_after_6_months():
    r = E.Realistic(account_id=1, income=5000, protected_income=0, earned_income=5000, spending=4000, essential=1000,
                    flexible=3000, transfers_out_other=0, loan_payments=0, household_bills=500, buffer=20000, dip=0, window_months=12)
    # EI 2,750/month -> gap 1,250. Forever: 20,000/1,250 = 16.0. Ends at 6: 6 + (20,000 - 7,500)/4,000 = 9.1
    assert E.realistic_runway(r, E.Scenario(job_loss=True, ei_months=0))["runway"] == 16.0
    assert E.realistic_runway(r, E.Scenario(job_loss=True, ei_months=6))["runway"] == 9.1

def test_realistic_vector_matches_scalar(d):
    sc = E.Scenario(job_loss=True, ei_months=6, bills_increase_pct=0.15)
    v = E.realistic_runway_vec(d, sc)
    for a in v.sample(40, random_state=3).index:
        assert abs(E.realistic_runway(E.realistic_profile(a, d), sc)["runway"] - v[a]) <= 0.05

def test_portfolio_curve(d):
    pc = E.portfolio_curve(d, E.Scenario(job_loss=True, ei_months=6))
    row = pc[pc.month == 6].iloc[0]
    assert pc.iloc[0].standard == 1.0 and pc.iloc[0].realistic == 1.0
    assert row.standard == pytest.approx(0.649, abs=0.001) and row.realistic == pytest.approx(0.407, abs=0.001)

def test_loan_risk_93172(d):
    lr = E.loan_risk(93172, d)
    assert lr["loan_start"] == "2024-12-06" and lr["status"] == "D" and not lr["overdrawn_before_loan"]
    assert lr["pre_loan_min_balance"] == pytest.approx(238.49, abs=0.01)
    assert lr["payment_to_money_in"] == pytest.approx(1.504, abs=0.002)
    assert E.loan_risk(20134, d) is None or isinstance(E.loan_risk(20134, d), dict)

def test_overdraft_splits_loan_book(d):
    m, L = d["monthly"], d["loans"].copy()
    ever = m.groupby("account_id").days_below_zero.sum() > 0
    L["neg"] = L.account_id.map(ever)
    assert int((L.neg & (L.defaulted == 1)).sum()) == 76 and int(L.neg.sum()) == 76
    assert int((~L.neg & (L.defaulted == 1)).sum()) == 0 and int((~L.neg).sum()) == 606
    L["start_m"] = L.loan_start.dt.strftime("%Y-%m")
    pre = m.merge(L[["account_id", "start_m"]], on="account_id"); pre = pre[pre.month < pre.start_m]
    pre_neg = L.account_id.map(pre.groupby("account_id").days_below_zero.sum() > 0).fillna(False)
    assert int(pre_neg.sum()) == 27 and int(L[pre_neg].defaulted.sum()) == 27
    assert int(L[~pre_neg].defaulted.sum()) == 49
    noloan = ever[~ever.index.isin(L.account_id)]
    assert int(noloan.sum()) == 212

@pytest.mark.slow
def test_evidence_loans_and_holes(d):
    import evidence
    lo = evidence.loan_evidence(d)
    assert lo["pre_loan_signal"]["auc_pre_loan_trough"] == pytest.approx(0.7753, abs=0.0005)
    assert (lo["pre_loan_signal"]["low20_defaults"], lo["pre_loan_signal"]["low20_n"]) == (23, 118)
    fh = evidence.formula_holes(d)
    assert fh["ei_forever"]["flip_from_no_shortfall"] == 257
    assert fh["pensioners"]["accounts"] == 740 and fh["pensioners"]["min_owner_age"] >= 59
    assert fh["minors"] == 57

@pytest.mark.slow
def test_evidence_confounders(d):
    import evidence
    cf = evidence.confounders(d)
    assert (cf["accounts"], cf["events"], cf["flagged"]) == (3417, 55, 342)   # same population as by_year 2025
    adj = cf["adjusted"]
    assert adj["or_ci95"][0] < adj["odds_ratio"] < adj["or_ci95"][1]
    assert adj["odds_ratio"] == pytest.approx(16.81, abs=0.01)
    assert adj["or_ci95"][0] > 1   # the trough still predicts after balance size, history and unemployment

@pytest.mark.slow
def test_evidence_multiple_testing(d):
    import evidence
    ev = evidence.main(n_boot=200)
    mt = ev["multiple_testing"]
    assert mt["tests"] == len(mt["rows"]) == 29
    assert all(0 <= r["p"] <= r["p_bh"] <= 1 for r in mt["rows"])
    by = {r["hypothesis"]: r for r in mt["rows"]}
    assert all(r["survives"] for r in mt["rows"] if r["log_row"] in (7, "E4"))   # the trough headline
    assert not by["Trough beats Lowest balance, last 6 months (2025)"]["survives"]   # honest: a tie with plain lowest balance
    assert any("14 first overdrafts vs 1.7%" in h for h in by)   # matches the Time Machine watchlist test


# ---------------------------------------------------------------- Monte Carlo calibration (added)
def test_calibration_is_monotone_and_bounded():
    xs = [E.calibrate_break(x) for x in (0.0, 0.05, 0.2, 0.5, 0.9, 1.0)]
    assert xs == sorted(xs) and all(0 < x < 1 for x in xs)
    assert E.calibrate_break(0.5) == pytest.approx(0.035, abs=0.002)   # raw 50% is really about 3.5% (refit, sim starts at latest balance)

def test_overdraft_risk_93172_time_machine(d):
    m = d["monthly"]; dd = {"monthly": m[m.month <= "2024-12"], "loans": d["loans"]}
    risky, calm = E.overdraft_risk(93172, dd), E.overdraft_risk(20134, d)
    assert risky["validated_population"] and 0 < calm["p_12m"] < risky["p_12m"] < 1

def test_watchlist_realistic_matches_know(d):
    w = E.watchlist(d)
    for a in w.sample(30, random_state=5).index:
        assert abs(w.loc[a, "realistic_runway_ei"] - E.realistic_runway(E.realistic_profile(a, d), E.Scenario(job_loss=True))["runway"]) <= 0.05

@pytest.mark.slow
def test_evidence_sim_calibration(d):
    import evidence
    c = evidence.sim_calibration(d)
    assert c["fit"]["a"] == pytest.approx(E.SIM_CAL_A, abs=1e-3) and c["fit"]["b"] == pytest.approx(E.SIM_CAL_B, abs=1e-3)
    v = c["validate"]
    assert v["brier_calibrated"] < v["brier_base_rate"] < v["brier_raw"]
    assert abs(v["calibrated_mean"] - v["observed_rate"]) < 0.005


# ---------------------------------------------------------------- Dip-focused action (added)
def test_cushion_93172_time_machine(d):
    m = d["monthly"]; dd = {"monthly": m[m.month <= "2024-12"], "loans": d["loans"]}
    c = E.cushion(93172, dd)
    assert c["as_of"] == "2024-12" and c["buffer"] == pytest.approx(E.realistic_profile(93172, dd).dip)
    assert c["alert_level"] == c["buffer"] and c["top_up_now"] >= 0
    assert "cushion" in E.make_plan(93172, dd, E.Scenario())

def test_dip_days(d):
    t = E.load_dip_days()
    if t is None:
        pytest.skip("transactions.csv not present")
    assert t.day.between(1, 31).all() and not t.duplicated(["account_id", "month"]).any()
    c = E.cushion(93172, {"monthly": d["monthly"][d["monthly"].month <= "2024-12"], "loans": d["loans"]}, dip_table=t)
    assert c["dip_day"] is not None and not c["dip_day_reliable"]   # 93172 dips on scattered days (3 .. 23)

@pytest.mark.slow
def test_evidence_impact(d):
    import evidence
    i = evidence.impact(d, "2024-12")
    assert (i["first_overdrafts"], i["caught"]) == (55, 34)
    assert i["buffer"]["covered_in_full"] == 27 and i["alert"]["fired_before"] == 23 and i["alert"]["generic_100_fired_before"] == 1
    assert i["buffer"]["drawn_total"] < 0.05 * i["buffer"]["limits_total"]

@pytest.mark.parametrize("acct,sc,answer,top", [
    (20111, dict(job_loss=True, bills_increase_pct=0.15), "no", "Recent months"),   # answer key 3.4, realistic 1.3
    (20176, dict(job_loss=True), "yes", "Pension keeps coming"),                  # pensioner
    (68235, dict(job_loss=True), "paper", None),                                  # standard fine, realistic not
    (66325, dict(job_loss=True), "no", None),                                     # savings already below zero
])
def test_verdict(d, acct, sc, answer, top):
    s = E.Scenario(**sc)
    p, r = E.profile(acct, d), E.realistic_profile(acct, d)
    v = E.verdict(p, E.runway(p, s.to_answer_key_shock()), E.realistic_runway(r, s), r, s)
    assert v["answer"] == answer and v["headline"] and v["reason"]
    if top:
        want = 1 if answer == "yes" else -1
        assert next(x for x in v["drivers"] if x["direction"] == want)["driver"] == top

def test_verdict_fragile_when_most_futures_fail(d):
    """93172 + furnace: averages say 'no shortfall' with $6 usable left ($392 before forward loan payments: one of the last
    12 loan payments was skipped, so the window under-counted it); the simulation says no future lasts 6 months."""
    s = E.Scenario(one_off_months_of_spending=1.0)
    p, r = E.profile(93172, d), E.realistic_profile(93172, d)
    v = E.verdict(p, E.runway(p, s.to_answer_key_shock()), E.realistic_runway(r, s), r, s, E.simulate(93172, d, s))
    assert v["answer"] == "fragile" and v["headline"].startswith("Fragile.") and "$6 " in v["headline"]

def test_repeat_overdraft_rates_out_of_time(d):
    r25, r24 = E.repeat_rates(d["monthly"], 2025), E.repeat_rates(d["monthly"], 2024)
    for r in (r24, r25):   # overdrawn last year -> far likelier again than the never-overdrawn base rate
        assert r["8+ days"]["rate"] > 10 * r["never_overdrawn_rate"] and r["1-7 days"]["rate"] > 10 * r["never_overdrawn_rate"]
    rep = E.repeat_overdraft(93172, d, r25)   # 21 days below zero in 2025
    assert rep["tier"] == "8+ days" and rep["tested_on"] == "2024 -> 2025"
    assert E.repeat_overdraft(20176, d, r25) is None   # never overdrawn


def test_simulation_runway_range_is_ordered(d):
    s = E.simulate(20111, d, E.Scenario(job_loss=True, bills_increase_pct=0.15))
    assert s["months_to_zero_p10"] <= s["months_to_zero_p50"] <= (s["months_to_zero_p90"] or 99)
@pytest.mark.slow
def test_evidence_self_correction_and_extended_bh(d):
    import evidence
    sc = evidence.self_correction(d)
    assert len(sc["rows"]) == 4 and all(r["gap"] > 0.1 and r["share_accounts_positive"] > 0.8 for r in sc["rows"])
    full = evidence.main(n_boot=200)
    ext = full["multiple_testing_extended"]
    # base family + 8 steering tests + the diagnosis tests added Nov 8 (8 of them): every idea tried is counted
    assert len(full["diagnoses"]["tests"]) == 8
    assert ext["tests"] == full["multiple_testing"]["tests"] + 8 + len(full["diagnoses"]["tests"])
    assert all(r["survives"] for r in ext["rows"] if r["log_row"] in (7, "E4", 15))   # trough + steering hold
    assert full["impact"]["2024-12"]["alert"]["quiet_flagged"] > 0

@pytest.mark.slow
def test_evidence_segment_profile(d):
    import evidence
    s = {r["trait"]: r for r in evidence.segment_profile(d)["rows"]}
    assert s["money in per month"]["riskiest_10"] > 2 * s["money in per month"]["everyone_else"]   # not poor: high flow
    assert s["has a loan"]["differs"] and s["has a loan"]["riskiest_10"] > 2 * s["has a loan"]["everyone_else"]
    assert s["pensioner"]["differs"] and s["pensioner"]["riskiest_10"] < 0.02
    assert not s["district average salary"]["differs"] and not s["joint account"]["differs"]   # region doesn't matter


# ---------------------------------------------------------------- Forward loan payments (Nov 8)
def test_new_loan_payment_counts_without_lookahead(d):
    m = d["monthly"]
    assert E.loan_payment_due(93172, d, "2024-12") == pytest.approx(4637.72, abs=0.01)   # granted 2024-12-06
    assert E.loan_payment_due(93172, d, "2024-11") == 0.0                               # not granted yet: no lookahead
    dd = {"monthly": m[m.month <= "2024-12"], "loans": d["loans"]}
    r = E.realistic_profile(93172, dd)
    assert r.loan_adjust == pytest.approx(4637.72, abs=1) and E.realistic_runway(r, E.Scenario())["label"] == "2.4 months"

def test_finished_loan_stops_costing(d):
    L = d["loans"]; done = L[L.loan_end < pd.Timestamp("2025-06-01")].iloc[0]
    assert E.loan_payment_due(int(done.account_id), d, "2025-12") == 0.0


# ---------------------------------------------------------------- Diagnosis -> next best action (Nov 8)
def test_diagnose_orders_by_urgency_and_always_ends_with_the_dip(d):
    m = d["monthly"]; dd = {"monthly": m[m.month <= "2024-12"], "loans": d["loans"]}
    x = E.diagnose(93172, dd)
    assert [g["code"] for g in x["all"]] == ["income_drop", "swing", "dip"]       # money in fell 27% before the overdraft
    assert x["primary"]["code"] == "income_drop" and "27%" in x["primary"]["why"]
    assert [g["code"] for g in E.diagnose(20111, d)["all"]][0] == "repeat"          # already overdrawn: recovery plan first
    assert [g["code"] for g in E.diagnose(20176, d)["all"]] == ["dip"]             # pensioner, steady: cushion only
    for code_list in ([g["code"] for g in E.diagnose(a, d)["all"]] for a in (20111, 20176, 93172)):
        assert code_list[-1] == "dip"

def test_diagnose_needs_a_year_of_history(d):
    m = d["monthly"]; dd = {"monthly": m[m.month <= "2023-12"], "loans": d["loans"]}
    young = dd["monthly"].groupby("account_id").size(); a = int(young[young < 12].index[0])
    assert E.diagnose(a, dd) is None

def test_extended_loan_payment_uses_data_fields_only(d):
    L = d["loans"]; l = L.iloc[0]
    assert l.amount == pytest.approx(l.duration_months * l.monthly_payment, rel=1e-6)   # so amount/(term+12) is the longer-term payment


def test_loan_check_93172_would_have_been_held(d):
    c = E.loan_check(93172, d)
    assert c["hold"] and c["data_up_to"] == "2024-11" and not c["overdrawn_before"] and c["trough_rank"] < 0.10


def test_loan_check_uses_only_data_before_the_loan(d):
    m2 = d["monthly"].copy()
    m2.loc[(m2.account_id == 93172) & (m2.month >= "2024-12"), ["min_balance", "avg_daily_balance", "days_below_zero"]] = [-9e9, 1.0, 31]
    assert E.loan_check(93172, {"monthly": m2, "loans": d["loans"]}) == E.loan_check(93172, d)   # no lookahead


@pytest.mark.slow
def test_evidence_loan_policy(d):
    import evidence
    lp = evidence.loan_policy(d)
    a, b = lp["all_defaults"], lp["finished_unpaid"]
    assert (a["held"], a["caught"], a["events"]) == (118, 41, 76)
    assert a["default_rate_held"] > 5 * a["default_rate_not_held"] and a["fisher_p"] < 1e-6
    assert (b["caught"], b["events"]) == (12, 31) and b["default_rate_held"] > 2.5 * b["default_rate_not_held"] and b["fisher_p"] < 0.01


@pytest.mark.slow
def test_evidence_monitoring_no_breaches(d):
    import evidence
    ev = evidence.main(n_boot=200)
    mo = ev["monitoring"]
    assert mo["breaches"] == [] and mo["checks"]["missing_values"] == 0
    assert {r["effect"] for r in ev["segment"]["rows"] if r["trait"] in ("money in per month", "has a loan", "pensioner")} == {"big"}


def test_overdraft_cost_tangerine_terms():
    c = E.overdraft_cost(6000, 1)
    assert c["fee"] == 5 and c["interest"] == pytest.approx(95.0) and c["total"] == pytest.approx(100.0)   # 6000 x 19% / 12
