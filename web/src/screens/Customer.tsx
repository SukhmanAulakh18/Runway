import { useQuery } from "@tanstack/react-query";
import { api, money, monthName, pct } from "../api";
import type { Nav } from "../App";
import { BalanceChart, Legend } from "../charts";
import { Failed, Kpi, Loading } from "./ui";

export default function CustomerScreen({ nav }: { nav: Nav }) {
  const q = useQuery({ queryKey: ["customer", nav.acct, nav.asof], queryFn: () => api.customer(nav.acct, nav.asof) });
  if (q.isPending) return <main className="page"><Loading h={90} /><Loading h={140} /><Loading h={320} /></main>;
  if (q.isError) return <main className="page"><Failed error={q.error} /></main>;
  const c = q.data, t = c.trough, r = c.realistic;
  const next = c.what_happened_next ?? [];
  const overdrawnNext = next.filter((m) => m.days_below_zero > 0);

  return (
    <main className="page fade">
      <div>
        <p className="eyebrow">02 · Know the customer{c.asof ? ` · as of ${monthName(c.asof)}` : ""}</p>
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginTop: 6 }}>
          <h1 className="title" style={{ margin: 0 }}>Customer {c.account_id}</h1>
          {c.owner_age != null && <span className="badge muted">Owner {c.owner_age}</span>}
          {t?.bottom_10 && <span className="badge ours">Riskiest 10%</span>}
          {!t?.scorable && <span className="badge muted">Too new to score</span>}
        </div>
      </div>

      <p className="summary">
        Over the last {r.window_months} months they brought in about <b>{money(r.income)}</b> a month and sent out <b>{money(r.spending)}</b>,
        {" "}with <b>{money(c.profile.buffer)}</b> on average in the account.
        {t?.scorable && <> But their balance dipped to <b>{money(t.min_balance)}</b>, {pct(t.ltr)} of the average.</>}
        {" "}Standard runway: <span className="s">{c.standard_runway.label}</span>. Realistic: <span className="o">{c.realistic_runway.label}</span>.
      </p>

      <section className="grid g4">
        <div className="card ink">
          {c.risk.validated_population
            ? <Kpi label="Chance of a first overdraft, next 12 months" value={pct(c.risk.p_12m, 1)} note="Calibrated on 2024, checked on 2025. If nothing changes." />
            : <Kpi label="First-overdraft forecast" value="n/a" size="md" note="Only for customers with 12+ months who were never overdrawn" />}
        </div>
        <div className="card ours">
          <Kpi label="Liquidity trough (lowest ÷ average, 6 mo)" value={t ? pct(t.ltr) : "–"}
            note={t?.pct_rank != null ? `Riskier than ${pct(1 - t.pct_rank)} of customers` : "Needs 12+ months of history"} />
        </div>
        <div className="card"><Kpi swatch="std" label="Standard runway (no shock)" value={c.standard_runway.label} size="md" note="Judges' formula, medians" /></div>
        <div className="card"><Kpi swatch="ours" label="Realistic runway (no shock)" value={c.realistic_runway.label} size="md" note="Last 12 months, dip-aware" /></div>
      </section>

      <section className="grid g-7-5" style={{ alignItems: "start" }}>
        <div className="card">
          <div className="card-head">
            <div>
              <h2>{t?.scorable ? `Dipped to ${money(t.min_balance)} while averaging ${money(t.avg_balance)} (last 6 months)` : "Average and lowest balance each month"}</h2>
              <p className="sub">The shaded gap is the in-month dip: money that looks saved but is spent before the month ends.</p>
            </div>
          </div>
          <BalanceChart history={c.history} />
          <Legend items={[{ label: "Average balance", kind: "ink" }, { label: "Lowest balance", kind: "ours" }, { label: "In-month dip", kind: "soft" }, { label: "Below $0", kind: "bad" }]} />
        </div>

        <div className="grid" style={{ alignContent: "start" }}>
          {c.asof && (
            <div className={`card ${overdrawnNext.length ? "" : ""}`}>
              <h2>{overdrawnNext.length
                ? `What happened next: overdrawn in ${overdrawnNext.length} of the next ${next.length} months`
                : `What happened next: stayed above $0 for ${next.length} months`}</h2>
              <p className="sub">Hidden from the model. Revealed because the Time Machine is on.</p>
              <div className="chips" style={{ marginTop: 10 }}>
                {next.map((m) => (
                  <span key={m.month} className={`chip ${m.days_below_zero > 0 ? "warn" : ""}`} title={`Lowest ${money(m.min_balance)}`}>
                    {monthName(m.month)}{m.days_below_zero > 0 ? ` · ${m.days_below_zero} days below $0` : ""}
                  </span>
                ))}
              </div>
            </div>
          )}
          <div className="card ours">
            <h2>The fix: a cushion sized to their own dip</h2>
            <p style={{ margin: "8px 0 12px" }}>Overdraft protection of <b>{money(c.cushion.buffer)}</b>, and an alert when the balance falls below <b>{money(c.cushion.alert_level)}</b>.
              {c.cushion.dip_day_reliable && c.cushion.dip_day && <> Their balance usually bottoms out around day {c.cushion.dip_day}.</>}</p>
            <button className="btn ours" onClick={() => nav.go("plan")}>Open the plan →</button>
          </div>
          {c.flags.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: 8 }}>Things to know before you explain the numbers</h3>
              <div className="chips">{c.flags.map((f) => <span key={f} className={`chip ${/overdrawn|riskiest|zero/i.test(f) ? "warn" : ""}`}>{f}</span>)}</div>
            </div>
          )}
          {c.loan && (
            <div className="card">
              <h3>Loan</h3>
              <p style={{ margin: "6px 0 0" }}>{money(c.loan.amount)} from {c.loan.loan_start}, {money(c.loan.monthly_payment)}/month. <b>{c.loan.status_meaning}</b>.
                {c.loan.overdrawn_before_loan && <span className="chip warn" style={{ marginLeft: 6 }}>Granted while already overdrawn</span>}</p>
            </div>
          )}
        </div>
      </section>

      <section className="card">
        <div className="card-head"><div><h2>The judges' numbers</h2><p className="sub">Exactly the Tangerine README definitions, from monthly_summary.csv.</p></div>
          <button className="btn" onClick={() => nav.go("stress")}>Apply a shock →</button></div>
        <table className="tbl">
          <tbody>
            {([["I", "Typical monthly money in (median)", c.profile.income], ["S", "Typical monthly money out (median)", c.profile.spending],
              ["B", "Buffer (mean average daily balance, last 6 months)", c.profile.buffer], ["H", "Household bills (median)", c.profile.household_bills],
              ["F", "Fixed costs (median bills + insurance + loans)", c.profile.fixed_costs], ["P", "Loan payment (running at end of 2025)", c.profile.loan_payment]] as const)
              .map(([k, label, v]) => <tr key={k}><td style={{ width: 40 }}><b>{k}</b></td><td>{label}</td><td className="num">{money(v)}</td></tr>)}
          </tbody>
        </table>
      </section>
    </main>
  );
}
