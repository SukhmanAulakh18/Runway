import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ASOF_LABEL, NO_SHOCK, type Asof, type Scenario } from "./api";
import Overview from "./screens/Overview";
import CustomerScreen from "./screens/Customer";
import Stress from "./screens/Stress";
import Plan from "./screens/Plan";
import Evidence from "./screens/Evidence";

export type Tab = "overview" | "customer" | "stress" | "plan" | "evidence";
const STEPS: { id: Tab; n: string; name: string; hint: string }[] = [
  { id: "overview", n: "01", name: "Who's at risk", hint: "The finding + watchlist" },
  { id: "customer", n: "02", name: "Know the customer", hint: "Money in, out, the dip" },
  { id: "stress", n: "03", name: "Stress test", hint: "Twist card + Monte Carlo" },
  { id: "plan", n: "04", name: "Make a plan", hint: "Cushion, cuts, backup" },
  { id: "evidence", n: "05", name: "Why trust it", hint: "Backtests and limits" },
];
const PITCH: { tab: Tab; title: string; cue: string; shock?: Partial<Scenario> }[] = [
  { tab: "overview", title: "The finding", cue: "Banks watch the average; overdrafts happen at the low point. Point at the four headline numbers, then the call list: every row has its own next step." },
  { tab: "customer", title: "One customer", cue: "Read the four steps left to right: looks fine, the low point, the new loan, call this week. The loan card says a check at approval would have held it." },
  { tab: "stress", title: "A twist card", cue: "Job loss plus bills up 15%. Read the verdict first, then 'What moves the answer'. The judges' formula is under 'Judge check'.", shock: { job_loss: true, bills_increase_pct: 0.15 } },
  { tab: "plan", title: "The plan", cue: "Fix the cause first. Then the no-risk steps: an alert and a transfer from savings. A limit comes last, with its real cost.", shock: { job_loss: true, bills_increase_pct: 0.15 } },
  { tab: "evidence", title: "Why trust it", cue: "Tested on years the model never saw. Model health shows no breaches, and everything that failed is listed. Now: pick any account and any twist card." },
];

export interface Nav { acct: number; asof: Asof; scenario: Scenario; go: (t: Tab, acct?: number, asof?: Asof) => void; setScenario: (s: Scenario) => void }

function readUrl() {
  const p = new URLSearchParams(location.search);
  const asof = p.get("asof");
  return { tab: (p.get("tab") as Tab) || "overview", acct: Number(p.get("acct")) || 93172,
           asof: (asof === "2024-12" || asof === "2023-12" ? asof : null) as Asof };
}

export default function App() {
  const init = readUrl();
  const [tab, setTab] = useState<Tab>(init.tab);
  const [acct, setAcct] = useState(init.acct);
  const [asof, setAsof] = useState<Asof>(init.asof);
  const [scenario, setScenario] = useState<Scenario>(NO_SHOCK);
  const [draft, setDraft] = useState(String(init.acct));
  const qc = useQueryClient();
  const health = useQuery({ queryKey: ["health"], queryFn: api.health });
  const accounts = useQuery({ queryKey: ["accounts"], queryFn: api.accounts, staleTime: Infinity });

  useEffect(() => {
    const p = new URLSearchParams({ tab, acct: String(acct), ...(asof ? { asof } : {}) });
    history.replaceState(null, "", `?${p}`);
  }, [tab, acct, asof]);
  useEffect(() => setDraft(String(acct)), [acct]);
  useEffect(() => {   // prewarm the pitch moment so Demo mode is instant
    qc.prefetchQuery({ queryKey: ["customer", 93172, "2024-12"], queryFn: () => api.customer(93172, "2024-12") });
    qc.prefetchQuery({ queryKey: ["watchlist", "2024-12"], queryFn: () => api.watchlist("2024-12") });
  }, [qc]);

  const go = (t: Tab, a?: number, w?: Asof) => { if (a) setAcct(a); if (w !== undefined) setAsof(w); setTab(t); window.scrollTo({ top: 0 }); };   // w: undefined keeps the Time Machine, null = Today
  const [step, setStep] = useState<number | null>(null);
  const pitch = (i: number | null) => {
    setStep(i);
    if (i === null) return;
    setAsof("2024-12"); setScenario({ ...NO_SHOCK, ...PITCH[i].shock }); go(PITCH[i].tab, 93172);
  };
  useEffect(() => {   // arrow keys move through the pitch; Esc leaves it
    if (step === null) return;
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.closest("input, textarea")) return;
      if (e.key === "ArrowRight" && step < PITCH.length - 1) pitch(step + 1);
      if (e.key === "ArrowLeft" && step > 0) pitch(step - 1);
      if (e.key === "Escape") pitch(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [step]); // eslint-disable-line react-hooks/exhaustive-deps
  const open = () => {
    const n = Number(draft);
    if (accounts.data?.includes(n)) go(tab === "overview" || tab === "evidence" ? "customer" : tab, n);
  };
  const unknown = draft !== "" && accounts.data && !accounts.data.includes(Number(draft));
  const nav: Nav = { acct, asof, scenario, go, setScenario };

  return (
    <div className="app">
      <aside className="rail">
        <div className="brand">
          <svg width="30" height="30" viewBox="0 0 32 32" aria-hidden><rect width="32" height="32" rx="8" fill="#f26a1b" />
            <path d="M7 22c4-9 8-9 9-2s5 4 9-9" stroke="#ffffff" strokeWidth="3" fill="none" strokeLinecap="round" /></svg>
          <div><b>Runway</b><small>Liquidity early warning</small></div>
        </div>
        <nav className="steps" aria-label="Steps">
          {STEPS.map((s) => (
            <button key={s.id} className={`step ${tab === s.id ? "on" : ""}`} onClick={() => go(s.id)} aria-current={tab === s.id}>
              <i>{s.n}</i><span>{s.name}</span><em>{s.hint}</em>
            </button>
          ))}
        </nav>
        <div className="rail-foot">
          <p><span className="swatch ours" /> Ours (realistic)</p>
          <p><span className="swatch std" /> Standard formula (judges')</p>
          <p style={{ marginTop: 12 }}>Tangerine track · Sheridan Datathon 2026. Data: PKDD'99 Financial, re-dated.</p>
        </div>
      </aside>

      <div className="main">
        <header className="top">
          <form className="search" onSubmit={(e) => { e.preventDefault(); open(); }}>
            <label htmlFor="acct">Account</label>
            <input id="acct" inputMode="numeric" value={draft} onChange={(e) => setDraft(e.target.value.replace(/\D/g, ""))}
              aria-invalid={!!unknown} />
            <button className="btn primary sm" type="submit" disabled={!!unknown}>Open</button>
          </form>
          {unknown && <span className="pill" style={{ color: "#8f2520" }}>Not an account</span>}
          <span className="seg-label">Time Machine</span>
          <div className="seg" role="group" aria-label="Time Machine">
            {(["", "2024-12", "2023-12"] as const).map((k) => (
              <button key={k} className={(asof ?? "") === k ? "on" : ""} onClick={() => setAsof((k || null) as Asof)}>{ASOF_LABEL[k]}</button>
            ))}
          </div>
          <button className="btn ours" onClick={() => pitch(0)} aria-pressed={step !== null}>
            {step === null ? "▶ Pitch mode" : "Pitch mode on"}
          </button>
          <span className="spacer" />
          <span className={`pill ${health.data?.ai?.toLowerCase().includes("gemini") ? "ai" : ""}`} title="AI reads twist cards and writes plans; it never calculates">
            AI: {health.data?.ai ?? "…"}
          </span>
        {step !== null && (
            <div className="pitchbar" role="region" aria-label="Pitch mode">
              <div className="pitch-dots">{PITCH.map((p, i) => <button key={p.title} className={i === step ? "on" : ""} onClick={() => pitch(i)} aria-label={`Step ${i + 1}: ${p.title}`} />)}</div>
              <div className="pitch-text"><b>{step + 1} / {PITCH.length} · {PITCH[step].title}</b><span>{PITCH[step].cue}</span></div>
              <div className="pitch-btns">
                <button className="btn sm" onClick={() => pitch(step - 1)} disabled={step === 0}>← Back</button>
                {step < PITCH.length - 1
                  ? <button className="btn ours sm" onClick={() => pitch(step + 1)}>Next →</button>
                  : <button className="btn primary sm" onClick={() => pitch(null)}>Done</button>}
                <button className="btn sm" onClick={() => pitch(null)} aria-label="Leave pitch mode">Esc</button>
              </div>
            </div>
          )}
        </header>

        {tab === "overview" && <Overview nav={nav} />}
        {tab === "customer" && <CustomerScreen nav={nav} />}
        {tab === "stress" && <Stress nav={nav} />}
        {tab === "plan" && <Plan nav={nav} />}
        {tab === "evidence" && <Evidence />}

      </div>
    </div>
  );
}
