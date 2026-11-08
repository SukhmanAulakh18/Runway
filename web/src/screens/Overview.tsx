import { useQuery } from "@tanstack/react-query";
import { api, kmoney, money, monthName, pct, NO_SHOCK } from "../api";
import type { Nav } from "../App";
import { Legend, PortfolioChart } from "../charts";
import { Failed, Kpi, Loading } from "./ui";

export default function Overview({ nav }: { nav: Nav }) {
  const ev = useQuery({ queryKey: ["evidence"], queryFn: api.evidence, staleTime: Infinity });
  const wl = useQuery({ queryKey: ["watchlist", nav.asof], queryFn: () => api.watchlist(nav.asof) });
  const job = { ...NO_SHOCK, job_loss: true };
  const pc = useQuery({ queryKey: ["portfolio", job], queryFn: () => api.portfolio(job), staleTime: Infinity });
  const im = ev.data?.impact?.["2024-12"];
  const y25 = ev.data?.trough?.by_year?.find((r: { predicted_year: number }) => r.predicted_year === 2025);
  const at6 = pc.data?.find((p) => p.month === 6);

  return (
    <main className="page fade">
      <div>
        <p className="eyebrow">01 · The finding</p>
        <h1 className="title">Banks watch the average balance. <em>Overdrafts happen at the low point.</em></h1>
        <p className="lede">
          Some customers look healthy on average but dip close to $0 every month. Runway measures that dip (the liquidity trough),
          flags who is about to have a first overdraft, stress-tests them, and sizes the cheapest fix.
        </p>
      </div>

      {ev.isPending ? <Loading h={130} /> : ev.isError ? <Failed error={ev.error} /> : im && y25 && (
        <section className="grid g4" aria-label="Headline results">
          <div className="card ink"><Kpi label="Flag 10% of customers, catch" value={pct(im.caught_share)}
            note={`${im.caught} of ${im.first_overdrafts} first overdrafts in 2025, tested on data the model never saw`} /></div>
          <div className="card"><Kpi label="Risk vs everyone else" value={`${y25.risk_ratio.toFixed(1)}×`}
            note={`${pct(y25.low10_rate, 1)} vs ${pct(y25.rest_rate, 2)}. Holds in 2023, 2024 and 2025`} /></div>
          <div className="card ours"><Kpi label="Dip-sized buffer covers" value={pct(im.buffer.covered_share)}
            note={`${kmoney(im.buffer.drawn_total)} drawn of ${kmoney(im.buffer.limits_total)} in limits`} /></div>
          <div className="card"><Kpi label="Personal alert warns" value={`${im.alert.median_lead_months} mo early`}
            note={`${im.alert.fired_before} of ${im.caught}. A $100 alert: ${im.alert.generic_100_fired_before} of ${im.caught}`} /></div>
        </section>
      )}

      <section className="grid g-7-5">
        <div className="card">
          <div className="card-head">
            <div>
              <h2>Watchlist{nav.asof ? `, as the bank saw it in ${monthName(nav.asof)}` : ""}</h2>
              <p className="sub">Never overdrawn yet, ranked by how close their balance gets to $0. Click a row to open the customer.</p>
            </div>
            {wl.data?.reveal && <span className="badge bad">{wl.data.reveal.top_hit} of {wl.data.rows.length} overdrawn next year</span>}
          </div>
          {wl.data?.reveal && (
            <p className="callout bad" style={{ marginTop: 0 }}>
              Time Machine: {wl.data.reveal.top_hit} of these {wl.data.rows.length} went overdrawn in the next 12 months,
              vs {pct(wl.data.reveal.base_rate, 1)} of everyone.
            </p>
          )}
          {!nav.asof && <p className="sub" style={{ marginBottom: 10 }}>Tip: set the Time Machine to Dec 2024 to see who actually went overdrawn next.</p>}
          {wl.isPending ? <Loading h={320} /> : wl.isError ? <Failed error={wl.error} /> : (
            <div style={{ maxHeight: 520, overflow: "auto" }}>
              <table className="tbl">
                <thead><tr>
                  <th>Account</th><th>Lowest vs average (6 mo)</th><th className="num" title="Percentile rank: 1.6% = in the riskiest 1.6% of customers">Top %</th>
                  <th className="num">Lowest</th><th>Why</th>{nav.asof && <th>Next 12 months</th>}
                </tr></thead>
                <tbody>
                  {wl.data.rows.map((r) => (
                    <tr key={r.account_id} className={`row ${r.account_id === nav.acct ? "cur" : ""}`} onClick={() => nav.go("customer", r.account_id)}>
                      <td><b>{r.account_id}</b></td>
                      <td><div className="bar-cell"><div className="bar-track"><div className="bar-fill" style={{ width: `${Math.max(r.ltr, 0) * 100}%` }} /></div>
                        <span style={{ width: 40 }}>{pct(r.ltr)}</span></div></td>
                      <td className="num">{r.ltr_pct_rank != null ? pct(r.ltr_pct_rank, 1) : "–"}</td>
                      <td className="num">{money(r.min_balance)}</td>
                      <td><div className="chips">{r.reasons.split("; ").filter(Boolean).slice(0, 2).map((x) => <span key={x} className="chip">{x}</span>)}</div></td>
                      {nav.asof && <td>{r.overdraft_next_12m ? <span className="badge bad">Overdrawn</span> : <span className="muted">Stayed above $0</span>}</td>}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="grid" style={{ alignContent: "start" }}>
          <div className="card">
            <h2>{at6 ? `If everyone lost their job: the standard formula says ${pct(at6.standard)} still have money at month 6. Realistically, ${pct(at6.realistic)}.`
              : "Bank view: a layoff hits everyone at once"}</h2>
            <p className="sub" style={{ marginBottom: 10 }}>Share of all 4,500 customers above zero. Realistic = EI capped at $729/week and stopping after 6 months, pensions kept.</p>
            {pc.isPending ? <Loading h={220} /> : pc.isError ? <Failed error={pc.error} /> : <PortfolioChart data={pc.data} />}
            <Legend items={[{ label: "Realistic", kind: "ours" }, { label: "Standard formula", kind: "std" }]} />
          </div>
          <div className="card">
            <h2>Why it matters to a lender</h2>
            {ev.data && (
              <p style={{ margin: "8px 0 0" }}>
                <b>{ev.data.loans.overdrawn_and_defaulted} of {ev.data.loans.overdrawn_borrowers}</b> borrowers who were ever overdrawn defaulted;
                none of the others did. {ev.data.loans.pre_loan_overdrawn} loans were granted to customers already overdrawn, and all
                {" "}{ev.data.loans.pre_loan_overdrawn_defaulted} defaulted.
              </p>
            )}
            <button className="btn" style={{ marginTop: 12 }} onClick={() => nav.go("evidence")}>See the evidence →</button>
          </div>
        </div>
      </section>
    </main>
  );
}
