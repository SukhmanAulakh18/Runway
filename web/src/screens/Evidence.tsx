import { useQuery } from "@tanstack/react-query";
import { api, money, pct } from "../api";
import { Legend, PairBars, SurvivalChart } from "../charts";
import { Failed, Kpi, Loading } from "./ui";

export default function Evidence() {
  const q = useQuery({ queryKey: ["evidence"], queryFn: api.evidence, staleTime: Infinity });
  if (q.isPending) return <main className="page"><Loading h={140} /><Loading h={300} /></main>;
  if (q.isError) return <main className="page"><Failed error={q.error} /></main>;
  const e = q.data;
  const years = e.trough.by_year.map((r: { predicted_year: number; low10_rate: number; rest_rate: number }) => ({ x: String(r.predicted_year), a: r.low10_rate, b: r.rest_rate }));
  const rr = e.trough.by_year.map((r: { risk_ratio: number }) => r.risk_ratio);
  const cal = e.sim_calibration.validate;
  const bins = e.sim_calibration.bins.map((b: { predicted: number; observed: number }, i: number) => ({ x: `Group ${i + 1}`, a: b.predicted, b: b.observed }));
  const cf = e.confounders.adjusted, mt = e.multiple_testing_extended ?? e.multiple_testing, L = e.loans;
  type SC = { predicted_year: number; low_month_cutoff: number; rebuild_after_low_real: number; rebuild_after_low_shuffled: number; share_accounts_positive: number };
  const steer: SC[] = (e.self_correction?.rows ?? []).filter((r: SC) => r.low_month_cutoff === 0.2);
  const steerBars = steer.map((r) => ({ x: String(r.predicted_year - 1), a: r.rebuild_after_low_real, b: r.rebuild_after_low_shuffled }));

  return (
    <main className="page fade">
      <div>
        <p className="eyebrow">05 · Why trust it</p>
        <h1 className="title">Tested on years the model never saw. <em>Reported even where it failed.</em></h1>
      </div>

      <section className="grid g4">
        <div className="card"><Kpi label="Findings that survive multiple-testing correction" value={`${mt.survive} of ${mt.tests}`} note="Benjamini–Hochberg, q = 0.10" /></div>
        <div className="card"><Kpi label="Odds ratio after controls" value={`${cf.odds_ratio.toFixed(1)}×`} note={`95% CI ${cf.or_ci95[0].toFixed(1)}–${cf.or_ci95[1].toFixed(1)}; balance size, account age, unemployment`} /></div>
        <div className="card"><Kpi label="Risk forecast: predicted vs actual, 2025" value={`${pct(cal.calibrated_mean, 1)} vs ${pct(cal.observed_rate, 1)}`} note={`AUC ${cal.auc.toFixed(2)}; Brier ${cal.brier_calibrated.toFixed(4)} beats the base rate ${cal.brier_base_rate.toFixed(4)}`} /></div>
        <div className="card"><Kpi label="Ever-overdrawn borrowers who defaulted" value={`${L.overdrawn_and_defaulted} of ${L.overdrawn_borrowers}`} note={`${L.pre_loan_overdrawn} of ${L.pre_loan_overdrawn} lent to while already overdrawn defaulted (p = ${L.fisher_p.toExponential(1)})`} /></div>
      </section>

      {e.out_of_time && e.mislabel && e.ei_cap && e.formula_holes && (
        <section className="card">
          <h2>Our runway vs the judges' formula: better at predicting overdrafts, and why</h2>
          <p className="sub">The judges' formula is kept exactly (it is the answer key). These are the holes our realistic runway fixes, each tested on the data.</p>
          <table className="tbl" style={{ marginTop: 8 }}><thead><tr><th>What we tested</th><th>Judges' formula</th><th>Realistic runway</th></tr></thead>
            <tbody>
              <tr><td>Predicting who goes overdrawn in 2025 (out of time, {e.out_of_time.n_accounts.toLocaleString()} customers)</td>
                <td>AUC {e.out_of_time.auc_answer_key.toFixed(2)}</td>
                <td><b>AUC {e.out_of_time.auc_realistic.toFixed(2)}</b> (+{e.out_of_time.diff.toFixed(3)}, 95% CI {e.out_of_time.diff_ci95[0].toFixed(3)}–{e.out_of_time.diff_ci95[1].toFixed(3)}, p = {e.out_of_time.diff_p_boot.toFixed(3)})</td></tr>
              <tr><td>Customers the formula labels "in deficit" (typical money out above money in)</td>
                <td>{pct(e.mislabel.flagged_share)} of customers</td>
                <td>{pct(e.mislabel.flagged_actually_net_positive)} of them actually had more money in than out; {pct(e.mislabel.flagged_balance_grew)} saw their balance grow</td></tr>
              <tr><td>EI is capped at {money(e.ei_cap.ei_monthly_max)}/month: {pct(e.ei_cap.capped_share)} of customers would hit the cap</td>
                <td>{pct(e.ei_cap.capped_survive6_card)} of them last 6 months on a job loss</td>
                <td><b>{pct(e.ei_cap.capped_survive6_real)}</b> do</td></tr>
              <tr><td>EI stops after 6 months (the formula pays it forever)</td>
                <td>{pct(e.formula_holes.ei_forever.survive12_formula)} last 12 months on a job loss</td>
                <td><b>{pct(e.formula_holes.ei_forever.survive12_ei_stops_6)}</b> do; {e.formula_holes.ei_forever.flip_from_no_shortfall} customers lose their "no shortfall"</td></tr>
            </tbody></table>
        </section>
      )}

      {e.monitoring && (
        <details className="card fold">
          <summary><h2>Model health: {e.monitoring.breaches.length === 0 ? "no breaches" : `${e.monitoring.breaches.length} breach${e.monitoring.breaches.length > 1 ? "es" : ""}, re-validate`}</h2>
            <span className="sub">{e.monitoring.rows.length} monitors (drift, accuracy, calibration, fairness, data quality) against stated thresholds. Show them</span></summary>
          <p className="sub">What a deployed model reports each period: input drift, accuracy and data quality against stated thresholds. {e.monitoring.note}</p>
          <table className="tbl"><thead><tr><th>Monitor</th><th className="num">Value</th><th>Threshold</th><th>Status</th></tr></thead>
            <tbody>{(e.monitoring.rows as { metric: string; value: number; threshold: string; status: string }[]).map((r) => (
              <tr key={r.metric}><td>{r.metric}</td>
                <td className="num">{r.metric.startsWith("Data quality: money") ? pct(r.value, 1) : r.metric.startsWith("Data quality") ? String(r.value) : r.value.toFixed(3)}</td>
                <td className="muted">{r.threshold}</td>
                <td>{r.status === "ok" ? <span className="chip good">OK</span> : r.status === "watch" ? <span className="chip amber">Watch</span> : <span className="chip warn">Breach</span>}</td></tr>))}</tbody></table>
          <p className="sub" style={{ marginTop: 8 }}>Model documentation in the OSFI E-23 format: docs/MODEL_CARD.md. Every pull request is checked by CI.</p>
        </details>
      )}

      <section className="grid g2">
        <div className="card">
          <h2>The riskiest 10% are {Math.min(...rr).toFixed(0)}–{Math.max(...rr).toFixed(0)}× likelier to have a first overdraft, every year</h2>
          <p className="sub" style={{ marginBottom: 8 }}>Scored on December data, outcome the next year. Only customers never overdrawn before.</p>
          <PairBars data={years} a={{ key: "a", name: "Riskiest 10% by trough" }} b={{ key: "b", name: "Everyone else" }} />
          <Legend items={[{ label: "Riskiest 10% by trough", kind: "ours" }, { label: "Everyone else", kind: "soft" }]} />
        </div>
        <div className="card">
          <h2>When we say {pct(cal.calibrated_mean, 1)} chance, about that many go overdrawn</h2>
          <p className="sub" style={{ marginBottom: 8 }}>Monte Carlo calibrated on 2023→2024, checked on 2024→2025, by risk group. Raw simulation said {pct(cal.raw_mean)}: 8× too pessimistic, so we calibrated it.</p>
          <PairBars data={bins} a={{ key: "a", name: "Predicted" }} b={{ key: "b", name: "Actually overdrawn", color: "#0f172a" }} />
          <Legend items={[{ label: "Predicted", kind: "ours" }, { label: "Actually overdrawn", kind: "ink" }]} />
        </div>
      </section>

      {steer.length > 0 && (
        <section className="grid g-7-5" style={{ alignItems: "start" }}>
          <div className="card">
            <h2>After a low month, {pct(Math.min(...steer.map((r) => r.share_accounts_positive)))} of customers steer back faster than chance</h2>
            <p className="sub" style={{ marginBottom: 8 }}>How much more often money in beats money out the month after a low than after a normal month (percentage points). Real months vs the same months in random order: customers aren't a random walk.</p>
            <PairBars data={steerBars} a={{ key: "a", name: "Real customers" }} b={{ key: "b", name: "Same months, random order" }} fmt={(v) => (Math.round(v * 100) === 0 ? "0" : `+${Math.round(v * 100)} pts`)} />
            <Legend items={[{ label: "Real customers", kind: "ours" }, { label: "Same months, random order", kind: "soft" }]} />
          </div>
          <div className="card">
            <h2>Why it matters</h2>
            <p style={{ margin: "8px 0" }}>A simulation that replays months in random order can't steer back, so it predicted {pct(cal.raw_mean)} would go overdrawn when {pct(cal.observed_rate, 1)} did. That's why we calibrate it, and why the dip, not the average, is what to watch.</p>
            <p className="callout">Follow-up we don't claim: weak steering predicting who in the riskiest 10% goes overdrawn held in 2025 but not in 2024.</p>
          </div>
        </section>
      )}

      {e.loan_policy && (() => {
        const lp = e.loan_policy, rows = [["All defaults (finished unpaid + running in debt)", lp.all_defaults], ["Finished unpaid only (the clean outcome)", lp.finished_unpaid]] as const;
        return (
          <section className="card">
            <h2>A credit check that uses the finding: held loans default {(lp.all_defaults.default_rate_held / lp.all_defaults.default_rate_not_held).toFixed(1)}× as often</h2>
            <p className="sub" style={{ marginBottom: 8 }}>{lp.rule}. {lp.loans} loans; {lp.scorable_by_trough} had 12+ months to score. {lp.note}</p>
            <table className="tbl"><thead><tr><th>Outcome</th><th className="num">Held for review</th><th className="num">Defaults caught</th><th className="num">Default rate: held vs not</th><th className="num">Good loans held</th><th className="num">p</th></tr></thead>
              <tbody>{rows.map(([name, r]) => (
                <tr key={name}><td>{name}</td><td className="num">{r.held} ({pct(r.held_share)})</td><td className="num">{r.caught} of {r.events}</td>
                  <td className="num">{pct(r.default_rate_held)} vs {pct(r.default_rate_not_held, 1)}</td><td className="num">{r.good_loans_held}</td>
                  <td className="num">{r.fisher_p < 0.001 ? "< 0.001" : r.fisher_p.toFixed(3)}</td></tr>))}</tbody></table>
          </section>
        );
      })()}

      {e.segment && (
        <details className="card fold">
          <summary><h2>Who the riskiest 10% are: not poor, but running hot</h2><span className="sub">3 big differences (money in, loans, pensioners); where they live doesn't matter. Show all {e.segment.rows.length} traits</span></summary>
          <p className="sub" style={{ marginBottom: 8 }}>{e.segment.riskiest_10_n} flagged vs {e.segment.everyone_else_n} others (Dec 2024 data). Medians for amounts, shares for yes/no. Multiple-testing corrected.</p>
          <table className="tbl"><thead><tr><th>Trait</th><th className="num">Riskiest 10%</th><th className="num">Everyone else</th><th>Difference</th></tr></thead>
            <tbody>{(e.segment.rows as { trait: string; kind: string; riskiest_10: number; everyone_else: number; differs: boolean; effect?: string }[]).map((r) => {
              // explicit per-trait formats ("average" contains "age", "urban share" is already a percent)
              const f = (v: number) => r.kind === "bin" || r.trait === "share of money in that is cash" ? pct(v, 1)
                : r.trait === "owner age" ? `${v.toFixed(0)} yrs` : r.trait === "district urban share" ? `${v.toFixed(1)}%` : money(v);
              return <tr key={r.trait}><td>{r.trait}</td><td className="num">{f(r.riskiest_10)}</td><td className="num">{f(r.everyone_else)}</td>
                <td>{r.effect === "big" ? <span className="chip ours">Big difference</span> : r.effect === "small" ? <span className="chip">Small (real but minor)</span> : <span className="chip">No difference</span>}</td></tr>;
            })}</tbody></table>
        </details>
      )}

      {e.diagnoses && (
        <details className="card fold">
          <summary><h2>Why they're at risk: which reasons hold up inside the riskiest 10%</h2><span className="sub">Each reason picks the action (call, auto-save, loan review, alert); money in falling and big swings held in 2025. Show the table</span></summary>
          <p className="sub">Each reason picks an action. Overdraft rate the next year for flagged customers with the reason vs flagged customers without it.
            Combining these reasons with the trough did not catch more overdrafts ({e.diagnoses.combined_model.catch_at_10pct.combined} vs {e.diagnoses.combined_model.catch_at_10pct.trough_only} of {e.diagnoses.combined_model.catch_at_10pct.events}), so they choose the action, they don't replace the score.</p>
          <table className="tbl"><thead><tr><th>Reason → action</th><th className="num">2024</th><th className="num">2025</th></tr></thead>
            <tbody>{(["income_drop", "swing", "new_loan", "dip_only"] as const).map((k) => {
              const [a, b] = e.diagnoses.by_year.map((y: { groups: Record<string, { label: string; rate: number | null; flagged_without_rate?: number | null; flagged_with: number; p_greater?: number }> }) => y.groups[k]);
              const cell = (g: typeof a) => g.rate == null ? "–" : `${pct(g.rate)}${g.flagged_without_rate != null ? ` vs ${pct(g.flagged_without_rate)}` : ""} (n=${g.flagged_with})${g.p_greater != null && g.p_greater < 0.05 ? " ✓" : ""}`;
              const act: Record<string, string> = { income_drop: "Call first: income check, EI, payment holiday", swing: "Auto-save good months into the cushion",
                new_loan: "Loan review: payment date or longer term", dip_only: "Cushion + personal alert" };
              return <tr key={k}><td><b>{a.label}</b><br /><span className="muted">{act[k]}</span></td><td className="num">{cell(a)}</td><td className="num">{cell(b)}</td></tr>;
            })}
            <tr><td><b>{e.diagnoses.by_year[1].rejected_bill_timing.label}</b><br /><span className="muted">Rejected: it is protective, so no "move the bill date" action</span></td>
              {e.diagnoses.by_year.map((y: { year: number; rejected_bill_timing: { rate: number; others_rate: number; accounts: number } }) =>
                <td key={y.year} className="num">{pct(y.rejected_bill_timing.rate, 1)} vs {pct(y.rejected_bill_timing.others_rate, 1)} (n={y.rejected_bill_timing.accounts})</td>)}</tr>
            </tbody></table>
          <p className="sub" style={{ marginTop: 8 }}>✓ = significant on its own (one-sided Fisher, p &lt; 0.05). All of these tests are in the multiple-testing count above.</p>
        </details>
      )}

      {e.survival && (() => {
        const cs = e.survival.cohorts as { scored: string; followed: string; customers: number; first_overdrafts: number; curves: Record<string, { customers: number; overdrawn_by_month: number[] }>; hazard_ratio_flag: number; hazard_ratio_flag_ci95: number[]; hazard_ratio_first_6_months: number; logrank_p: number }[];
        const last = cs[cs.length - 1], r = last.curves["riskiest 10%"].overdrawn_by_month;
        return (
          <section className="grid g-7-5" style={{ alignItems: "start" }}>
            <div className="card">
              <h2>Once flagged, the riskiest 10% overdraw early: {pct(r[6], 1)} within 6 months, {pct(r[24], 1)} within 2 years</h2>
              <p className="sub" style={{ marginBottom: 8 }}>Survival analysis (Kaplan–Meier): share who've had a first overdraft, by months since scoring. Scored {last.scored}, followed {last.followed}; customers who leave are handled correctly (censored).</p>
              <SurvivalChart curves={last.curves} />
              <Legend items={[{ label: "Riskiest 10%", kind: "ours" }, { label: "Next 20%", kind: "ink" }, { label: "Everyone else", kind: "grey" }]} />
            </div>
            <div className="card">
              <h2>When to act: in the first 6 months</h2>
              <p className="sub">Discrete-time hazard model (monthly data, so most event times tie), adjusted for balance size and account age.</p>
              <table className="tbl" style={{ marginTop: 8 }}><thead><tr><th>Cohort</th><th className="num">Riskiest 10% vs rest</th><th className="num">Months 1–6 vs later</th></tr></thead>
                <tbody>{cs.map((c) => <tr key={c.scored}><td>{c.followed}</td>
                  <td className="num">{c.hazard_ratio_flag.toFixed(1)}× ({c.hazard_ratio_flag_ci95[0].toFixed(1)}–{c.hazard_ratio_flag_ci95[1].toFixed(1)})</td>
                  <td className="num">{c.hazard_ratio_first_6_months.toFixed(1)}×</td></tr>)}</tbody></table>
              <p className="callout" style={{ marginTop: 10 }}>The risk is front-loaded, so the call list says "call this week", not "this quarter". Log-rank test: groups differ, p {last.logrank_p < 1e-6 ? "< 0.000001" : last.logrank_p.toFixed(4)}.</p>
            </div>
          </section>
        );
      })()}

      {e.challenger && (() => {
        const ch = e.challenger, champ = "trough (champion)", chal = "gradient boosting (challenger)";
        return (
          <section className="card">
            <h2>Champion vs challenger: a 12-feature gradient-boosting model doesn't beat the one-number trough</h2>
            <p className="sub" style={{ marginBottom: 8 }}>Both fit on 2023 → 2024 and judged on 2025 ({ch.test_accounts} customers, {ch.test_events} first overdrafts), the way a bank tests a replacement model.</p>
            <table className="tbl"><thead><tr><th>Model</th><th className="num">AUC 2025</th><th className="num">Caught when flagging 10%</th><th>Explain to a customer?</th></tr></thead>
              <tbody>
                <tr><td><b>Liquidity trough</b> (champion)</td><td className="num">{ch.auc[champ].toFixed(3)}</td><td className="num">{ch.caught_top10[champ]} of {ch.test_events}</td><td>One sentence; one SQL query</td></tr>
                <tr><td>Gradient boosting, 12 features (challenger)</td><td className="num">{ch.auc[chal].toFixed(3)}</td><td className="num">{ch.caught_top10[chal]} of {ch.test_events}</td><td>Needs feature attributions</td></tr>
              </tbody></table>
            <p style={{ margin: "10px 0 4px" }}>Not a significant difference: AUC p = {ch.auc_diff_p_boot.toFixed(2)}; on the overdrafts only one model caught ({ch.caught_only_challenger} vs {ch.caught_only_champion}), McNemar p = {ch.mcnemar_p.toFixed(2)}. The challenger's most important input is the trough itself.</p>
            <p className="callout">{ch.decision}</p>
          </section>
        );
      })()}

      {e.fairness && (
        <details className="card fold">
          <summary><h2>Fairness: does it treat women and men alike?</h2><span className="sub">Flag-rate ratio women ÷ men {(e.fairness.by_year as { flag_rate_ratio_women_to_men: number }[]).map((y) => y.flag_rate_ratio_women_to_men.toFixed(2)).join(" and ")}, inside the 0.8–1.25 band; no consistent gap in overdrafts caught. Show the table</span></summary>
          <p className="sub" style={{ marginBottom: 8 }}>{e.fairness.verdict} {e.fairness.note}</p>
          <table className="tbl"><thead><tr><th>Predicting</th><th className="num">Flagged: women / men</th><th className="num">Ratio</th><th className="num">Overdrafts caught: women / men</th><th className="num">Gap p-value</th></tr></thead>
            <tbody>{(e.fairness.by_year as { predicted_year: number; flag_rate_ratio_women_to_men: number; catch_gap_p: number; groups: Record<string, { flag_rate: number; caught: number; first_overdrafts: number; catch_rate: number }> }[]).map((y) => {
              const w = y.groups.women, m = y.groups.men;
              return <tr key={y.predicted_year}><td>{y.predicted_year}</td><td className="num">{pct(w.flag_rate, 1)} / {pct(m.flag_rate, 1)}</td>
                <td className="num">{y.flag_rate_ratio_women_to_men.toFixed(2)}</td>
                <td className="num">{w.caught} of {w.first_overdrafts} ({pct(w.catch_rate)}) / {m.caught} of {m.first_overdrafts} ({pct(m.catch_rate)})</td>
                <td className="num">{y.catch_gap_p.toFixed(2)}</td></tr>;
            })}</tbody></table>
          <p className="sub" style={{ marginTop: 8 }}>Ratio band 0.8–1.25 is the "four-fifths rule" convention. Gender and age are never inputs to the score. Both are now monitored in Model health.</p>
        </details>
      )}

      {e.lessons && (
        <details className="card fold">
          <summary><h2>What we tried that didn't hold up, and what we did about it</h2>
            <span className="sub">{mt.did_not_survive.length} of {mt.tests} tests didn't survive correction. {Object.entries((e.lessons as { group: string }[]).reduce((a: Record<string, number>, l) => ({ ...a, [l.group]: (a[l.group] ?? 0) + 1 }), {})).map(([g, n]) => `${n} ${g.toLowerCase()}`).join(" · ")}. Show them</span></summary>
          <table className="tbl"><thead><tr><th>Idea</th><th>Result</th><th>What we did</th></tr></thead>
            <tbody>{(e.lessons as { group: string; idea: string; result: string; decision: string }[]).map((l) => (
              <tr key={l.idea}><td><span className={`chip ${l.group === "Rejected" ? "warn" : l.group === "Not claimed" ? "amber" : ""}`}>{l.group}</span> {l.idea}</td>
                <td>{l.result}</td><td>{l.decision}</td></tr>))}</tbody></table>
        </details>
      )}

      <section className="card">
        <h2>Limits, what we did about each, and what fixes it in production</h2>
        <table className="tbl"><thead><tr><th>Limit</th><th>What we did</th><th>In production</th></tr></thead>
          <tbody>{([
            ["Re-dated 1990s Czech bank data, not Tangerine customers", "Tested out of time on three separate years; nothing tuned on the year it was judged on", "Re-fit thresholds on Tangerine data during a 3-month shadow run before any customer contact"],
            ["Money in is mostly cash, so we can't see pay", "A slider shows the assumption; the verdict says when it drives the answer", "Use payroll tags on deposits to measure real income"],
            ["Loan status D ('in debt') is partly defined by overdraft", e.loan_policy ? `Also report the clean outcome (finished unpaid): ${pct(e.loan_policy.finished_unpaid.default_rate_held, 1)} vs ${pct(e.loan_policy.finished_unpaid.default_rate_not_held, 1)}` : "Report the clean outcome alongside", "Track real charge-offs and recoveries"],
            ["An early-warning signal, not a cause", "Used to decide who to call, never to decline credit automatically", "A controlled pilot measures whether outreach actually prevents overdrafts"],
            ["Small samples (55 first overdrafts in 2025; 14–29 per gender)", "Report confidence intervals, both years, and multiple-testing correction", "Larger book, monthly monitoring with breach thresholds (Model health)"],
            ["Possible unequal treatment of groups", "Checked by gender and age in two years: no consistent gap", "Monitor flag and catch rates by group every period"],
          ] as const).map(([a, b, c]) => <tr key={a}><td><b>{a}</b></td><td>{b}</td><td className="muted">{c}</td></tr>)}</tbody></table>
      </section>
    </main>
  );
}
