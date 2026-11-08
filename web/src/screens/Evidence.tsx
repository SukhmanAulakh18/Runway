import { useQuery } from "@tanstack/react-query";
import { api, money, pct } from "../api";
import { Legend, PairBars } from "../charts";
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
            <PairBars data={steerBars} a={{ key: "a", name: "Real customers" }} b={{ key: "b", name: "Same months, random order" }} fmt={(v) => `+${Math.round(v * 100)} pts`} />
            <Legend items={[{ label: "Real customers", kind: "ours" }, { label: "Same months, random order", kind: "soft" }]} />
          </div>
          <div className="card">
            <h2>Why it matters</h2>
            <p style={{ margin: "8px 0" }}>A simulation that replays months in random order can't steer back, so it predicted {pct(cal.raw_mean)} would go overdrawn when {pct(cal.observed_rate, 1)} did. That's why we calibrate it, and why the dip, not the average, is what to watch.</p>
            <p className="callout">Follow-up we don't claim: weak steering predicting who in the riskiest 10% goes overdrawn held in 2025 but not in 2024.</p>
          </div>
        </section>
      )}

      {e.segment && (
        <section className="card">
          <h2>Who the riskiest 10% are: every trait we checked, including the ones that don't matter</h2>
          <p className="sub" style={{ marginBottom: 8 }}>{e.segment.riskiest_10_n} flagged vs {e.segment.everyone_else_n} others (Dec 2024 data). Medians for amounts, shares for yes/no. Multiple-testing corrected.</p>
          <table className="tbl"><thead><tr><th>Trait</th><th className="num">Riskiest 10%</th><th className="num">Everyone else</th><th>Different?</th></tr></thead>
            <tbody>{(e.segment.rows as { trait: string; kind: string; riskiest_10: number; everyone_else: number; differs: boolean }[]).map((r) => {
              const f = (v: number) => r.kind === "bin" || r.trait.includes("share") ? pct(v, 1) : r.trait.includes("age") ? v.toFixed(1) : money(v);
              return <tr key={r.trait}><td>{r.trait}</td><td className="num">{f(r.riskiest_10)}</td><td className="num">{f(r.everyone_else)}</td>
                <td>{r.differs ? <span className="chip ours">Yes</span> : <span className="chip">No difference</span>}</td></tr>;
            })}</tbody></table>
        </section>
      )}

      <section className="grid g2" style={{ alignItems: "start" }}>
        <div className="card">
          <h2>What didn't survive, said out loud</h2>
          <div className="list">{mt.did_not_survive.map((d: string) => <div key={d} className="list-row"><span>{d}</span><span className="chip">Not significant</span></div>)}</div>
          <p className="callout" style={{ marginTop: 10 }}>The trough and the plain lowest balance are statistically tied. Our claim is the low point beats both runway formulas, not that the ratio beats the low point.</p>
        </div>
        <div className="card">
          <h2>Limits</h2>
          <div className="list">
            {["Re-dated 1990s Czech bank data (PKDD'99), not real Tangerine customers.",
              "Most money in is cash, so a job loss assumes all non-pension money in stops: the biggest assumption in the model.",
              "Loan status D means 'in debt', so part of the overdraft → default link is by definition. The before-the-loan results don't have that problem.",
              "An early-warning signal, not a cause."].map((l) => <div key={l} className="list-row"><span>{l}</span></div>)}
          </div>
        </div>
      </section>
    </main>
  );
}
