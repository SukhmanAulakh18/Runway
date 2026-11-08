import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api, money, monthName, pct, type Asof } from "../api";
import type { Nav } from "../App";
import { BalanceChart, Legend } from "../charts";
import { Failed, GLOSSARY, Info, Kpi, Loading } from "./ui";

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
            ? <Kpi tip={GLOSSARY.risk} label="Chance of a first overdraft, next 12 months" value={pct(c.risk.p_12m, 1)} note="Calibrated on 2024, checked on 2025. If nothing changes." />
            : <Kpi label="First-overdraft forecast" value="n/a" size="md" note="Only for customers with 12+ months who were never overdrawn" />}
        </div>
        <div className="card ours">
          <Kpi tip={GLOSSARY.trough} label="Liquidity trough (lowest ÷ average, 6 mo)" value={t ? pct(t.ltr) : "–"}
            note={t?.pct_rank != null ? `Riskier than ${pct(1 - t.pct_rank)} of customers` : "Needs 12+ months of history"} />
        </div>
        <div className="card"><Kpi swatch="std" tip={GLOSSARY.standard} label="Standard runway (no shock)" value={c.standard_runway.label} size="md" note="Judges' formula, medians" /></div>
        <div className="card"><Kpi swatch="ours" tip={GLOSSARY.realistic} label="Realistic runway (no shock)" value={c.realistic_runway.label} size="md" note="Last 12 months, dip-aware" /></div>
      </section>

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
          <div className="card ours">
            <h2>The fix: a cushion sized to their own dip <Info tip={GLOSSARY.cushion} /></h2>
            <p style={{ margin: "8px 0 12px" }}>Keep <b>{money(c.cushion.buffer)}</b> available (overdraft protection or an auto-transfer), the size of their usual in-month dip, and alert them before the balance gets that low.
              {c.cushion.dip_day_reliable && c.cushion.dip_day && <> Their balance usually bottoms out around day {c.cushion.dip_day}.</>}</p>
            <button className="btn ours" onClick={() => nav.go("plan")}>Open the plan →</button>
          </div>
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
