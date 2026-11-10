import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, money, pct } from "../api";
import { Failed, Loading } from "./ui";

const FLAGS = [0.02, 0.05, 0.10, 0.20, 0.30];
const num = (s: string) => (s.trim() === "" ? null : Number(s));

/** For the bank: the measured flag-size trade-off, scaled to its book, with its own costs and a pilot size. Display only:
 *  every figure comes from POST /api/bank-case (engine.bank_case). The dollar fields start empty: nothing is assumed. */
export default function BankCase() {
  const [customers, setCustomers] = useState("100000");
  const [flag, setFlag] = useState(0.10);
  const [cost, setCost] = useState("");
  const [value, setValue] = useState("");
  const [prevent, setPrevent] = useState(100);
  const [drop, setDrop] = useState(25);
  const n = Number(customers), c = num(cost), v = num(value);
  const ok = Number.isFinite(n) && n >= 1 && (c === null || (Number.isFinite(c) && c >= 0)) && (v === null || (Number.isFinite(v) && v >= 0));
  const req = { customers: Math.round(n), flag_share: flag, cost_per_call: c, value_per_prevented: v, prevent_rate: prevent / 100, relative_reduction: drop / 100 };
  const q = useQuery({ queryKey: ["bankcase", req], queryFn: () => api.bankCase(req), enabled: ok, placeholderData: keepPreviousData });
  const b = q.data;

  return (
    <div style={{ marginTop: 12 }}>
      <p className="sub">The catches come from our backtest on 2024 and 2025 (each tested on a year the model never saw). The dollar figures are yours: nothing is assumed.
        A catch is a flagged customer who then went overdrawn; whether a call prevents it is what a pilot shows.</p>
      <div className="bankform">
        <div className="field"><label htmlFor="bc-n">Customers in your book</label>
          <input id="bc-n" type="number" min={1} value={customers} onChange={(e) => setCustomers(e.target.value)} /></div>
        <div className="field"><label htmlFor="bc-cost">What one call costs ($)</label>
          <input id="bc-cost" type="number" min={0} placeholder="your figure" value={cost} onChange={(e) => setCost(e.target.value)} /></div>
        <div className="field"><label htmlFor="bc-val">What preventing one overdraft is worth ($)</label>
          <input id="bc-val" type="number" min={0} placeholder="your figure" value={value} onChange={(e) => setValue(e.target.value)} /></div>
        <div className="field"><label htmlFor="bc-prev">Share of caught overdrafts a call prevents: {prevent}%</label>
          <input id="bc-prev" type="range" min={5} max={100} step={5} value={prevent} onChange={(e) => setPrevent(Number(e.target.value))} />
          <small className="muted">100% is the best case; the pilot finds the real number</small></div>
        <div className="field"><label htmlFor="bc-drop">Pilot: drop in first overdrafts to detect: {drop}%</label>
          <input id="bc-drop" type="range" min={10} max={50} step={5} value={drop} onChange={(e) => setDrop(Number(e.target.value))} /></div>
      </div>
      <div role="group" aria-label="Flag the riskiest customers" className="chips" style={{ marginBottom: 10 }}>
        <span className="sub" style={{ alignSelf: "center" }}>Flag the riskiest</span>
        {FLAGS.map((f) => <button key={f} type="button" className="btn sm" aria-pressed={f === flag} onClick={() => setFlag(f)}>{pct(f)}</button>)}
      </div>

      {!ok ? <p className="chip amber">Enter a customer count of at least 1, and costs of zero or more.</p>
        : q.isPending ? <Loading h={160} /> : q.isError ? <Failed error={q.error} /> : b && (
        <div style={{ opacity: q.isPlaceholderData ? 0.6 : 1 }}>
          <div style={{ overflowX: "auto" }} tabIndex={0} role="region" aria-label="Flag size trade-off, scrollable">
            <table className="tbl">
              <thead><tr><th>Flag the riskiest</th><th className="num">Calls a year</th><th className="num">First overdrafts caught a year</th>
                <th className="num">Share of all first overdrafts</th><th className="num">Customers called per catch</th></tr></thead>
              <tbody>{b.rows.map((r) => (
                <tr key={r.flag_share} className={r.flag_share === b.chosen.flag_share ? "row cur" : "row"}>
                  <td><b>{pct(r.flag_share)}</b></td><td className="num">{Math.round(r.calls_per_year).toLocaleString("en-CA")}</td>
                  <td className="num">{Math.round(r.catches_per_year).toLocaleString("en-CA")}</td><td className="num">{pct(r.catch_share)}</td>
                  <td className="num">{r.calls_per_catch.toFixed(1)}</td></tr>))}</tbody>
            </table>
          </div>

          <div className="list" style={{ marginTop: 10 }}>
            {b.break_even_value_per_prevented != null && b.cost != null ? (
              <p style={{ margin: "6px 0" }}>Calls cost about <b>{money(b.cost)}</b> a year. If a call prevents {prevent}% of the overdrafts it catches, a prevented overdraft must be worth at least <b>{money(b.break_even_value_per_prevented)}</b> to break even.
                {b.net != null && <> At {money(v)} each, the value is <b>{money(b.value)}</b>: <b>{b.net >= 0 ? "net " : "a net loss of "}{money(Math.abs(b.net))}</b> a year.</>}</p>
            ) : <p className="sub" style={{ margin: "6px 0" }}>Enter what a call costs to see the break-even.</p>}
            <p style={{ margin: "6px 0" }}><b>Pilot.</b> To show that calls cut first overdrafts by {drop}% (80% power, 5% significance) you need
              {" "}<b>{b.pilot.per_arm.toLocaleString("en-CA")}</b> flagged customers in each group, <b>{b.pilot.total.toLocaleString("en-CA")}</b> in all: a random half get the call, the other half business as usual.
              {b.pilot.years_of_flags != null && <> At your size that is {b.pilot.years_of_flags < 1 ? "under a year" : `about ${b.pilot.years_of_flags.toFixed(1)} years`} of flags, plus a 12-month follow-up.</>}</p>
          </div>
        </div>
      )}
    </div>
  );
}
