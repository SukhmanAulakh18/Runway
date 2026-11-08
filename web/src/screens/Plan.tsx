import { keepPreviousData, useMutation, useQuery } from "@tanstack/react-query";
import { api, kmoney, money, monthName, pct } from "../api";
import type { Nav } from "../App";
import { Legend, OptimiserChart } from "../charts";
import { Failed, Kpi, Loading } from "./ui";

export default function Plan({ nav }: { nav: Nav }) {
  const q = useQuery({ queryKey: ["plan", nav.acct, nav.asof, nav.scenario], queryFn: () => api.plan(nav.acct, nav.asof, nav.scenario),
    placeholderData: keepPreviousData });
  const ev = useQuery({ queryKey: ["evidence"], queryFn: api.evidence, staleTime: Infinity });
  const write = useMutation({ mutationFn: api.writePlan });
  const s = nav.scenario;
  const shocked = s.job_loss || s.bills_increase_pct > 0 || s.one_off_cost > 0 || s.one_off_months_of_spending > 0 || s.income_cut > 0 || s.spending_increase !== 0;

  if (q.isPending) return <main className="page"><Loading h={180} /><Loading h={300} /></main>;
  if (q.isError) return <main className="page"><Failed error={q.error} /></main>;
  const p = q.data, cu = p.cushion, o = p.optimiser, im = ev.data?.impact?.["2024-12"];
  const levers = p.backup.levers.filter((l) => l.gain !== 0);

  return (
    <main className="page fade" style={{ opacity: q.isPlaceholderData ? 0.6 : 1 }}>
      <div>
        <p className="eyebrow">04 · Make a plan · customer {nav.acct}{nav.asof ? ` · as of ${monthName(nav.asof)}` : ""}</p>
        <h1 className="title">Fix the cause first. <em>Then plan for the shock.</em></h1>
      </div>

      {p.diagnosis && p.diagnosis.primary.code !== "dip" && (
        <section className="card nba">
          <div className="nba-first">
            <span className="badge ours">Do this first</span>
            <h3>{p.diagnosis.primary.title}</h3>
            <p className="why">{p.diagnosis.primary.why}</p>
            <p className="act"><b>Action:</b> {p.diagnosis.primary.action}</p>
          </div>
        </section>
      )}

      <section className="grid g-7-5">
        <div className="card hero">
          <p className="eyebrow" style={{ color: "#ffe7d6" }}>{p.diagnosis && p.diagnosis.primary.code !== "dip" ? "Then: cover the dip" : "Goal plan · do this now"}</p>
          <div className="grid g3" style={{ marginTop: 12 }}>
            <Kpi label="1 · Alert them (free, no risk)" value={money(cu.alert_level)} note="When the balance falls below this: their own danger level, not a generic $100" />
            <Kpi label="2 · Auto-transfer from savings" value={money(cu.buffer)} note="Sized to their typical in-month dip. A small overdraft limit only after a call." />
            <Kpi label="Move to chequing now" value={cu.top_up_now > 0 ? money(cu.top_up_now) : "Nothing"} size={cu.top_up_now > 0 ? undefined : "md"} note={`Balance ${money(cu.last_balance)} at ${monthName(cu.as_of)}`} />
          </div>
          {p.limit_cost && <p style={{ margin: "14px 0 0" }}>Cost to the customer: the alert <b>$0</b>, the auto-transfer from savings <b>$0</b>. A {money(p.limit_cost.amount)} limit used for a whole month at Tangerine's published terms ($5 a month used + 19% a year) would cost about <b>{money(p.limit_cost.total)}</b>, which is why it comes last.</p>}
          {cu.dip_day_reliable && cu.dip_day && <p style={{ margin: "14px 0 0" }}>Their balance usually bottoms out around <b>day {cu.dip_day}</b> of the month ({pct(cu.dip_day_share)} of months): time the alert for then.</p>}
        </div>
        <div className="card">
          <h2>Does a dip-sized cushion work? Backtested on 2025</h2>
          {im ? <>
            <p style={{ margin: "10px 0 6px" }}>For the riskiest 10% at Dec 2024, a cushion like this fully covered <b>{im.buffer.covered_in_full} of {im.caught}</b> caught first overdrafts.</p>
            <p style={{ margin: "6px 0" }}>Only <b>{kmoney(im.buffer.drawn_total)}</b> of <b>{kmoney(im.buffer.limits_total)}</b> in limits was ever used: it works as a limit, not cash.</p>
            <p style={{ margin: "6px 0 0" }}>The personal alert fired before <b>{im.alert.fired_before} of {im.caught}</b>, a median {im.alert.median_lead_months} months early. A $100 alert: {im.alert.generic_100_fired_before}.
              {im.alert.fired_for_quiet_share != null && <> It pinged only {pct(im.alert.fired_for_quiet_share)} of flagged customers who never went overdrawn.</>}</p>
          </> : <Loading h={100} />}
        </div>
      </section>

      <section className="grid g-7-5" style={{ alignItems: "start" }}>
        <div className="card">
          <h2>{o.protected_months > o.base_months
            ? `Smallest cuts that keep them out of overdraft: ${o.protected_months} months instead of ${o.base_months}`
            : o.base_months >= o.horizon ? `No cuts needed: safe for all ${o.horizon} months in a ${o.outcome}` : `Cuts alone can't protect month ${o.base_months + 1}: they need a bridge first`}</h2>
          <p className="sub" style={{ marginBottom: 8 }}>
            Linear program over the simulated path for {o.outcome}{shocked ? ", under your shock" : ""}. Bills and insurance are never cut; at most {money(o.max_monthly_cut)}/month.
            {o.protected_months > o.base_months && <> Average cut {money(o.avg_monthly_cut)}/month.</>}
            {o.share_of_futures_protected != null && <> Keeps {pct(o.share_of_futures_protected)} of whole simulated futures safe.</>}
          </p>
          <OptimiserChart path={o.path} protectedPath={o.protected_path} cuts={o.cuts} dip={o.dip} />
          <Legend items={[{ label: "With the cuts", kind: "ours" }, { label: "Without changes", kind: "std" }, { label: "Monthly cut", kind: "soft" }, { label: "Overdraft line", kind: "bad" }]} />
        </div>
        <div className="card">
          <h2>Backup plan if the shock hits</h2>
          <p className="sub">Ranked by months of runway each action buys. Current realistic runway: {p.backup.base_runway} months.</p>
          {!shocked && <p className="chip amber" style={{ display: "inline-block" }}>No shock set yet. <button className="btn sm" onClick={() => nav.go("stress")}>Apply one in Stress test</button></p>}
          <div className="list" style={{ marginTop: 6 }}>
            {levers.length ? levers.map((l) => (
              <div key={l.action} className="list-row">
                <b>{l.action}</b>
                <span className="chip ours">{l.gain == null ? "120+ months" : `+${l.gain} months`}</span>
                <span className="how">{l.how}{l.monthly_saving > 0 ? ` · saves ${money(l.monthly_saving)}/month` : ""}</span>
              </div>
            )) : <p className="sub">No action changes the runway for this shock.</p>}
          </div>
        </div>
      </section>

      <section className="grid g2" style={{ alignItems: "start" }}>
        <div className="card">
          <h2>Emergency fund for a job loss</h2>
          <p className="sub">Milestones toward surviving months on (capped) EI. Saving {money(p.goal.stretch_saving)}/month on the stretch plan.</p>
          <div className="list" style={{ marginTop: 6 }}>
            {p.goal.milestones.map((m) => (
              <div key={m.name} className="list-row">
                <b>{m.name}</b>
                {m.done ? <span className="chip good">Done</span> : <span className="chip">{money(m.need)} to go</span>}
                <span className="how">Target {money(m.target)}{!m.done && (m.months_stretch ?? m.months_steady) ? ` · about ${Math.round((m.months_stretch ?? m.months_steady)!)} months` : ""}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="card-head"><div><h2>The plan, in plain English</h2>
            <p className="sub">AI writes the words; every number is checked against the engine, or a template is used.</p></div>
            <button className="btn primary" onClick={() => write.mutate(p.facts)} disabled={write.isPending}>{write.isPending ? "Writing…" : "Write the plan"}</button></div>
          {write.data && <div className="fade"><p style={{ margin: 0, fontSize: 15.5 }}>{write.data.text}</p>
            <p className="sub" style={{ marginTop: 8 }}>Written by {write.data.source}</p></div>}
          {write.isError && <Failed error={write.error} />}
        </div>
      </section>
    </main>
  );
}
