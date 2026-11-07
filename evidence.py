"""Recompute every headline finding from the raw data and save evidence.json.

Run: python evidence.py   (about 1-2 minutes; 1,000 bootstrap resamples)
"""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import engine as E

def main(n_boot=1000, seed=0):
    d = E.load(); m = d["monthly"]; P = E.all_profiles(d); g = m.groupby("account_id")
    ev = {}
    # 1. Median method mislabels savers
    mean_net = g.money_in.mean() - g.money_out.mean()
    bal_change = g.last().month_end_balance - g.first().month_end_balance
    flag = P.S > P.I
    ev["mislabel"] = {"accounts": int(len(P)), "flagged_deficit": int(flag.sum()),
                      "flagged_share": float(flag.mean()),
                      "flagged_actually_net_positive": float((mean_net[flag] > 0).mean()),
                      "flagged_balance_grew": float((bal_change[flag] > 0).mean())}
    # 2. EI cap
    capped = 0.55 * P.I > E.EI_MONTHLY_MAX
    r_card = E.runway_vec(P, E.Shock(income_factor=0.55))
    gap = P.S - np.minimum(0.55 * P.I, E.EI_MONTHLY_MAX)
    r_cap = pd.Series(np.round(np.where(P.B <= 0, 0, np.where(gap <= 0, 120, np.minimum(P.B / gap.where(gap > 0), 120))), 1), index=P.index)
    ev["ei_cap"] = {"ei_monthly_max": E.EI_MONTHLY_MAX, "capped_share": float(capped.mean()), "capped_n": int(capped.sum()),
                    "capped_median_runway_card": float(r_card[capped].median()), "capped_median_runway_real": float(r_cap[capped].median()),
                    "capped_survive6_card": float((r_card[capped] >= 6).mean()), "capped_survive6_real": float((r_cap[capped] >= 6).mean()),
                    "all_survive6_card": float((r_card >= 6).mean()), "all_survive6_real": float((r_cap >= 6).mean())}
    # 3. Out-of-time: which runway predicts 2025 overdrafts (features <= 2024)
    pre = m[m.month <= "2024-12"]; post = m[m.month >= "2025-01"]
    ok = pre.groupby("account_id").size(); ok = ok[ok >= 12].index
    pre = pre[pre.account_id.isin(ok)]
    y = (post[post.account_id.isin(ok)].groupby("account_id").days_below_zero.sum() > 0).reindex(ok).fillna(False).astype(int).to_numpy()
    X = E.all_profiles({"monthly": pre, "loans": d["loans"]}).loc[ok]
    def flows(src):
        gg = src.groupby("account_id"); inc = gg.money_in.mean(); out = gg.money_out.mean()
        prot = gg.pension_in.mean() + gg.interest_in.mean()
        dip = (src.avg_daily_balance - src.min_balance).groupby(src.account_id).median()
        return [s.reindex(ok) for s in (inc, out, prot, (inc - prot).clip(lower=0), dip)]
    full = flows(pre); last = [a.fillna(b) for a, b in zip(flows(pre[pre.month >= "2024-01"]), full)]
    inc, out, prot, earned, dip = last
    def rw(B, gap): return np.where(B <= 0, 0, np.where(gap <= 0, 120, np.minimum(B / np.where(gap > 0, gap, np.nan), 120)))
    key = -np.asarray(rw(X.B, X.S - 0.55 * X.I), float)
    real = -np.asarray(rw(X.B - dip, out - (prot + np.minimum(0.55 * earned, E.EI_MONTHLY_MAX))), float)
    key = np.where(np.isnan(key), np.nanmedian(key), key); real = np.where(np.isnan(real), np.nanmedian(real), real)
    rng = np.random.default_rng(seed); n = len(y); diffs = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        if y[i].sum() == 0: continue
        diffs.append(roc_auc_score(y[i], real[i]) - roc_auc_score(y[i], key[i]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    ev["out_of_time"] = {"n_accounts": int(n), "events": int(y.sum()), "auc_answer_key": float(roc_auc_score(y, key)),
                         "auc_realistic": float(roc_auc_score(y, real)), "diff": float(roc_auc_score(y, real) - roc_auc_score(y, key)),
                         "diff_ci95": [float(lo), float(hi)], "n_boot": len(diffs),
                         "design": "features from months <= 2024-12; outcome = any negative-balance day in 2025; accounts with >= 12 months history"}
    ev["trough"] = trough_evidence(d, n_boot=n_boot, seed=seed)
    ev["loans"] = loan_evidence(d)
    ev["formula_holes"] = formula_holes(d)
    ev["confounders"] = confounders(d)
    json.dump(ev, open("evidence.json", "w"), indent=2)
    return ev

def _ltr_backtest(m, year, window=6, pct=0.10):
    ya, yb = str(year - 1), str(year)
    ca = m[m.month.between(f"{ya}-01", f"{ya}-12")].groupby("account_id").size()
    cb = m[m.month.between(f"{yb}-01", f"{yb}-12")].groupby("account_id").size()
    full = ca[ca == 12].index.intersection(cb[cb == 12].index)
    pre = m[(m.month <= f"{ya}-12") & m.account_id.isin(full)]
    nv = pre.groupby("account_id").days_below_zero.sum(); nv = nv[nv == 0].index
    y = (m[m.month.between(f"{yb}-01", f"{yb}-12") & m.account_id.isin(nv)].groupby("account_id").days_below_zero.sum() > 0).reindex(nv).astype(int)
    h = pre[(pre.month >= f"{ya}-{13 - window:02d}") & pre.account_id.isin(nv)].groupby("account_id")
    ltr = (h.min_balance.min() / h.avg_daily_balance.mean()).reindex(nv)
    low = ltr <= ltr.quantile(pct)
    return nv, pre, y, ltr, low


def trough_evidence(d, n_boot=1000, seed=0):
    """Liquidity Trough Ratio: first-time overdrafts among accounts never negative before."""
    m = d["monthly"]; out = {"definition": "lowest end-of-day balance / average daily balance over the last 6 months",
                             "population": "complete records in both years; never below zero before the predicted year"}
    rows = []
    for yr in (2023, 2024, 2025):
        nv, pre, y, ltr, low = _ltr_backtest(m, yr)
        a, b, c, n0 = int(y[low].sum()), int(low.sum()), int(y[~low].sum()), int((~low).sum())
        rr = (a / b) / (c / n0); se = np.sqrt(1 / a - 1 / b + 1 / c - 1 / n0)
        rows.append({"predicted_year": yr, "accounts": int(len(nv)), "new_overdrafts": int(y.sum()),
                     "auc": float(roc_auc_score(y, -ltr)), "low10_rate": a / b, "low10_n": b, "low10_events": a,
                     "rest_rate": c / n0, "risk_ratio": rr, "rr_ci95": [float(np.exp(np.log(rr) - 1.96 * se)), float(np.exp(np.log(rr) + 1.96 * se))]})
    out["by_year"] = rows
    # 2025 head-to-head on the same population, with bootstrap CI for LTR
    nv, pre, y, ltr, low = _ltr_backtest(m, 2025)
    yv = y.to_numpy(); X = E.all_profiles({"monthly": pre[pre.account_id.isin(nv)], "loans": d["loans"]}).reindex(nv)
    w = pre[(pre.month >= "2024-01") & pre.account_id.isin(nv)]; g = w.groupby("account_id")
    inc = g.money_in.mean().reindex(nv); outf = g.money_out.mean().reindex(nv)
    prot = (g.pension_in.mean() + g.interest_in.mean()).reindex(nv)
    dip = (w.avg_daily_balance - w.min_balance).groupby(w.account_id).median().reindex(nv)
    def rw(B, gap): return np.where(B <= 0, 0, np.where(gap <= 0, 120, np.minimum(B / np.where(gap > 0, gap, np.nan), 120)))
    cands = {"Standard runway (answer key, EI 55%)": -np.nan_to_num(rw(X.B, X.S - 0.55 * X.I), nan=60),
             "Realistic runway (EI capped, dip-aware)": -np.nan_to_num(rw(X.B - dip, outf - (prot + np.minimum(0.55 * (inc - prot).clip(lower=0), E.EI_MONTHLY_MAX))), nan=60),
             "Lowest balance, last 6 months": -pre[(pre.month >= "2024-07") & pre.account_id.isin(nv)].groupby("account_id").min_balance.min().reindex(nv).to_numpy(),
             "Liquidity Trough Ratio": -ltr.to_numpy()}
    out["head_to_head_2025"] = {k: float(roc_auc_score(yv, v)) for k, v in cands.items()}
    rng = np.random.default_rng(seed); s = cands["Liquidity Trough Ratio"]; boots = []
    for _ in range(n_boot):
        i = rng.integers(0, len(yv), len(yv))
        if yv[i].sum() > 0: boots.append(roc_auc_score(yv[i], s[i]))
    out["ltr_auc_2025_ci95"] = [float(x) for x in np.percentile(boots, [2.5, 97.5])]
    sens = []
    for wdw in (3, 6, 12):
        _, _, y2, l2, _ = _ltr_backtest(m, 2025, window=wdw)
        sens.append({"window_months": wdw, "auc": float(roc_auc_score(y2, -l2))})
    out["sensitivity_window"] = sens
    # Why the no-shock runway can't rank anyone (resolves conflicting analyses)
    full25 = m[m.month.between("2025-01", "2025-12")].groupby("account_id").size(); full25 = full25[full25 == 12].index
    A = m[(m.month <= "2024-12") & m.account_id.isin(full25)]
    yy = (m[m.month >= "2025-01"].groupby("account_id").days_below_zero.sum() > 0).reindex(full25).fillna(False).astype(int)
    XX = E.all_profiles({"monthly": A, "loans": d["loans"]}).reindex(full25); gg = A.groupby("account_id")
    mi, mo = gg.money_in.mean().reindex(full25), gg.money_out.mean().reindex(full25)
    def auc(v): v = pd.Series(v, index=full25); return float(roc_auc_score(yy, -v.fillna(v.median())))
    out["no_shock_vs_shock"] = {"accounts": int(len(full25)), "overdrafts_2025": int(yy.sum()),
        "median_no_shock": auc(rw(XX.B, XX.S - XX.I)), "mean_no_shock": auc(rw(XX.B, mo - mi)),
        "median_ei_shock": auc(rw(XX.B, XX.S - 0.55 * XX.I)), "mean_ei_shock": auc(rw(XX.B, mo - 0.55 * mi)),
        "note": "With no shock almost every account shows 'no shortfall', so the runway can't rank them; under the EI stress test it can."}
    ex = m[m.account_id == 93172].set_index("month")
    h = ex.loc["2024-07":"2024-12"]
    out["example_93172"] = {"avg_balance_jul_dec_2024": float(h.avg_daily_balance.mean()), "lowest_balance": float(h.min_balance.min()),
                            "ltr": float(h.min_balance.min() / h.avg_daily_balance.mean()),
                            "jan_2025_days_below_zero": int(ex.loc["2025-01"].days_below_zero), "feb_2025_days_below_zero": int(ex.loc["2025-02"].days_below_zero),
                            "lowest_2025": float(ex.loc["2025-01":"2025-12"].min_balance.min())}
    return out


def confounders(d):
    """Does the bottom-10% trough flag still predict a first 2025 overdraft after controlling for
    balance size, account age and district unemployment? Same population as the 2025 backtest."""
    import statsmodels.api as sm
    m = d["monthly"]
    nv, pre, y, ltr, low = _ltr_backtest(m, 2025)
    avg = pre[(pre.month >= "2024-07") & pre.account_id.isin(nv)].groupby("account_id").avg_daily_balance.mean()
    acc = pd.read_csv(E.DATA / "accounts.csv").set_index("account_id")
    unemp = acc.district_id.map(pd.read_csv(E.DATA / "districts.csv").set_index("district_id").unemployment_rate_2023)
    X = pd.DataFrame({"bottom_10_trough": low.astype(float), "log_avg_balance": np.log(avg.reindex(nv)),
                      "months_of_history": pre.groupby("account_id").size().reindex(nv).astype(float),
                      "district_unemployment_2023": unemp.reindex(nv)})
    def fit(cols):
        r = sm.Logit(y.astype(float), sm.add_constant(X[cols])).fit(disp=0)
        lo, hi = r.conf_int().loc["bottom_10_trough"]
        return {"odds_ratio": float(np.exp(r.params["bottom_10_trough"])), "or_ci95": [float(np.exp(lo)), float(np.exp(hi))],
                "p_value": float(r.pvalues["bottom_10_trough"])}, r
    unadj, _ = fit(["bottom_10_trough"])
    adj, r = fit(list(X.columns))
    return {"model": "statsmodels Logit: first overdraft in 2025 ~ bottom-10% trough flag + log(avg balance, Jul-Dec 2024) "
                     "+ months of history to Dec 2024 + district unemployment 2023",
            "population": "complete 2024 and 2025, never below zero before 2025 (same as trough by_year 2025)",
            "accounts": int(len(y)), "events": int(y.sum()), "flagged": int(low.sum()),
            "unadjusted": unadj, "adjusted": adj,
            "controls_odds_ratios": {k: float(np.exp(r.params[k])) for k in X.columns if k != "bottom_10_trough"},
            "pseudo_r2": float(r.prsquared)}


def loan_evidence(d):
    """Finding 5: overdraft separates defaulted from repaid loans; pre-loan signals predict default."""
    from scipy.stats import fisher_exact
    m, L = d["monthly"], d["loans"].copy()
    ever = m.groupby("account_id").days_below_zero.sum() > 0
    L["ever_neg"] = L.account_id.map(ever)
    L["start_m"] = L.loan_start.dt.strftime("%Y-%m")
    pre = m.merge(L[["account_id", "start_m"]], on="account_id"); pre = pre[pre.month < pre.start_m]
    L["pre_neg"] = L.account_id.map(pre.groupby("account_id").days_below_zero.sum() > 0).fillna(False)
    L["pre_months"] = L.account_id.map(pre.groupby("account_id").size()).fillna(0)
    a, b = int(L[L.pre_neg].defaulted.sum()), int(L.pre_neg.sum())
    c, n0 = int(L[~L.pre_neg].defaulted.sum()), int((~L.pre_neg).sum())
    out = {"loans": int(len(L)), "defaults": int(L.defaulted.sum()),
           "overdrawn_and_defaulted": int((L.ever_neg & (L.defaulted == 1)).sum()), "overdrawn_borrowers": int(L.ever_neg.sum()),
           "never_overdrawn_defaulted": int((~L.ever_neg & (L.defaulted == 1)).sum()), "never_overdrawn_borrowers": int((~L.ever_neg).sum()),
           "status_by_overdrawn": {st: {"overdrawn": int(((L.status == st) & L.ever_neg).sum()), "never": int(((L.status == st) & ~L.ever_neg).sum())} for st in "ABCD"},
           "pre_loan_overdrawn": b, "pre_loan_overdrawn_defaulted": a,
           "pre_loan_overdrawn_status": {k: int(v) for k, v in L[L.pre_neg].status.value_counts().items()},
           "pre_loan_overdrawn_amount": float(L[L.pre_neg].amount.sum()), "pre_loan_overdrawn_median_amount": float(L[L.pre_neg].amount.median()),
           "others": n0, "others_defaulted": c, "fisher_p": float(fisher_exact([[a, b - a], [c, n0 - c]])[1])}
    noloan = ever[~ever.index.isin(L.account_id)]
    neg25 = m[m.month >= "2025-01"].groupby("account_id").days_below_zero.sum() > 0
    out["no_loan_overdrawn"] = int(noloan.sum()); out["no_loan_overdrawn_2025"] = int(neg25.reindex(noloan[noloan].index).fillna(False).sum())
    ok = L[(~L.pre_neg) & (L.pre_months >= 6)].copy()
    h = pre[pre.account_id.isin(ok.account_id)].sort_values(["account_id", "month"]).groupby("account_id").tail(6).groupby("account_id")
    ok["pre_ltr"] = ok.account_id.map(h.min_balance.min() / h.avg_daily_balance.mean())
    ok["pre_I"] = ok.account_id.map(pre[pre.account_id.isin(ok.account_id)].groupby("account_id").money_in.median())
    ok["pti"] = ok.monthly_payment / ok.pre_I.replace(0, np.nan)
    low = ok.pre_ltr <= ok.pre_ltr.quantile(0.2); hi = ok.pti > ok.pti.quantile(0.75)
    out["pre_loan_signal"] = {"loans": int(len(ok)), "defaults": int(ok.defaulted.sum()),
        "auc_pre_loan_trough": float(roc_auc_score(ok.defaulted, -ok.pre_ltr.fillna(ok.pre_ltr.median()))),
        "auc_payment_to_money_in": float(roc_auc_score(ok.defaulted, ok.pti.fillna(ok.pti.median()))),
        "low20_trough_default": float(ok[low].defaulted.mean()), "low20_n": int(low.sum()), "low20_defaults": int(ok[low].defaulted.sum()),
        "rest_default": float(ok[~low].defaulted.mean()),
        "top25_payment_default": float(ok[hi].defaulted.mean()), "rest_payment_default": float(ok[~hi].defaulted.mean()),
        "both_n": int((low & hi).sum()), "both_default": float(ok[low & hi].defaulted.mean())}
    return out


def formula_holes(d):
    """Where the standard runway formula misleads, counted across all accounts."""
    m = d["monthly"]; P = E.all_profiles(d)
    key = E.runway_vec(P, E.Shock(income_factor=0.55))
    gap_ei, gap_after = P.S - 0.55 * P.I, P.S
    t6 = np.where(gap_ei > 0, P.B / gap_ei.where(gap_ei > 0), np.inf)
    after = np.where(gap_after > 0, 6 + (P.B - 6 * gap_ei.clip(lower=0)) / gap_after.where(gap_after > 0), 120)
    ei6 = pd.Series(np.round(np.where(P.B <= 0, 0, np.where(t6 <= 6, t6, np.minimum(after, 120))), 1), index=P.index)
    pen = m.groupby("account_id").pension_in.sum() > 0
    pen_share = m.groupby("account_id").pension_in.sum() / m.groupby("account_id").money_in.sum()
    base = E.DATA
    cl = pd.read_csv(base / "clients.csv", parse_dates=["birth_date"]); dp = pd.read_csv(base / "dispositions.csv")
    own = dp[dp.type == "owner"].merge(cl, on="client_id").set_index("account_id")
    age = (pd.Timestamp("2025-12-31") - own.birth_date).dt.days / 365.25
    cash = m.groupby("account_id").cash_deposits.sum() / m.groupby("account_id").money_in.sum()
    g = m.groupby("account_id").money_out
    di = pd.read_csv(base / "districts.csv")
    return {"ei_forever": {"survive12_formula": float((key >= 12).mean()), "survive12_ei_stops_6": float((ei6 >= 12).mean()),
                           "flip_from_no_shortfall": int(((key == 120) & (ei6 < 120)).sum())},
            "pensioners": {"accounts": int(pen.sum()), "share": float(pen.mean()), "min_owner_age": float(age.reindex(pen[pen].index).min()),
                           "median_pension_share": float(pen_share[pen].median()), "median_formula_runway_job_loss": float(key[pen].median())},
            "minors": int((age < 18).sum()), "cash_over_80pct_share": float((cash > 0.8).mean()),
            "bad_month_ratio_p90_over_median": float((g.quantile(0.9) / g.median()).replace(np.inf, np.nan).median()),
            "district_unemployment_corr_2022_2023": float(di[["unemployment_rate_2022", "unemployment_rate_2023"]].corr().iloc[0, 1]),
            "stale_accounts": int((m.groupby("account_id").month.max() < "2025-12").sum())}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
