import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api, kmoney, money, monthName, pct, type Asof, type Diagnosis } from "../api";
import type { Nav } from "../App";
import { BalanceChart, Legend } from "../charts";
import { CountUp, Failed, GLOSSARY, Kpi, Loading } from "./ui";

function Source({ s }: { s: string }) {
  return <span className={`src ${s.startsWith("AI") ? "" : "tpl"}`}>{s.startsWith("AI") ? "AI · every number checked" : "Template (AI off or unsure)"}</span>;
}

/** AI helps the advisor talk: it writes words from engine numbers, never calculates. */
function Assistant({ acct, asof }: { acct: number; asof: Asof }) {
  const [lang, setLang] = useState<"en" | "fr">("en");
  const [copied, setCopied] = useState(false);
  const brief = useMutation({ mutationFn: () => api.brief(acct, asof) });
  const msg = useMutation({ mutationFn: (l: "en" | "fr") => api.message(acct, asof, l) });
  const copy = async (t: string) => { try { await navigator.clipboard.writeText(t); setCopied(true); setTimeout(() => setCopied(false), 1500); } catch { /* clipboard blocked */ } };
  return (
    <section className="card">
      <div className="card-head">
        <div><h2>Advisor assistant</h2>
          <p className="sub">Gemini turns the engine's numbers into words. It never calculates: any number not in the engine's facts and the text is replaced by a template.</p></div>
      </div>
      <div className="grid g2">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <h3>Brief me before I call</h3>
            <button className="btn primary sm" onClick={() => brief.mutate()} disabled={brief.isPending}>{brief.isPending ? "Writing…" : "Brief me"}</button>
          </div>
          {brief.data && <div className="ai-box fade"><p style={{ margin: "0 0 8px" }}>{brief.data.text}</p><Source s={brief.data.source} /></div>}
          {brief.isError && <Failed error={brief.error} />}
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <h3>Message to the customer</h3>
            <div className="seg" role="group" aria-label="Language">
              {(["en", "fr"] as const).map((l) => <button key={l} className={lang === l ? "on" : ""} onClick={() => setLang(l)}>{l === "en" ? "English" : "Français"}</button>)}
            </div>
            <button className="btn ours sm" onClick={() => msg.mutate(lang)} disabled={msg.isPending}>{msg.isPending ? "Writing…" : "Draft message"}</button>
          </div>
          {msg.data && <div className="ai-box fade"><p style={{ margin: "0 0 8px" }}>{msg.data.text}</p>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}><Source s={msg.data.source} />
              <button className="btn sm" onClick={() => copy(msg.data!.text)}>{copied ? "Copied" : "Copy"}</button>
              <span className="muted" style={{ fontSize: 12 }}>No risk numbers go to the customer.</span></div></div>}
          {msg.isError && <Failed error={msg.error} />}
        </div>
      </div>
    </section>
  );
}


/** Why this customer is at risk and what the bank can do, most urgent first. The engine picks and sizes each action. */
function NextBestAction({ dx, nav, tested }: { dx: Diagnosis; nav: Nav; tested: Record<string, string> }) {
  const [first, ...rest] = dx.all;
  return (
    <section className="card nba">
      <div className="card-head"><div><h2>Why they're at risk, and what to do</h2>
        <p className="sub">Most urgent first. Every amount comes from this customer's own numbers.</p></div>
        <button className="btn ours" onClick={() => nav.go("plan")}>Open the plan →</button></div>
      <div className="nba-first">
        <span className="badge ours">Do this first</span>
        <h3>{first.title}</h3>
        <p className="why">{first.why}</p>
        <p className="act"><b>Action:</b> {first.action}</p>
        {tested[first.code] && <p className="sub tested">{tested[first.code]}</p>}
      </div>
      {rest.length > 0 && <div className="list">
        {rest.map((g) => (
          <div key={g.code} className="list-row">
            <b>{g.title}</b><span className="chip">{g.code === "dip" ? "Always" : "Also"}</span>
            <span className="how">{g.why} <b>Action:</b> {g.action}{tested[g.code] ? ` (${tested[g.code]})` : ""}</span>
          </div>))}
      </div>}
    </section>
  );
}

export default function CustomerScreen({ nav }: { nav: Nav }) {
  const q = useQuery({ queryKey: ["customer", nav.acct, nav.asof], queryFn: () => api.customer(nav.acct, nav.asof) });
  const ev = useQuery({ queryKey: ["evidence"], queryFn: api.evidence, staleTime: Infinity });
  if (q.isPending) return <main className="page"><Loading h={90} /><Loading h={140} /><Loading h={320} /></main>;
  if (q.isError) return <main className="page"><Failed error={q.error} /></main>;
  const c = q.data, t = c.trough, r = c.realistic;
  const next = c.what_happened_next ?? [];
  const overdrawnNext = next.filter((m) => m.days_below_zero > 0);
  // tested notes for each diagnosis, straight from evidence.json (2025 out-of-time results); display only
  const g25 = ev.data?.diagnoses?.by_year?.find((y: { year: number }) => y.year === 2025)?.groups;
  const im = ev.data?.impact?.["2024-12"];
  const tested: Record<string, string> = {};
  if (g25?.income_drop) tested.income_drop = `Tested: in 2025, flagged customers whose money in fell overdrew ${pct(g25.income_drop.rate)} vs ${pct(g25.income_drop.flagged_without_rate)} of other flagged customers.`;
  if (g25?.swing) tested.swing = `Tested: in 2025, flagged customers with big swings overdrew ${pct(g25.swing.rate)} vs ${pct(g25.swing.flagged_without_rate)}.`;
  if (im) tested.dip = `Tested: a buffer like this fully covered ${im.buffer.covered_in_full} of ${im.caught} caught first overdrafts in 2025; only ${kmoney(im.buffer.drawn_total)} of ${kmoney(im.buffer.limits_total)} in limits was ever used.`;
  if (c.repeat) tested.repeat = `Tested: ${pct(c.repeat.rate)} of customers like this were overdrawn again within a year (${c.repeat.tested_on}).`;

  return (
    <main className="page fade">
      <div>
        <p className="eyebrow">02 · Know the customer{c.asof ? ` · as of ${monthName(c.asof)}` : ""}</p>
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginTop: 6 }}>
          <h1 className="title" style={{ margin: 0 }}>Customer {c.account_id}</h1>
          {c.owner_age != null && <span className="badge muted">Owner {c.owner_age}</span>}
          {t?.bottom_10 && <span className="badge ours">Riskiest 10%</span>}
          {!t?.scorable && (c.tier?.key === "new_hot"
            ? <span className="badge ours" title={c.tier.action}>New and swinging: top 10% of new accounts</span>
            : <span className="badge muted">Too new to score</span>)}
        </div>
      </div>

      {(() => {   // the 10-second story for any account: four beats, every number from the API
        const nl = c.diagnosis?.signals?.new_loan, pr = c.diagnosis?.primary;
        const beats: [string, React.ReactNode][] = [
          ["Looks fine", <><b>{money(c.profile.buffer)}</b> on average. Standard runway: {c.standard_runway.label}.</>],
          ["The low point", t?.scorable ? <>Dipped to <b>{money(t.min_balance)}</b>: riskier than {pct(1 - (t.pct_rank ?? 0))} of customers.</> : <>Lowest balance {t ? money(t.min_balance) : "–"} (too new to rank).</>],
          ["What changed", nl ? <>New loan: <b>{money(nl.payment)}</b> a month. Realistic runway: <b>{c.realistic_runway.label}</b>.</>
            : c.risk.validated_population ? <><b>{pct(c.risk.p_12m, 1)}</b> chance of a first overdraft in 12 months. Realistic runway: {c.realistic_runway.label}.</>
            : c.repeat ? <>Already overdrawn: <b>{pct(c.repeat.rate)}</b> like them are overdrawn again within a year.</> : <>Realistic runway: <b>{c.realistic_runway.label}</b>.</>],
          ["Do this", pr ? <><b>{pr.short ?? pr.title}</b>: {pr.title.toLowerCase()}.</> : <>Alert + auto-transfer of <b>{money(c.cushion.buffer)}</b>.</>],
        ];
        return <section className="story" aria-label="The story in four steps">{beats.map(([h, b], i) => (
          <div key={h} className={`card ${i === 3 ? "ours" : ""}`}><p className="eyebrow">{i + 1} · {h}</p><p style={{ margin: "6px 0 0" }}>{b}</p></div>))}</section>;
      })()}

      <p className="summary">
        Over the last {r.window_months} months they brought in about <b>{money(r.income)}</b> a month and sent out <b>{money(r.spending_history)}</b>,
        {" "}with <b>{money(c.profile.buffer)}</b> on average in the account.
        {r.loan_adjust >= 1 && <> A new loan now costs <b>{money(r.loan_payments)}</b> a month, which isn't in that history yet.</>}
        {t?.scorable && <> But their balance dipped to <b>{money(t.min_balance)}</b>, {pct(t.ltr)} of the average.</>}
        {" "}Standard runway: <span className="s">{c.standard_runway.label}</span>. Realistic: <span className="o">{c.realistic_runway.label}</span>.
      </p>

      <section className="grid g4">
        <div className="card ink">
          {c.risk.validated_population
            ? <Kpi tip={GLOSSARY.risk} label="Chance of a first overdraft, next 12 months" value={<CountUp text={pct(c.risk.p_12m, 1)} />} note="Calibrated on 2024, checked on 2025. If nothing changes." />
            : c.repeat
              ? <Kpi tip="Tested out of time: among customers overdrawn this much in one year, the share overdrawn again the next year."
                  label="Overdrawn again within a year" value={pct(c.repeat.rate)}
                  note={`Below $0 on ${c.repeat.days_below_zero_12m} days in the last 12 months. Of ${c.repeat.similar_accounts} customers like this (${c.repeat.tested_on}), ${pct(c.repeat.rate)} were overdrawn again, vs ${pct(c.repeat.never_overdrawn_rate, 1)} of those never overdrawn.`} />
              : <Kpi label="First-overdraft forecast" value="n/a" size="md" note="Needs 12+ months of history" />}
        </div>
        <div className="card ours">
          <Kpi tip={GLOSSARY.trough} label="Liquidity trough (lowest ÷ average, 6 mo)" value={t ? pct(t.ltr) : "–"}
            note={t?.pct_rank != null ? `Riskier than ${pct(1 - t.pct_rank)} of customers` : "Needs 12+ months of history"} />
        </div>
        <div className="card"><Kpi swatch="std" tip={GLOSSARY.standard} label="Standard runway (no shock)" value={c.standard_runway.label} size="md" note="Judges' formula, medians" /></div>
        <div className="card"><Kpi swatch="ours" tip={GLOSSARY.realistic} label="Realistic runway (no shock)" value={c.realistic_runway.label} size="md" note="Last 12 months, dip-aware" /></div>
      </section>

      {c.diagnosis && <NextBestAction dx={c.diagnosis} nav={nav} tested={tested} />}

      {c.when && (
        <p className="callout" style={{ margin: 0 }}>
          <b>When?</b> Among the {c.when.customers.toLocaleString()} customers in the same group ({c.when.group}), {pct(c.when.within_6, 1)} had a first overdraft within 6 months,
          {" "}{pct(c.when.within_12, 1)} within 12 and {pct(c.when.within_24, 1)} within 24 ({c.when.cohort}; survival analysis).{c.when.group === "riskiest 10%" ? " Most of it comes early: act this week." : ""}
        </p>
      )}

      <Assistant key={`${c.account_id}-${c.asof}`} acct={c.account_id} asof={c.asof as Asof} />

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
          {c.committed && (
            <div className="card">
              <h3>Leaves every month by standing order: {money(c.committed.total)}</h3>
              <p className="sub" style={{ margin: "4px 0 8px" }}>Fixed commitments the customer can't cut. From the end-2025 snapshot, so hidden in Time Machine mode.</p>
              <div className="chips">{Object.entries(c.committed.by_purpose).map(([k, v]) => <span key={k} className="chip">{k} {money(v)}</span>)}</div>
            </div>
          )}
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
              {c.loan_check && (
                <p className={`callout ${c.loan_check.hold ? "bad" : ""}`} style={{ marginTop: 10 }}>
                  {c.loan_check.hold
                    ? <>A review rule at approval, using only data up to {monthName(c.loan_check.data_up_to)}, <b>would have held this loan</b>: {c.loan_check.reasons.join("; ")}.</>
                    : <>A review rule at approval would have passed this loan (data up to {monthName(c.loan_check.data_up_to)}).</>}
                </p>
              )}
            </div>
          )}
        </div>
      </section>

      <details className="card fold">
        <summary><h2>The judges' numbers</h2><span className="sub">I, S, B, H, F, P from the Tangerine README. Standard runway: {c.standard_runway.label}. Show the table</span></summary>
        <div className="card-head"><div><h2 className="sr-only">The judges' numbers</h2><p className="sub">Exactly the Tangerine README definitions, from monthly_summary.csv.</p></div>
          <button className="btn" onClick={() => nav.go("stress")}>Apply a shock →</button></div>
        <table className="tbl">
          <tbody>
            {([["I", "Typical monthly money in (median)", c.profile.income], ["S", "Typical monthly money out (median)", c.profile.spending],
              ["B", "Buffer (mean average daily balance, last 6 months)", c.profile.buffer], ["H", "Household bills (median)", c.profile.household_bills],
              ["F", "Fixed costs (median bills + insurance + loans)", c.profile.fixed_costs], ["P", "Loan payment (running at end of 2025)", c.profile.loan_payment]] as const)
              .map(([k, label, v]) => <tr key={k}><td style={{ width: 40 }}><b>{k}</b></td><td>{label}</td><td className="num">{money(v)}</td></tr>)}
          </tbody>
        </table>
      </details>
    </main>
  );
}
