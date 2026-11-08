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
export interface Nav { acct: number; asof: Asof; scenario: Scenario; go: (t: Tab, acct?: number) => void; setScenario: (s: Scenario) => void }

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

  const go = (t: Tab, a?: number) => { if (a) setAcct(a); setTab(t); window.scrollTo({ top: 0 }); };
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
          <button className="btn ours" onClick={() => { setAsof("2024-12"); setScenario(NO_SHOCK); go("customer", 93172); }}>
            Demo mode
          </button>
          <span className="spacer" />
          <span className={`pill ${health.data?.ai?.toLowerCase().includes("gemini") ? "ai" : ""}`} title="AI reads twist cards and writes plans; it never calculates">
            AI: {health.data?.ai ?? "…"}
          </span>
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
