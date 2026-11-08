import { useQuery } from "@tanstack/react-query";
import { api, kmoney, money, monthName, pct, NO_SHOCK } from "../api";
import type { Nav } from "../App";
import { Legend, PortfolioChart } from "../charts";
import { CountUp, Failed, Kpi, Loading } from "./ui";

export default function Overview({ nav }: { nav: Nav }) {
  const ev = useQuery({ queryKey: ["evidence"], queryFn: api.evidence, staleTime: Infinity });
  const wl = useQuery({ queryKey: ["watchlist", nav.asof], queryFn: () => api.watchlist(nav.asof) });
  const job = { ...NO_SHOCK, job_loss: true };
  const pc = useQuery({ queryKey: ["portfolio", job], queryFn: () => api.portfolio(job), staleTime: Infinity });
  const im = ev.data?.impact?.["2024-12"];
  const y25 = ev.data?.trough?.by_year?.find((r: { predicted_year: number }) => r.predicted_year === 2025);
  const at6 = pc.data?.find((p) => p.month === 6);
  const lp = ev.data?.loan_policy;
  type Trait = { trait: string; riskiest_10: number; everyone_else: number };
  const seg = ev.data?.segment ? Object.fromEntries((ev.data.segment.rows as Trait[]).map((r) => [r.trait, r])) as Record<string, Trait> : null;

  return (
    <main className="page fade">
      <div>
        <p className="eyebrow">01 · The finding</p>
        <h1 className="title">Banks watch the average balance. <em>Overdrafts happen at the low point.</em></h1>
        <p className="lede">
          Built for a bank's customer-care and risk teams. Some customers look healthy on average but dip close to $0 every
          month. Runway finds them before their first overdraft and tells the advisor exactly what to offer.
        </p>
      </div>

      <section className="howto" aria-label="How it works">
        {[["Spot", "Flag customers whose balance keeps dipping near $0, even when the average looks fine."],
          ["Explain", "Show why in plain words: the dip, the risk, and what a job loss or repair would do."],
          ["Act", "Match the action to the cause: a call when money in falls, a loan review, auto-saving good months, and a cushion with an alert sized to their own dip. Message ready in English or French."]].map(([h, t], i) => (
          <div key={h} className="card"><span className="n">{i + 1}</span><div><h2>{h}</h2><p className="sub" style={{ marginTop: 4 }}>{t}</p></div></div>
        ))}
      </section>

      {ev.isPending ? <Loading h={130} /> : ev.isError ? <Failed error={ev.error} /> : im && y25 && (
        <section className="grid g4" aria-label="Headline results">
          <div className="card hero"><Kpi label="Flag 10% of customers, catch" value={<CountUp text={pct(im.caught_share)} />}
            note={`${im.caught} of ${im.first_overdrafts} first overdrafts in 2025, tested on data the model never saw`} /></div>
          <div className="card"><Kpi label="Risk vs everyone else" value={<CountUp text={`${y25.risk_ratio.toFixed(1)}×`} />}
            note={`${pct(y25.low10_rate, 1)} vs ${pct(y25.rest_rate, 2)}. Holds in 2023, 2024 and 2025`} /></div>
          <div className="card ours"><Kpi label="Dip-sized buffer covers" value={<CountUp text={pct(im.buffer.covered_share)} />}
            note={`${kmoney(im.buffer.drawn_total)} drawn of ${kmoney(im.buffer.limits_total)} in limits`} /></div>
          <div className="card"><Kpi label="Personal alert warns" value={<CountUp text={`${im.alert.median_lead_months} mo early`} />}
            note={`${im.alert.fired_before} of ${im.caught}; a $100 alert: ${im.alert.generic_100_fired_before}.${im.alert.fired_for_quiet_share != null ? ` Pinged ${pct(im.alert.fired_for_quiet_share)} of flagged customers who never needed it` : ""}`} /></div>
        </section>
      )}

      <BookCard nav={nav} />

      <section className="grid g-7-5">
        <div className="card">
          <div className="card-head">
            <div>
              <h2>Advisor call list{nav.asof ? `, as the bank saw it in ${monthName(nav.asof)}` : ""}</h2>
              <p className="sub">Never overdrawn yet, ranked by how close their balance gets to $0. Each row has its own cause and next step. Click to open.</p>
              {wl.data?.calls && <div className="chips" style={{ marginTop: 8 }}>{Object.entries(wl.data.calls).map(([a, n]) => <span key={a} className="chip ours"><b>{n}</b>&nbsp;· {a}</span>)}</div>}
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
            <div style={{ maxHeight: 520, overflow: "auto" }} tabIndex={0} role="region" aria-label="Watchlist table, scrollable">
              <table className="tbl">
                <thead><tr>
                  <th>Account</th><th>Lowest vs average (6 mo)</th><th className="num" title="Percentile rank: 1.6% = in the riskiest 1.6% of customers">Top %</th>
                  <th className="num">Lowest</th><th>Cause → next step</th>{nav.asof && <th>Next 12 months</th>}
                </tr></thead>
                <tbody>
                  {wl.data.rows.map((r) => (
                    <tr key={r.account_id} className={`row ${r.account_id === nav.acct ? "cur" : ""}`} onClick={() => nav.go("customer", r.account_id)}>
                      <td><b>{r.account_id}</b></td>
                      <td><div className="bar-cell"><div className="bar-track"><div className="bar-fill" style={{ width: `${Math.max(r.ltr, 0) * 100}%` }} /></div>
                        <span style={{ width: 40 }}>{pct(r.ltr)}</span></div></td>
                      <td className="num">{r.ltr_pct_rank != null ? pct(r.ltr_pct_rank, 1) : "–"}</td>
                      <td className="num">{money(r.min_balance)}</td>
                      <td>{r.cause ? <span title={r.reasons}>{r.cause} → <b>{r.action}</b></span> : <span className="muted">{r.reasons.split("; ")[0]}</span>}</td>
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
            <p className="sub" style={{ marginBottom: 10 }}>Share of all 4,500 customers above zero, on today's data (Dec 2025) whatever the Time Machine is set to. Realistic = EI capped at $729/week and stopping after 6 months, pensions kept.</p>
            {pc.isPending ? <Loading h={220} /> : pc.isError ? <Failed error={pc.error} /> : <PortfolioChart data={pc.data} />}
            <Legend items={[{ label: "Realistic", kind: "ours" }, { label: "Standard formula", kind: "std" }]} />
          </div>
          <div className="card">
            <h2>{lp ? `Check the trough before lending: held loans defaulted ${pct(lp.all_defaults.default_rate_held)} vs ${pct(lp.all_defaults.default_rate_not_held, 1)}` : "Why it matters to a lender"}</h2>
            {lp && (
              <p style={{ margin: "8px 0 0" }}>
                A review rule at loan approval (already overdrawn, or riskiest 10% by trough; data before the loan only, nothing fit on
                loan outcomes) holds <b>{pct(lp.all_defaults.held_share)}</b> of loans and catches <b>{lp.all_defaults.caught} of {lp.all_defaults.events}</b> defaults.
                Counting only loans that finished unpaid: {lp.finished_unpaid.caught} of {lp.finished_unpaid.events}, {pct(lp.finished_unpaid.default_rate_held)} vs {pct(lp.finished_unpaid.default_rate_not_held, 1)}.
                It also holds {lp.all_defaults.good_loans_held} good loans: review means talk first, not reject.
              </p>
            )}
            {ev.data && (
              <p style={{ margin: "8px 0 0" }}>
                <b>{ev.data.loans.overdrawn_and_defaulted} of {ev.data.loans.overdrawn_borrowers}</b> borrowers who were ever overdrawn defaulted;
                none of the others did. {ev.data.loans.pre_loan_overdrawn} loans were granted to customers already overdrawn, and all
                {" "}{ev.data.loans.pre_loan_overdrawn_defaulted} defaulted.
              </p>
            )}
            <button className="btn" style={{ marginTop: 12 }} onClick={() => nav.go("evidence")}>See the evidence →</button>
          </div>
          {seg && (
            <div className="card">
              <h2>Who the riskiest 10% are: not poor, but running hot</h2>
              <div className="list" style={{ marginTop: 6 }}>
                <div className="list-row"><span>Money in per month (median)</span><b>{money(seg["money in per month"].riskiest_10)} vs {money(seg["money in per month"].everyone_else)}</b></div>
                <div className="list-row"><span>Carry a loan</span><b>{pct(seg["has a loan"].riskiest_10)} vs {pct(seg["has a loan"].everyone_else)}</b></div>
                <div className="list-row"><span>Pensioners</span><b>{pct(seg["pensioner"].riskiest_10, 1)} vs {pct(seg["pensioner"].everyone_else)}</b></div>
              </div>
              <p className="sub" style={{ marginTop: 8 }}>Where they live, joint accounts and district salaries make no difference. Descriptive, tested; not causal.</p>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

const TIER_CLASS: Record<string, string> = { overdrawn: "t-bad", act: "t-act", new_hot: "t-newhot", watch: "t-watch", stable: "t-stable", new: "t-new" };

/** The whole book: every customer in one tier, with its action and the tier's tested overdraft rate. */
function BookCard({ nav }: { nav: Nav }) {
  const q = useQuery({ queryKey: ["book", nav.asof], queryFn: () => api.book(nav.asof) });
  if (q.isPending) return <Loading h={160} />;
  if (q.isError) return <Failed error={q.error} />;
  const b = q.data, s = b.summary;
  return (
    <section className="card" aria-label="The whole book">
      <div className="card-head"><div>
        <h2>The whole book: {b.customers.toLocaleString("en-CA")} customers, one action each</h2>
        <p className="sub">
          {pct(s.focus_customer_share)} of customers at this date need an advisor (already overdrawn, riskiest 10%, or a new account that swings hard); {pct(s.stable_customer_share)} are stable and need nothing.
          {s.tested_focus_overdraft_share != null && s.tested_focus_customer_share != null && s.tested_stable_rate != null &&
            <> Tested on {b.tested_on}: those tiers were <b>{pct(s.tested_focus_customer_share)}</b> of customers and produced <b>{pct(s.tested_focus_overdraft_share)}</b> of the next year's overdrafts; the stable tier overdrew {pct(s.tested_stable_rate, 1)}.</>}
          {b.tested_on && <> Rates come from a year already over at this date.</>}
        </p></div></div>
      <div className="bookbar" role="img" aria-label={b.tiers.map((t) => `${t.label}: ${t.customers}`).join("; ")}>
        {b.tiers.filter((t) => t.customers > 0).map((t) => (
          <span key={t.tier} className={TIER_CLASS[t.tier]} style={{ flexGrow: t.customers }} title={`${t.label}: ${t.customers.toLocaleString("en-CA")}`} />
        ))}
      </div>
      <table className="tbl" style={{ marginTop: 10 }}>
        <thead><tr><th>Tier</th><th className="num">Customers</th><th className="num">Overdrew next year</th><th className="num">Share of all overdrafts</th><th>Action</th></tr></thead>
        <tbody>{b.tiers.map((t) => (
          <tr key={t.tier}>
            <td><span className={`dot ${TIER_CLASS[t.tier]}`} aria-hidden="true" /> <b>{t.label}</b></td>
            <td className="num">{t.customers.toLocaleString("en-CA")}</td>
            <td className="num">{pct(t.tested_rate, 1)}</td>
            <td className="num">{pct(t.tested_share_of_overdrafts)}</td>
            <td>{t.action}{t.tier === "act" && Object.keys(b.act_causes).length > 0 &&
              <span className="muted"> ({Object.entries(b.act_causes).map(([k, v]) => `${v} ${k.toLowerCase()}`).join(", ")})</span>}</td>
          </tr>))}
        </tbody></table>
      <p className="sub" style={{ marginTop: 8 }}>New accounts can't be scored by the trough (it needs 12 months), so they get their own test: swings in money in, chosen on 2023 and 2024 and confirmed on 2025 (the top 10% of new accounts caught 13 of 32 first overdrafts, 18.6% vs 3.0%). Accounts under 3 months stay unscored.</p>
    </section>
  );
}
