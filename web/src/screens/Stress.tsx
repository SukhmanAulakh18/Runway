import { useEffect, useState } from "react";
import { keepPreviousData, useMutation, useQuery } from "@tanstack/react-query";
import { api, money, monthName, NO_SHOCK, pct, type Scenario, type Twist, type Verdict } from "../api";
import type { Nav } from "../App";
import { FanChart, Legend } from "../charts";
import { Failed, GLOSSARY, Info, Kpi, Loading } from "./ui";

const PRESETS: { label: string; text: string }[] = [
  { label: "Job loss, EI 55%", text: "This customer was laid off. EI pays 55% of their usual income for 6 months." },
  { label: "Furnace: 1 month of spending", text: "The furnace dies, and the repair costs a full month of their typical spending." },
  { label: "Job loss + bills +15%", text: "They lose their job (EI at 55%) and their household bills go up 15% in the same month." },
];

function Futures({ p, months }: { p: number; months: number }) {
  const n = Math.round(p * 10);
  return (
    <div>
      <div className="dots" role="img" aria-label={`${n} of 10 simulated futures last ${months} months`}>
        {Array.from({ length: 10 }, (_, i) => <span key={i} className={`dot ${i < n ? "on" : ""}`} />)}
      </div>
      <p style={{ margin: "8px 0 0", fontWeight: 600 }}>{n} of 10 simulated futures stay above the overdraft line for {months} months</p>
    </div>
  );
}

function VerdictCard({ v }: { v: Verdict }) {
  const scale = Math.max(1, ...v.drivers.map((x) => Math.abs(x.months ?? 0)));
  return (
    <section className={`verdict ${v.answer} fade`} aria-live="polite">
      <div className="verdict-tag">{({ yes: "Yes", no: "No", paper: "Only on paper", fragile: "Fragile" } as const)[v.answer]}</div>
      <div>
        <p className="eyebrow">Do they make it {v.threshold_months} months?</p>
        <h2 className="verdict-h">{v.headline}</h2>
        {v.reason && <p style={{ margin: 0 }}>{v.reason}</p>}
        {v.futures && <p className="sub" style={{ marginTop: 6 }}>{v.futures}</p>}
      </div>
      {v.drivers.length > 0 && (
        <div className="drivers">
          <h3>What moves the answer <Info tip="Each bar flips one of our realistic choices back to the standard formula and measures how many months of runway it moves." /></h3>
          {v.drivers.map((x) => (
            <div key={x.driver} className="row">
              <span>{x.driver}</span>
              <div className="track"><div className={`fill ${x.direction > 0 ? "up" : ""}`} style={{ width: `${x.months == null ? 100 : (Math.abs(x.months) / scale) * 100}%` }} /></div>
              <b>{x.months == null ? "decisive" : `${x.months > 0 ? "+" : ""}${x.months} mo`}</b>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function Slider({ label, value, min, max, step, fmt, on }: { label: string; value: number; min: number; max: number; step: number; fmt: (v: number) => string; on: (v: number) => void }) {
  return (
    <label className="field">
      <span>{label}</span><output>{fmt(value)}</output>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => on(Number(e.target.value))} />
    </label>
  );
}

export default function Stress({ nav }: { nav: Nav }) {
  const [sc, setSc] = useState<Scenario>(nav.scenario);
  const [text, setText] = useState("");
  const [read, setRead] = useState<Twist | null>(null);
  useEffect(() => { const t = setTimeout(() => nav.setScenario(sc), 250); return () => clearTimeout(t); }, [sc]); // eslint-disable-line react-hooks/exhaustive-deps
  const set = (patch: Partial<Scenario>) => setSc({ ...sc, ...patch });

  const twist = useMutation({ mutationFn: api.twist, onSuccess: (t) => { setRead(t); setSc({ ...NO_SHOCK, ...t.settings }); } });
  const readCard = (t: string) => { setText(t); if (t.trim()) twist.mutate(t); };
  const q = useQuery({ queryKey: ["shock", nav.acct, nav.asof, nav.scenario], queryFn: () => api.shock(nav.acct, nav.asof, nav.scenario),
    placeholderData: keepPreviousData });

  return (
    <main className="page fade">
      <div>
        <p className="eyebrow">03 · Stress test · customer {nav.acct}{nav.asof ? ` · as of ${monthName(nav.asof)}` : ""}</p>
        <h1 className="title">Read the twist card. <em>Do they make it?</em></h1>
      </div>

      <section className="grid g-7-5" style={{ alignItems: "start" }}>
        <div className="card">
          <h2>Twist card</h2>
          <p className="sub" style={{ marginBottom: 10 }}>Type it as the judge reads it. The engine only runs on the settings you see below.</p>
          <textarea className="card-input" value={text} onChange={(e) => setText(e.target.value)} placeholder="e.g. Laid off, EI pays 55% for 6 months, and the furnace dies"
            onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) readCard(text); }} />
          <div className="chips" style={{ marginTop: 10, alignItems: "center" }}>
            <button className="btn primary" onClick={() => readCard(text)} disabled={twist.isPending}>{twist.isPending ? "Reading…" : "Read card"}</button>
            {PRESETS.map((p) => <button key={p.label} className="btn sm" onClick={() => readCard(p.text)}>{p.label}</button>)}
            <button className="btn sm" onClick={() => { setText(""); setRead(null); setSc(NO_SHOCK); }}>Reset</button>
          </div>
          {twist.isError && <p className="err" style={{ marginTop: 10 }}>Couldn't read the card. Set the shock with the controls.</p>}
          {read && (
            <div style={{ marginTop: 14 }}>
              <span className="muted" style={{ fontSize: 12.5 }}>Understood by {read.source}:</span>
              <div className="chips" style={{ marginTop: 6 }}>{read.chips.map((c) => <span key={c} className="chip ours">{c}</span>)}</div>
              {read.disagree.length > 0 && <p className="chip amber" style={{ marginTop: 8, display: "inline-block" }}>
                AI and rules read these differently, check them: {read.disagree.join(", ")}</p>}
            </div>
          )}
        </div>

        <div className="card">
          <h2>Shock settings</h2>
          <div className="grid" style={{ marginTop: 12, gap: 14 }}>
            <label className="toggle"><input type="checkbox" checked={sc.job_loss} onChange={(e) => set({ job_loss: e.target.checked })} /> Job loss (EI)</label>
            {sc.job_loss && <>
              <Slider label="EI pays" value={sc.ei_rate} min={0} max={1} step={0.05} fmt={(v) => pct(v)} on={(v) => set({ ei_rate: v })} />
              <Slider label="EI lasts" value={sc.ei_months} min={0} max={10} step={1} fmt={(v) => `${v} months`} on={(v) => set({ ei_months: v })} />
              <Slider label="Share of money in that is pay" value={sc.employment_share} min={0.2} max={1} step={0.1} fmt={(v) => pct(v)} on={(v) => set({ employment_share: v })} />
              <p className="sub" style={{ marginTop: -6 }}>Our biggest assumption: most money in is cash, so we can't see what is salary. 100% = a job loss stops all non-pension money in.</p>
            </>}
            <Slider label="Household bills" value={sc.bills_increase_pct} min={0} max={0.5} step={0.05} fmt={(v) => `+${pct(v)}`} on={(v) => set({ bills_increase_pct: v })} />
            <Slider label="One-off repair" value={sc.one_off_cost} min={0} max={20000} step={500} fmt={money} on={(v) => set({ one_off_cost: v })} />
            <Slider label="…or in months of typical spending" value={sc.one_off_months_of_spending} min={0} max={3} step={0.5} fmt={(v) => `${v} mo`} on={(v) => set({ one_off_months_of_spending: v })} />
          </div>
        </div>
      </section>

      {q.isPending ? <Loading h={360} /> : q.isError ? <Failed error={q.error} /> : (() => {
        const s = q.data, sim = s.simulation, k = s.standard;
        return (
          <div className="grid fade" style={{ gap: 16, opacity: q.isPlaceholderData ? 0.6 : 1, transition: "opacity .2s" }}>
            <VerdictCard v={s.verdict} />
            <section className="grid g3">
              <div className="card"><Kpi swatch="std" tip={GLOSSARY.standard} label="Standard runway (judges' formula)" value={k.label} note={`Money in ${money(k.income_after)} vs money out ${money(k.spending_after)} a month`} /></div>
              <div className="card ours"><Kpi swatch="ours" tip={GLOSSARY.realistic} label="Realistic runway" value={s.realistic.label}
                note={s.realistic.ei_capped ? `EI capped at ${money(s.realistic.ei_monthly)}/month (2026 maximum)` : "Last 12 months, EI stops, pensions kept, dip-aware"} /></div>
              <div className="card ink"><span className="kpi"><span className="label">Simulated futures<Info tip={GLOSSARY.futures} /></span></span><Futures p={sim.p_survive_6} months={6} />
                <p className="sub" style={{ marginTop: 6 }}>{Math.round(sim.p_survive_12 * 10)} of 10 last 12 months. {sim.n_paths.toLocaleString()} futures replayed from their own last {sim.history_months} months.</p></div>
            </section>

            <section className="grid g-7-5" style={{ alignItems: "start" }}>
              <div className="card">
                <h2>Monte Carlo: {sim.n_paths.toLocaleString()} futures built from their own months</h2>
                <p className="sub" style={{ marginBottom: 8 }}>Starts at today's balance{s.scenario.one_off_cost || s.scenario.one_off_months_of_spending ? " minus the one-off" : ""}. Below the red line, a normal month takes them under $0.</p>
                {sim.insufficient_history && <p className="chip amber">Only {sim.history_months} months of history: treat this as rough.</p>}
                <FanChart sim={sim} eiEnds={s.scenario.job_loss ? s.scenario.ei_months : null} />
                <Legend items={[{ label: "Typical future", kind: "ours" }, { label: "Middle 80% of futures", kind: "soft" }, { label: "Overdraft line", kind: "bad" }]} />
                {sim.ee && sim.pfe95 && (
                  <details className="judge" style={{ marginTop: 12 }}>
                    <summary>For risk teams: the bank's exposure profile under this shock</summary>
                    <p className="sub" style={{ margin: "6px 0" }}>How far below $0 the in-month low goes across the same futures: expected exposure (average over all futures)
                      and potential future exposure (95th percentile), the same exposure-profile idea used in counterparty credit risk.
                      From the raw simulation, before calibration: compare shocks with it, don't read it as a loss forecast.</p>
                    <table className="tbl"><thead><tr><th>Month</th><th className="num">Expected exposure</th><th className="num">95% exposure</th></tr></thead>
                      <tbody>{[3, 6, 12, 24].filter((mo) => mo <= sim.months.length).map((mo) => (
                        <tr key={mo}><td>{mo}</td><td className="num">{money(sim.ee![mo - 1])}</td><td className="num">{money(sim.pfe95![mo - 1])}</td></tr>))}
                      </tbody></table>
                  </details>
                )}
              </div>
              <div className="card">
                <h2>Why the two runways differ</h2>
                {s.why_different.length ? <div className="list">{s.why_different.map((w) => <div key={w} className="list-row"><span>{w}</span></div>)}</div>
                  : <p className="sub">They agree for this customer and shock.</p>}
                <details className="judge" style={{ marginTop: 14 }}>
                  <summary>Judge check: the standard formula with the numbers in</summary>
                  <table className="tbl" style={{ marginTop: 8 }}><tbody>
                    {([["I (median money in)", s.judge_check.I], ["S (median money out)", s.judge_check.S], ["B (buffer)", s.judge_check.B], ["H (household bills)", s.judge_check.H],
                      ["Money in after shock", k.income_after], ["Money out after shock", k.spending_after], ["One-off costs", k.one_off], ["Buffer left", k.buffer_left ?? 0], ["Monthly gap", k.monthly_gap]] as const)
                      .map(([l, v]) => <tr key={l}><td>{l}</td><td className="num">{money(v)}</td></tr>)}
                  </tbody></table>
                  <code>runway = buffer left ÷ gap = {money(k.buffer_left ?? 0)} ÷ {money(k.monthly_gap)} → {k.label}</code>
                </details>
                <button className="btn ours" style={{ marginTop: 14 }} onClick={() => nav.go("plan")}>Make a plan for this shock →</button>
              </div>
            </section>
          </div>
        );
      })()}
    </main>
  );
}
