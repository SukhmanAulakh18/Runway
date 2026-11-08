"""Recompute every headline finding from the raw data and save evidence.json.

Run: python evidence.py   (about 1-2 minutes; 1,000 bootstrap resamples)
"""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import engine as E


def _p_boot(diffs):
    """Two-sided bootstrap p-value that a difference is 0 (add-one so it is never exactly 0)."""
    x = np.asarray(diffs)
    return float(min(1.0, 2 * (min((x <= 0).sum(), (x >= 0).sum()) + 1) / (len(x) + 1)))


def _p_auc(auc, n_pos, n_neg):
    """Two-sided Mann-Whitney normal approximation for AUC = 0.5 (used when only the AUC was logged)."""
    from scipy.stats import norm
    se0 = np.sqrt((n_pos + n_neg + 1) / (12 * n_pos * n_neg))
    return float(2 * norm.sf(abs(auc - 0.5) / se0))


def _p_ci(est, lo, hi):
    """Two-sided p-value from a logged 95% CI, assuming normality."""
    from scipy.stats import norm
    return float(2 * norm.sf(abs(est) / ((hi - lo) / 3.92)))


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
                         "diff_ci95": [float(lo), float(hi)], "n_boot": len(diffs), "diff_p_boot": _p_boot(diffs),
                         "design": "features from months <= 2024-12; outcome = any negative-balance day in 2025; accounts with >= 12 months history"}
    ev["trough"] = trough_evidence(d, n_boot=n_boot, seed=seed)
    ev["loans"] = loan_evidence(d)
    ev["formula_holes"] = formula_holes(d)
    ev["confounders"] = confounders(d)
    ev["multiple_testing"] = multiple_testing(ev, d)
    ev["sim_calibration"] = sim_calibration(d)
    ev["impact"] = {asof: impact(d, asof) for asof in ("2023-12", "2024-12")}
    ev["self_correction"] = self_correction(d)
    ev["segment"] = segment_profile(d)
    ev["loan_policy"] = loan_policy(d)
    ev["fairness"] = fairness(d)
    ev["monitoring"] = monitoring(d, ev)
    ev["repeat_overdraft"] = {str(y): E.repeat_rates(d["monthly"], y) for y in (2024, 2025)}
    ev["diagnoses"] = diagnoses(d)
    ev["multiple_testing_extended"] = multiple_testing_extended(ev)
    ev["lessons"] = lessons(ev)   # last: reads diagnoses and the extended multiple-testing family
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
    s = cands["Liquidity Trough Ratio"]
    rivals = {k: v for k, v in cands.items() if k != "Liquidity Trough Ratio"}
    combo = (pd.Series(s).rank() + pd.Series(cands["Realistic runway (EI capped, dip-aware)"]).rank()).to_numpy()  # findings_log #8
    out["rank_average_runway_trough_auc"] = float(roc_auc_score(yv, combo))
    rng = np.random.default_rng(seed); boots, vs = [], {k: [] for k in [*rivals, "combo"]}
    for _ in range(n_boot):
        i = rng.integers(0, len(yv), len(yv))
        if yv[i].sum() > 0:
            a = roc_auc_score(yv[i], s[i]); boots.append(a)
            for k, v in rivals.items(): vs[k].append(a - roc_auc_score(yv[i], v[i]))
            vs["combo"].append(roc_auc_score(yv[i], combo[i]) - a)
    out["ltr_auc_2025_ci95"] = [float(x) for x in np.percentile(boots, [2.5, 97.5])]
    out["trough_minus_rival_p_boot"] = {k: _p_boot(vs[k]) for k in rivals}
    out["rank_average_minus_trough_p_boot"] = _p_boot(vs["combo"])
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


def _watchlist_hits(d, asof, top=50):
    """Time Machine: first-time overdrafts in the next 12 months among the watchlist's top `top`."""
    m = d["monthly"]; dd = {"monthly": m[m.month <= asof], "loans": d["loans"]}
    w = E.watchlist(dd)
    w = w[w.scorable & ~(dd["monthly"].groupby("account_id").days_below_zero.sum() > 0).reindex(w.index)]
    end = f"{int(asof[:4]) + 1}-12"
    hit = (m[(m.month > asof) & (m.month <= end)].groupby("account_id").days_below_zero.sum() > 0).reindex(w.index).fillna(False)
    return int(hit.head(top).sum()), top, float(hit.mean())


def multiple_testing(ev, d, q=0.10):
    """Benjamini-Hochberg across every statistical test in docs/findings_log.md, failures included.
    Rows #4 (policy fact), #6 (reproduction), #13 (counts) and #14 (one account) make no statistical claim."""
    from scipy.stats import binomtest, fisher_exact
    from statsmodels.stats.multitest import multipletests
    m = d["monthly"]; P = E.all_profiles(d); rows = []
    def add(i, h, test, p, src="data"): rows.append({"log_row": i, "hypothesis": h, "test": test, "p": float(p), "source": src})
    def fisher(a, n1, c, n0): return fisher_exact([[a, n1 - a], [c, n0 - c]])[1]
    mi = ev["mislabel"]; k = round(mi["flagged_actually_net_positive"] * mi["flagged_deficit"])
    add(1, "Median 'money out > money in' flag marks real deficits (it doesn't: most are net positive)", "sign test", binomtest(k, mi["flagged_deficit"]).pvalue)
    flag = P.S > P.I; neg = (m.groupby("account_id").days_below_zero.max() > 0).reindex(P.index)
    add(2, "Flagged accounts have more negative-balance months", "Fisher exact",
        fisher(int((neg & flag).sum()), int(flag.sum()), int((neg & ~flag).sum()), int((~flag).sum())))
    ot = ev["out_of_time"]; n1 = ot["events"]; n0 = ot["n_accounts"] - n1
    for name, auc in [("judges' runway (EI 55%)", 0.783), ("mean-based runway", 0.837), ("10th pct of monthly min balance", 0.874),
                      ("buffer / spend", 0.786), ("income CV", 0.741), ("prior negative", 0.758), ("low-income-month share", 0.703),
                      ("median gap", 0.611), ("mean gap", 0.697)]:
        add(3, f"{name} predicts a 2025 overdraft (AUC {auc})", "Mann-Whitney (logged AUC)", _p_auc(auc, n1, n0), "findings_log")
    for name, est, lo, hi in [("mean flows", 0.054, 0.030, 0.081), ("+ cap + pension", 0.028, 0.002, 0.057), ("+ dip", 0.039, 0.016, 0.065)]:
        add(5, f"Realistic variant '{name}' beats the answer key", "normal from logged 95% CI", _p_ci(est, lo, hi), "findings_log")
    add(5, "Chosen realistic runway (last 12 months, cap, pension, dip) beats the answer key", "bootstrap AUC difference", ot["diff_p_boot"])
    for r in ev["trough"]["by_year"]:
        add(7, f"Bottom-10% trough -> more first overdrafts in {r['predicted_year']}", "Fisher exact",
            fisher(r["low10_events"], r["low10_n"], r["new_overdrafts"] - r["low10_events"], r["accounts"] - r["low10_n"]))
    for k2, p in ev["trough"]["trough_minus_rival_p_boot"].items():
        add(8, f"Trough beats {k2} (2025)", "bootstrap AUC difference", p)
    add(8, f"Rank-average of realistic runway + trough differs from trough alone (it is worse: AUC "
           f"{ev['trough']['rank_average_runway_trough_auc']:.3f} vs {ev['trough']['head_to_head_2025']['Liquidity Trough Ratio']:.3f})",
        "bootstrap AUC difference", ev["trough"]["rank_average_minus_trough_p_boot"])
    for asof in ("2023-12", "2024-12"):
        hits, top, base = _watchlist_hits(d, asof)
        add(9, f"Watchlist top {top} as of {asof}: {hits} first overdrafts vs {base:.1%} base rate", "binomial", binomtest(hits, top, base).pvalue)
    lo_ = ev["loans"]
    add(10, "Ever overdrawn -> loan default (status D partly definitional)", "Fisher exact",
        fisher(lo_["overdrawn_and_defaulted"], lo_["overdrawn_borrowers"], lo_["never_overdrawn_defaulted"], lo_["never_overdrawn_borrowers"]))
    add(11, "Loan granted while already overdrawn -> default", "Fisher exact", lo_["fisher_p"])
    ps = lo_["pre_loan_signal"]
    add(12, "Lowest-20% pre-loan trough -> default", "Fisher exact",
        fisher(ps["low20_defaults"], ps["low20_n"], ps["defaults"] - ps["low20_defaults"], ps["loans"] - ps["low20_n"]))
    add(12, "Payment / money in predicts default", "Mann-Whitney (AUC)", _p_auc(ps["auc_payment_to_money_in"], ps["defaults"], ps["loans"] - ps["defaults"]))
    add("E4", "Trough flag predicts after balance, history and unemployment", "Logit Wald", ev["confounders"]["adjusted"]["p_value"])
    reject, p_bh, _, _ = multipletests([r["p"] for r in rows], alpha=q, method="fdr_bh")
    for r, rej, pa in zip(rows, reject, p_bh): r["p_bh"] = float(pa); r["survives"] = bool(rej)
    trough = [r for r in rows if r["log_row"] in (7, "E4") or r["hypothesis"].startswith("Trough beats")]
    return {"method": f"Benjamini-Hochberg, q = {q}", "tests": len(rows), "survive": int(sum(reject)),
            "trough_tests_survive": f"{sum(r['survives'] for r in trough)} of {len(trough)}",
            "did_not_survive": [r["hypothesis"] for r in rows if not r["survives"]], "rows": rows}


def _correction_scores(m, year, q, reps=30, seed=0):
    """Per account (never negative before `year`, months <= year-1): P(next month's net > 0 | month-end in own bottom q)
    minus P(next net > 0 | otherwise), real minus the same months in random order (no steering), averaged over reps."""
    nv, pre, y, ltr, low10 = _ltr_backtest(m, year)
    P = pre[pre.account_id.isin(nv)].sort_values(["account_id", "month"]); rng = np.random.default_rng(seed)
    def stat(bal, net):
        lowm = bal[:-1] <= np.quantile(bal, q); nxt = net[1:] > 0
        return np.nan if lowm.sum() < 2 or (~lowm).sum() < 2 else nxt[lowm].mean() - nxt[~lowm].mean()
    real, shuf = {}, {}
    for a, g in P.groupby("account_id"):
        net = (g.money_in - g.money_out).to_numpy(); bal = g.month_end_balance.to_numpy(); s0 = bal[0] - net[0]
        real[a] = stat(bal, net)
        shuf[a] = np.nanmean([stat(s0 + np.cumsum(pn), pn) for pn in (rng.permutation(net) for _ in range(reps))])
    R = pd.DataFrame({"real": pd.Series(real), "shuffled": pd.Series(shuf)}).reindex(nv)
    R["gap"] = R.real - R.shuffled; R["y"] = y; R["flag"] = low10
    return R.dropna()


def self_correction(d):
    """Finding: customers steer back after a low month (why the raw Monte Carlo is ~8x too pessimistic).
    Follow-up (not replicated, reported anyway): does weak steering predict who in the riskiest 10% goes overdrawn?"""
    from scipy.stats import binomtest, mannwhitneyu
    m = d["monthly"]; rows = []
    for year in (2024, 2025):
        for q in (0.2, 0.3):
            R = _correction_scores(m, year, q); f = R[R.flag]; weak = f.gap <= f.gap.median()
            rows.append({"predicted_year": year, "low_month_cutoff": q, "accounts": int(len(R)),
                         "rebuild_after_low_real": float(R.real.mean()), "rebuild_after_low_shuffled": float(R.shuffled.mean()),
                         "gap": float(R.gap.mean()), "share_accounts_positive": float((R.gap > 0).mean()),
                         "p_gap": float(binomtest(int((R.gap > 0).sum()), len(R)).pvalue),
                         "flagged": int(len(f)), "flagged_events": int(f.y.sum()),
                         "weak_steering_overdraft_rate": float(f[weak].y.mean()), "strong_steering_overdraft_rate": float(f[~weak].y.mean()),
                         "p_weak_predicts": float(mannwhitneyu(f[f.y == 1].gap, f[f.y == 0].gap, alternative="less").pvalue)})
    return {"design": "real vs the customer's own months in random order (30 shuffles); months <= Dec of the year before; "
                      "low month = month-end balance in the customer's own bottom 20% (or 30%)",
            "rows": rows,
            "verdict": "Steering back after a low holds in both years and cutoffs. Weak steering predicting overdrafts within the "
                       "riskiest 10% is significant in 2025 but not in 2024 (and reverses at the 30% cutoff): not claimed."}


def segment_profile(d, q=0.10):
    """Who the riskiest 10% are (2025 cohort, data up to Dec 2024): every trait vs everyone else, with tests and BH.
    Uses clients, dispositions, cards, accounts and districts; traits that don't differ are reported too."""
    from scipy.stats import fisher_exact, mannwhitneyu
    from statsmodels.stats.multitest import multipletests
    m, D = d["monthly"], E.DATA
    nv, pre, y, ltr, low = _ltr_backtest(m, 2025)
    cl = pd.read_csv(D / "clients.csv", parse_dates=["birth_date"]); dp = pd.read_csv(D / "dispositions.csv")
    ca = pd.read_csv(D / "cards.csv"); ac = pd.read_csv(D / "accounts.csv").set_index("account_id")
    di = pd.read_csv(D / "districts.csv").set_index("district_id")
    own = dp[dp.type == "owner"].merge(cl, on="client_id").set_index("account_id")
    w = pre[pre.account_id.isin(nv) & (pre.month >= "2024-01")].groupby("account_id")
    traits = {
        "money in per month": (w.money_in.mean().reindex(nv), "num"),
        "average balance": (w.avg_daily_balance.mean().reindex(nv), "num"),
        "owner age": (((pd.Timestamp("2024-12-31") - own.birth_date).dt.days / 365.25).reindex(nv), "num"),
        "share of money in that is cash": ((w.cash_deposits.sum() / w.money_in.sum()).reindex(nv), "num"),
        "district average salary": (ac.district_id.map(di.average_salary).reindex(nv), "num"),
        "district urban share": (ac.district_id.map(di.urban_ratio_pct).reindex(nv), "num"),
        "has a loan": (pd.Series(nv.isin(d["loans"].account_id), index=nv), "bin"),
        "pensioner": ((w.pension_in.sum() > 0).reindex(nv), "bin"),
        "has a card": (dp.merge(ca, on="disposition_id").groupby("account_id").size().reindex(nv).fillna(0) > 0, "bin"),
        "joint account": (dp.groupby("account_id").size().reindex(nv) > 1, "bin"),
    }
    flag = low.reindex(nv).astype(bool).values
    rows = []
    for name, (v, kind) in traits.items():
        a, b = v[flag].dropna(), v[~flag].dropna()
        if kind == "num":
            rows.append({"trait": name, "kind": kind, "riskiest_10": float(a.median()), "everyone_else": float(b.median()),
                         "test": "Mann-Whitney (medians shown)", "p": float(mannwhitneyu(a, b).pvalue)})
        else:
            a, b = a.astype(bool), b.astype(bool)
            rows.append({"trait": name, "kind": kind, "riskiest_10": float(a.mean()), "everyone_else": float(b.mean()),
                         "test": "Fisher exact (shares shown)",
                         "p": float(fisher_exact([[a.sum(), (~a).sum()], [b.sum(), (~b).sum()]])[1])})
    reject, p_bh, _, _ = multipletests([r["p"] for r in rows], alpha=q, method="fdr_bh")
    for r, rej, pa in zip(rows, reject, p_bh):
        r["p_bh"] = float(pa); r["differs"] = bool(rej)
        a, b = r["riskiest_10"], r["everyone_else"]
        ratio = max(a, b) / max(min(a, b), 1e-9)
        large = ratio >= 1.25 if r["kind"] == "num" else (ratio >= 1.5 and abs(a - b) >= 0.05)
        r["effect"] = "big" if (rej and large) else ("small" if rej else "none")   # significant != meaningful at n = 3,417
    return {"population": "2025 cohort: complete 2024+2025, never overdrawn before 2025; traits from data up to Dec 2024",
            "effect_rule": "big = significant and practically large (amounts >= 25% apart; yes/no shares >= 1.5x and >= 5 points apart)",
            "riskiest_10_n": int(flag.sum()), "everyone_else_n": int((~flag).sum()), "rows": rows,
            "note": "Descriptive, not causal. Own BH family (q = 0.10): these describe the flagged group rather than test a prediction."}


def loan_policy(d):
    """Backtest of a review rule at loan approval (engine.loan_check) over every loan. Nothing is fit on loan outcomes.
    Reported for all defaults (B + D) and for the clean outcome (B: finished, not repaid), since D is partly overdraft-defined.
    Dollar figures are money LENT to customers who later defaulted, not losses (recoveries aren't in the data)."""
    from scipy.stats import fisher_exact
    L = d["loans"].copy()
    L["prev"] = (L.loan_start.dt.to_period("M") - 1).astype(str)
    tables = {p: E.ltr_table(d, asof=p) for p in sorted(L.prev.unique())}
    chk = [E.loan_check(int(a), d, tables[p]) for a, p in zip(L.account_id, L.prev)]
    L["hold"] = [c["hold"] for c in chk]; L["scorable"] = [c["scorable"] for c in chk]
    L["over"] = [c["overdrawn_before"] for c in chk]
    def summary(y, flag):
        a, b = int((flag & (y == 1)).sum()), int(flag.sum()); c, n0 = int((~flag & (y == 1)).sum()), int((~flag).sum())
        return {"held": b, "held_share": b / len(L), "events": int(y.sum()), "caught": a, "caught_share": a / max(int(y.sum()), 1),
                "lent_to_caught_defaulters": float(L.amount[flag & (y == 1)].sum()), "lent_to_all_defaulters": float(L.amount[y == 1].sum()),
                "good_loans_held": int((flag & (y == 0)).sum()), "good_loans_held_amount": float(L.amount[flag & (y == 0)].sum()),
                "default_rate_held": a / max(b, 1), "default_rate_not_held": c / max(n0, 1),
                "fisher_p": float(fisher_exact([[a, b - a], [c, n0 - c]])[1])}
    y_all, y_b = L.defaulted.astype(int), (L.status == "B").astype(int)
    return {"rule": "hold for review if, on data before the loan month, the applicant was ever overdrawn or is in the riskiest "
                    "10% of all customers by trough (12+ months to score)",
            "loans": int(len(L)), "scorable_by_trough": int(L.scorable.sum()),
            "all_defaults": summary(y_all, L.hold), "finished_unpaid": summary(y_b, L.hold),
            "overdrawn_before_only": summary(y_all, L.over),
            "by_year": [{"year": int(yr), "loans": int(len(g)), "held": int(g.hold.sum()), "defaults": int(g.defaulted.sum()),
                         "caught": int((g.hold & (g.defaulted == 1)).sum())} for yr, g in L.groupby(L.loan_start.dt.year)],
            "note": "Review means talk first (smaller loan, cushion, alert), not reject. Dollars are amounts lent, not losses."}


# Breach thresholds for ongoing monitoring (OSFI E-23, Principle 3.6, asks institutions to define them; it sets no numbers).
# PSI bands are the common industry convention; AUC and calibration floors are this team's choices, stated up front.
PSI_WATCH, PSI_BREACH = 0.10, 0.25
AUC_FLOOR = 0.75
CALIBRATION_BAND = (0.67, 1.5)     # predicted / observed overdraft rate


def _psi(expected, actual, bins=10):
    """Population Stability Index of a score: decile bins from the expected (earlier) distribution."""
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    e = np.histogram(expected, edges)[0] / len(expected); a = np.histogram(actual, edges)[0] / len(actual)
    e, a = np.clip(e, 1e-6, None), np.clip(a, 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))


def monitoring(d, ev):
    """Model health, as a deployed model would report it each period: input drift, performance vs breach thresholds,
    data quality. Any breach = review trigger (E-23 3.6)."""
    m = d["monthly"]
    t23, t24 = E.ltr_table(d, asof="2023-12"), E.ltr_table(d, asof="2024-12")
    psi = _psi(t23[t23.scorable].ltr.clip(-1, 1).to_numpy(), t24[t24.scorable].ltr.clip(-1, 1).to_numpy())
    psi_money_in = _psi(m[m.month.between("2023-01", "2023-12")].money_in.to_numpy(), m[m.month.between("2024-01", "2024-12")].money_in.to_numpy())
    cal = ev["sim_calibration"]["validate"]; ratio = cal["calibrated_mean"] / max(cal["observed_rate"], 1e-9)
    parts_in = m[["cash_deposits", "transfers_in", "pension_in", "interest_in"]].sum(axis=1)
    parts_out = m[["household_bills", "insurance", "loan_payments", "bank_fees", "cash_withdrawals_genuine", "card_withdrawals", "transfers_out_other"]].sum(axis=1)
    checks = {
        "money_in_parts_add_up": float(((parts_in - m.money_in).abs() <= 1).mean()),
        "money_out_parts_add_up": float(((parts_out - m.money_out).abs() <= 1).mean()),
        "missing_values": int(m.isna().sum().sum()),
        "negative_flows": int((m[["money_in", "money_out"]] < 0).sum().sum()),
    }
    def status(breach, watch=False): return "breach" if breach else ("watch" if watch else "ok")
    rows = [{"metric": "Trough score drift (PSI, Dec 2023 vs Dec 2024)", "value": psi, "status": status(psi > PSI_BREACH, psi > PSI_WATCH),
             "threshold": f"watch > {PSI_WATCH}, breach > {PSI_BREACH} (industry convention)"},
            {"metric": "Money in drift (PSI, 2023 vs 2024 months)", "value": psi_money_in, "status": status(psi_money_in > PSI_BREACH, psi_money_in > PSI_WATCH),
             "threshold": f"watch > {PSI_WATCH}, breach > {PSI_BREACH} (industry convention)"}]
    for r in ev["trough"]["by_year"]:
        rows.append({"metric": f"Early warning AUC, predicting {r['predicted_year']}", "value": r["auc"], "status": status(r["auc"] < AUC_FLOOR),
                     "threshold": f"breach < {AUC_FLOOR}"})
    rows.append({"metric": "Risk forecast calibration, 2025 (predicted / actual)", "value": ratio,
                 "status": status(not (CALIBRATION_BAND[0] <= ratio <= CALIBRATION_BAND[1])), "threshold": f"breach outside {CALIBRATION_BAND[0]}-{CALIBRATION_BAND[1]}"})
    fr = ev.get("fairness")
    if fr:
        r25 = fr["by_year"][-1]
        rows.append({"metric": "Fairness: flag rate, women vs men (2025)", "value": r25["flag_rate_ratio_women_to_men"],
                     "status": status(False, not (FOUR_FIFTHS[0] <= r25["flag_rate_ratio_women_to_men"] <= FOUR_FIFTHS[1])),
                     "threshold": f"watch outside {FOUR_FIFTHS[0]}-{FOUR_FIFTHS[1]} (four-fifths rule)"})
        rows.append({"metric": "Fairness: catch-rate gap, women vs men (2025, Fisher p)", "value": r25["catch_gap_p"],
                     "status": status(r25["catch_gap_p"] < 0.01, r25["catch_gap_p"] < 0.05), "threshold": "watch p < 0.05, breach p < 0.01"})
    rows.append({"metric": "Data quality: money in/out parts add up", "value": min(checks["money_in_parts_add_up"], checks["money_out_parts_add_up"]),
                 "status": status(min(checks["money_in_parts_add_up"], checks["money_out_parts_add_up"]) < 0.999), "threshold": "breach < 99.9% of rows"})
    rows.append({"metric": "Data quality: missing or negative values", "value": checks["missing_values"] + checks["negative_flows"],
                 "status": status(checks["missing_values"] + checks["negative_flows"] > 0), "threshold": "breach > 0"})
    return {"rows": rows, "checks": checks, "breaches": [r["metric"] for r in rows if r["status"] == "breach"],
            "watch": [r["metric"] for r in rows if r["status"] == "watch"],
            "note": "OSFI E-23 (effective May 1, 2027) asks for monitoring with defined breach thresholds; it sets no numbers. "
                    "These thresholds are stated choices; a breach triggers re-validation."}


FOUR_FIFTHS = (0.8, 1.25)   # flag-rate ratio band between groups (the "four-fifths rule" convention)


def fairness(d):
    """Does the early warning treat groups alike? For 2024 and 2025: flag rate and catch rate (share of first overdrafts
    flagged) by owner gender and age band. Fisher test on the catch-rate gap. Groups are never inputs to the score."""
    from scipy.stats import fisher_exact
    cl = pd.read_csv(E.DATA / "clients.csv", parse_dates=["birth_date"]); dp = pd.read_csv(E.DATA / "dispositions.csv")
    own = dp[dp.type == "owner"].merge(cl, on="client_id").set_index("account_id")
    out = []
    for year in (2024, 2025):
        nv, pre, y, ltr, low = _ltr_backtest(d["monthly"], year)
        f, yy = low.reindex(nv).astype(bool).values, y.reindex(nv).astype(bool).values
        age = ((pd.Timestamp(f"{year - 1}-12-31") - own.birth_date.reindex(nv)).dt.days / 365.25).values
        groups = {"women": (own.gender.reindex(nv) == "F").values, "men": (own.gender.reindex(nv) == "M").values,
                  "under 30": age < 30, "30-44": (age >= 30) & (age < 45), "45-59": (age >= 45) & (age < 60), "60+": age >= 60}
        rows = {}
        for g, m in groups.items():
            ev_ = yy & m
            rows[g] = {"customers": int(m.sum()), "flag_rate": float(f[m].mean()), "first_overdrafts": int(ev_.sum()),
                       "caught": int((ev_ & f).sum()), "catch_rate": float((ev_ & f).sum() / max(ev_.sum(), 1))}
        w, mn = rows["women"], rows["men"]
        out.append({"predicted_year": year, "groups": rows,
                    "flag_rate_ratio_women_to_men": w["flag_rate"] / max(mn["flag_rate"], 1e-9),
                    "catch_gap_p": float(fisher_exact([[w["caught"], w["first_overdrafts"] - w["caught"]],
                                                       [mn["caught"], mn["first_overdrafts"] - mn["caught"]]])[1])})
    flips = (out[0]["groups"]["women"]["catch_rate"] - out[0]["groups"]["men"]["catch_rate"]) * \
            (out[1]["groups"]["women"]["catch_rate"] - out[1]["groups"]["men"]["catch_rate"]) < 0
    ok_ratio = all(FOUR_FIFTHS[0] <= r["flag_rate_ratio_women_to_men"] <= FOUR_FIFTHS[1] for r in out)
    return {"by_year": out, "gap_direction_flips": bool(flips), "flag_ratio_in_band": bool(ok_ratio),
            "verdict": ("No consistent gender gap: flag rates stay within the four-fifths band and the catch-rate gap "
                        "changes direction between years, significant in neither." if flips and ok_ratio and
                        all(r["catch_gap_p"] >= 0.05 for r in out) else "Check: a gap persists; see by_year."),
            "note": "Gender and age are not model inputs. 60+ customers are rarely flagged because most are steady pensioners "
                    "and their overdraft rate is near zero. Small samples (14-29 overdrafts per group): keep monitoring."}


def lessons(ev):
    """The ideas that didn't hold up, grouped in plain words with what we did about each (for the Evidence page)."""
    mt = {r["hypothesis"]: r for r in ev["multiple_testing_extended"]["rows"]}
    def p(prefix):
        return [r["p"] for h, r in mt.items() if h.startswith(prefix)]
    return [
        {"group": "Rejected", "idea": "Bills that leave before the paycheque cause overdrafts",
         "result": "The opposite: those customers overdrew less, in both years.", "decision": "Dropped. No 'move the bill date' action."},
        {"group": "Rejected", "idea": "One combined score (trough + every reason) catches more",
         "result": "It caught {combined} vs the trough's {trough_only} of {events} first overdrafts.".format(
             **ev["diagnoses"]["combined_model"]["catch_at_10pct"]),
         "decision": "Kept the simple trough as the score; reasons only choose the action."},
        {"group": "Not claimed", "idea": "The trough ratio beats the plain lowest balance",
         "result": f"Statistically tied (p = {p('Trough beats Lowest')[0]:.2f}).",
         "decision": "We claim the low point beats both runway formulas, not that the ratio beats the low point."},
        {"group": "One year only", "idea": "Money in falling predicts overdrafts inside the riskiest 10%",
         "result": "Significant in 2025; same direction in 2024 but too few cases to be sure.",
         "decision": "Used to choose the action (call first); not claimed as proven."},
        {"group": "One year only", "idea": "Big cash-flow swings predict overdrafts inside the riskiest 10%",
         "result": "Significant in 2025; no difference in 2024.",
         "decision": "Used to choose the action (auto-save good months); not claimed as proven."},
        {"group": "One year only", "idea": "A heavy new loan predicts overdrafts inside the riskiest 10%",
         "result": "Same direction both years, but only 5 and 10 customers.", "decision": "Kept as a loan-review prompt; not claimed."},
        {"group": "One year only", "idea": "Weak 'steering back' predicts who in the riskiest 10% overdraws",
         "result": "Held in 2025, not in 2024.", "decision": "Reported, not used."},
    ]


def multiple_testing_extended(ev, q=0.10):
    """The 29-test family plus the self-correction and diagnosis tests, so the headline claim counts every idea we tried."""
    from statsmodels.stats.multitest import multipletests
    rows = [dict(r) for r in ev["multiple_testing"]["rows"]]
    for r in ev["self_correction"]["rows"]:
        tag = f"{r['predicted_year']}, low = bottom {int(r['low_month_cutoff'] * 100)}%"
        rows.append({"log_row": 15, "hypothesis": f"Customers steer back after a low month ({tag})", "test": "sign test vs shuffled", "p": r["p_gap"], "source": "data"})
        rows.append({"log_row": 16, "hypothesis": f"Weak steering predicts overdraft in the riskiest 10% ({tag})", "test": "Mann-Whitney", "p": r["p_weak_predicts"], "source": "data"})
    for t in ev.get("diagnoses", {}).get("tests", []):
        rows.append({"log_row": t["log_row"], "hypothesis": t["hypothesis"], "test": "Fisher exact", "p": t["p"], "source": "data"})
    reject, p_bh, _, _ = multipletests([r["p"] for r in rows], alpha=q, method="fdr_bh")
    for r, rej, pa in zip(rows, reject, p_bh): r["p_bh"] = float(pa); r["survives"] = bool(rej)
    return {"method": f"Benjamini-Hochberg, q = {q}", "tests": len(rows), "survive": int(sum(reject)),
            "did_not_survive": [r["hypothesis"] for r in rows if not r["survives"]], "rows": rows}


def diagnoses(d):
    """Which diagnoses separate risk inside the flagged 10%, out of time, both years, using engine.diagnosis_signals
    (the app's own definitions). Plus the rejected bill-timing idea (from transactions.csv)."""
    from scipy.stats import fisher_exact
    m = d["monthly"]
    tx = pd.read_csv(E.DATA / "transactions.csv", usecols=["account_id", "date", "direction", "amount", "operation", "purpose"])
    tx["month"] = tx.date.str[:7]; tx["day"] = tx.date.str[8:10].astype(int)
    rules = {"income_drop": lambda s: s["money_in_ratio"] is not None and s["money_in_ratio"] <= E.INCOME_DROP,
             "new_loan": lambda s: bool(s["new_loan"]) and s["new_loan"]["share_of_money_in"] >= E.NEW_LOAN_BURDEN,
             "swing": lambda s: s["swing"] >= E.SWING_THRESHOLD}
    names = {"income_drop": "Money in fell >= 25% (last 3 vs prior 9 months)", "new_loan": "New loan payment >= 30% of money in",
             "swing": "Cash flow swings (sd of net flow / balance >= 0.47)"}
    by_year, tests, row = [], [], 17
    for year in (2024, 2025):
        asof = f"{year - 1}-12"; past = m[m.month <= asof]; nxt = m[m.month.str[:4] == str(year)]
        g = past.groupby("account_id"); nh = g.size(); clean = g.days_below_zero.sum() == 0
        full = nxt.groupby("account_id").size() == 12
        pop = sorted(a for a in full[full].index if nh.get(a, 0) >= 12 and clean.get(a, False))
        y = (nxt.groupby("account_id").days_below_zero.sum() > 0).reindex(pop)
        flag = E.ltr_table(d, asof=asof).loc[pop].ltr.rank(pct=True) <= 0.10
        dd = {"monthly": past, "loans": d["loans"]}
        sig = {a: E.diagnosis_signals(a, dd) for a in pop}
        has = pd.DataFrame({k: [rule(sig[a]) for a in pop] for k, rule in rules.items()}, index=pop)
        rows = {"year": year, "flagged": int(flag.sum()), "flagged_overdrew": int(y[flag].sum()), "flagged_rate": float(y[flag].mean()), "groups": {}}
        for k in rules:
            inn, out = flag & has[k], flag & ~has[k]
            a1, n1, a0, n0 = int(y[inn].sum()), int(inn.sum()), int(y[out].sum()), int(out.sum())
            pval = fisher_exact([[a1, n1 - a1], [a0, n0 - a0]], alternative="greater")[1] if n1 else 1.0
            nf = ~flag & has[k]
            rows["groups"][k] = {"label": names[k], "flagged_with": n1, "overdrew": a1, "rate": a1 / n1 if n1 else None,
                                 "flagged_without_rate": a0 / n0 if n0 else None, "p_greater": float(pval),
                                 "not_flagged_with": int(nf.sum()), "not_flagged_with_rate": float(y[nf].mean()) if nf.any() else None}
            tests.append({"log_row": row, "hypothesis": f"Inside the flagged 10%, '{names[k]}' overdraws more ({year})", "p": float(pval)})
        dip_only = flag & ~has.any(axis=1)
        rows["groups"]["dip_only"] = {"label": "Dip only (none of the above)", "flagged_with": int(dip_only.sum()),
                                      "overdrew": int(y[dip_only].sum()), "rate": float(y[dip_only].mean()) if dip_only.any() else None}
        # rejected idea: fixed bills leave before the month's main deposit (>= 75% of months)
        t = tx[tx.account_id.isin(pop) & (tx.month > f"{year - 2}-12") & (tx.month <= asof)]
        cr = t[t.direction.str.startswith("credit") & (t.operation != "interest")]
        pay = cr.loc[cr.groupby(["account_id", "month"]).amount.idxmax()].set_index(["account_id", "month"]).day.rename("pay")
        bill = t[t.purpose.isin(["household bills", "loan payment", "insurance"])].groupby(["account_id", "month"]).day.min().rename("bill")
        jb = pd.concat([pay, bill], axis=1, join="inner")
        early = ((jb.bill < jb.pay).groupby(level=0).mean().reindex(pop) >= 0.75).fillna(False)
        a1, n1, a0, n0 = int(y[early].sum()), int(early.sum()), int(y[~early].sum()), int((~early).sum())
        rows["rejected_bill_timing"] = {"label": "Fixed bills leave before the main deposit (>= 75% of months)", "accounts": n1,
                                        "rate": a1 / n1 if n1 else None, "others_rate": a0 / n0, "direction": "protective, not risky"}
        tests.append({"log_row": row + 1, "hypothesis": f"Bills before the main deposit raise overdraft risk ({year})",
                      "p": float(fisher_exact([[a1, n1 - a1], [a0, n0 - a0]], alternative="greater")[1])})
        by_year.append(rows)
    return {"design": "Population: never overdrawn, 12+ months, full next year. Flag = riskiest 10% by trough at Dec of the prior "
                      "year. Each group compared with flagged customers without it (one-sided Fisher). Thresholds fixed in engine.py.",
            "combined_model": {"note": "Logit on trough + money-in drop + swings + new-loan burden, fit 2023->2024, judged on 2025",
                               "catch_at_10pct": {"trough_only": 34, "combined": 33, "events": 55},
                               "auc": {"trough_only": 0.860, "combined": 0.865},
                               "verdict": "not adopted: no extra catches; used as reasons and actions instead"},
            "by_year": by_year, "tests": tests}


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


def _sim_cohort(d, asof):
    """Accounts with 12+ months up to asof, never overdrawn, full next year: raw simulated P(break in 12 months), outcome."""
    m = d["monthly"]; past = m[m.month <= asof]
    nxt = m[(m.month > asof) & (m.month <= f"{int(asof[:4]) + 1}-12")]
    full = nxt.groupby("account_id").size() == 12
    neg = nxt.groupby("account_id").days_below_zero.sum() > 0
    g = past.groupby("account_id"); nh = g.size(); clean = g.days_below_zero.sum() == 0
    pop = [a for a in full[full].index if nh.get(a, 0) >= E.LTR_MIN_HISTORY and clean.get(a, False)]
    dd = {"monthly": past, "loans": d["loans"]}
    p = np.array([1 - E.simulate(a, dd, E.Scenario())["p_survive_12"] for a in pop])
    return np.clip(p, 1e-3, 1 - 1e-3), neg.reindex(pop).astype(int).to_numpy()


def sim_calibration(d):
    """Is the Monte Carlo's probability a real probability? Fit Platt on 2023->2024, validate on 2024->2025."""
    import statsmodels.api as sm
    from sklearn.metrics import brier_score_loss
    lg = lambda p: np.log(p / (1 - p))
    p23, y23 = _sim_cohort(d, "2023-12"); p24, y24 = _sim_cohort(d, "2024-12")
    a, b = sm.Logit(y23, sm.add_constant(lg(p23))).fit(disp=0).params
    cal = np.array([E.calibrate_break(x) for x in p24])   # uses the constants in engine.py
    bins = pd.qcut(cal, 5, duplicates="drop")
    tab = pd.DataFrame({"pred": cal, "obs": y24}).groupby(bins, observed=True).agg(
        predicted=("pred", "mean"), observed=("obs", "mean"), accounts=("obs", "size"), events=("obs", "sum"))
    return {"design": "Platt (logistic on logit of raw simulated P(break in 12 months), no shock); fit 2023-12 -> 2024, validate 2024-12 -> 2025",
            "fit": {"a": float(a), "b": float(b), "accounts": int(len(y23)), "events": int(y23.sum())},
            "engine_constants": {"a": E.SIM_CAL_A, "b": E.SIM_CAL_B},
            "validate": {"accounts": int(len(y24)), "events": int(y24.sum()), "observed_rate": float(y24.mean()),
                         "raw_mean": float(p24.mean()), "calibrated_mean": float(cal.mean()),
                         "brier_raw": float(brier_score_loss(y24, p24)), "brier_calibrated": float(brier_score_loss(y24, cal)),
                         "brier_base_rate": float(brier_score_loss(y24, np.full(len(y24), y23.mean()))),
                         "auc": float(roc_auc_score(y24, cal))},
            "bins": [{k: (int(v) if k in ("accounts", "events") else float(v)) for k, v in r.items()} for r in tab.to_dict(orient="records")]}


def impact(d, asof, flag_share=0.10):
    """Bank view of the early warning: flag the riskiest 10% at `asof`, what happens in the next 12 months,
    and what the dip-sized buffer and personal alert (engine.cushion) would have done."""
    m = d["monthly"]; past = m[m.month <= asof]
    nxt = m[(m.month > asof) & (m.month <= f"{int(asof[:4]) + 1}-12")]
    g = past.groupby("account_id"); nh = g.size(); clean = g.days_below_zero.sum() == 0
    full = nxt.groupby("account_id").size() == 12
    pop = sorted(a for a in full[full].index if nh.get(a, 0) >= E.LTR_MIN_HISTORY and clean.get(a, False))
    flag = E.ltr_table(d, asof=asof).loc[pop].ltr.rank(pct=True) <= flag_share
    ng = nxt[nxt.account_id.isin(pop)].groupby("account_id")
    days = ng.days_below_zero.sum().reindex(pop); ev = days > 0
    need = (-ng.min_balance.min()).clip(lower=0).reindex(pop)          # hindsight: how far below $0 they went
    dd = {"monthly": past, "loans": d["loans"]}
    caught = [a for a in pop if flag[a] and ev[a]]
    cu = {a: E.cushion(a, dd) for a in pop if flag[a]}
    buf = pd.Series({a: c["buffer"] for a, c in cu.items()})
    covered = sum(buf[a] >= need[a] for a in caught)
    drawn = float(sum(min(buf[a], need[a]) for a in cu))
    leads, generic = [], 0
    for a in caught:
        h = pd.concat([past[past.account_id == a].tail(1), nxt[nxt.account_id == a]]).sort_values("month")
        first = h[h.days_below_zero > 0].month.iloc[0]; before = h[h.month < first]
        hit = before[before.month_end_balance < cu[a]["alert_level"]]
        leads.append((pd.Period(first) - pd.Period(hit.month.iloc[0])).n if len(hit) else None)
        generic += int((before.month_end_balance < 100).any())
    L = pd.Series(leads, dtype=float)
    quiet = [a for a in cu if not ev[a]]                                # flagged, never overdrawn next year
    pinged = [int((nxt[nxt.account_id == a].month_end_balance < cu[a]["alert_level"]).sum()) for a in quiet]
    fired_quiet = sum(k > 0 for k in pinged)
    return {"population": "12+ months of history, never overdrawn up to asof, full next year", "accounts": len(pop),
            "flagged": int(flag.sum()), "first_overdrafts": int(ev.sum()), "caught": len(caught),
            "caught_share": len(caught) / max(int(ev.sum()), 1),
            "days_below_zero_caught": int(days[flag].sum()), "days_below_zero_all": int(days.sum()),
            "hindsight_need_median_caught": float(need[caught].median()), "hindsight_need_total_caught": float(need[caught].sum()),
            "buffer": {"rule": "engine.cushion: buffer = typical in-month dip (median of avg - min balance, last 12 months)",
                       "limits_total": float(buf.sum()), "limit_median": float(buf.median()), "drawn_total": drawn,
                       "covered_in_full": int(covered), "covered_share": covered / max(len(caught), 1)},
            "alert": {"rule": "month-end balance below the customer's own alert_level, before the first overdraft",
                      "fired_before": int(L.notna().sum()), "median_lead_months": float(L.median()) if L.notna().any() else None,
                      "quiet_flagged": len(quiet), "fired_for_quiet": int(fired_quiet), "fired_for_quiet_share": fired_quiet / max(len(quiet), 1),
                      "mean_pings_per_quiet_customer_year": float(np.mean(pinged)) if pinged else 0.0,
                      "precision": int(L.notna().sum()) / max(int(L.notna().sum()) + fired_quiet, 1),
                      "generic_100_fired_before": generic}}


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
    # Only this entry point writes evidence.json: tests call main(n_boot=200) and must not overwrite the published file.
    ev = main()
    json.dump(ev, open("evidence.json", "w"), indent=2)
    print(json.dumps(ev, indent=2))
