import {
  Area, Bar, CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { kmoney, money, monthName, pct, type Month, type Sim } from "./api";

const C = { ours: "#f26a1b", oursSoft: "#ffc9a3", std: "#64748b", bad: "#dc2626", ink: "#24170f", ink3: "#6a5a4e", line: "#e6e8ee" };
const axis = { stroke: C.ink3, fontSize: 11.5, tickLine: false, axisLine: false } as const;
const grid = <CartesianGrid stroke={C.line} vertical={false} />;

type Row = Record<string, unknown>;
function Tip({ active, payload, label, rows }: {
  active?: boolean; payload?: { payload: Row }[]; label?: string | number;
  rows: (r: Row) => [string, string][];
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="tip">
      <b>{label}</b>
      {rows(payload[0].payload).map(([k, v]) => <div key={k}><span>{k}</span><span>{v}</span></div>)}
    </div>
  );
}

/** Average vs lowest balance each month; the shaded gap is the in-month dip. */
export function BalanceChart({ history, height = 280 }: { history: Month[]; height?: number }) {
  const data = history.map((h) => ({ m: monthName(h.month), avg: h.avg_daily_balance, low: h.min_balance,
    dip: [h.min_balance, h.avg_daily_balance], neg: h.days_below_zero > 0 ? h.min_balance : null, days: h.days_below_zero }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 8, right: 8, left: 4, bottom: 0 }}>
        {grid}
        <XAxis dataKey="m" {...axis} minTickGap={40} />
        <YAxis {...axis} tickFormatter={kmoney} width={56} />
        <ReferenceLine y={0} stroke={C.bad} strokeWidth={1.5} label={{ value: "$0", position: "insideBottomRight", fill: C.bad, fontSize: 11 }} />
        <Area dataKey="dip" stroke="none" fill={C.oursSoft} fillOpacity={0.55} isAnimationActive={false} name="In-month dip" />
        <Line dataKey="avg" stroke={C.ink} strokeWidth={2} dot={false} name="Average balance" />
        <Line dataKey="low" stroke={C.ours} strokeWidth={2} dot={false} name="Lowest balance" />
        <Line dataKey="neg" stroke="none" dot={{ r: 4, fill: C.bad, stroke: "#fff", strokeWidth: 2 }} isAnimationActive={false} legendType="none" />
        <Tooltip content={<Tip rows={(r) => [["Average", money(r.avg as number)], ["Lowest", money(r.low as number)],
          ...((r.days as number) > 0 ? [["Days below $0", String(r.days)] as [string, string]] : [])]} />} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/** Monte Carlo fan: 10th-90th percentile band, median, the overdraft line (typical dip) and where EI ends. */
export function FanChart({ sim, eiEnds, height = 300 }: { sim: Sim; eiEnds: number | null; height?: number }) {
  const data = sim.months.map((m, i) => ({ m, band: [sim.p10[i], sim.p90[i]], p10: sim.p10[i], p50: sim.p50[i], p90: sim.p90[i] }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 10, right: 12, left: 4, bottom: 0 }}>
        {grid}
        <XAxis dataKey="m" {...axis} tickFormatter={(m) => `M${m}`} interval={2} />
        <YAxis {...axis} tickFormatter={kmoney} width={56} />
        <Area dataKey="band" stroke="none" fill={C.ours} fillOpacity={0.16} name="Middle 80% of futures" />
        <Line dataKey="p50" stroke={C.ours} strokeWidth={2.5} dot={false} name="Typical future" />
        <Line dataKey="p10" stroke={C.ours} strokeWidth={1} strokeDasharray="2 3" dot={false} name="Bad future (10th pct)" />
        <ReferenceLine y={sim.dip} stroke={C.bad} strokeDasharray="5 4"
          label={{ value: "Overdraft line (typical dip)", position: "insideBottomLeft", fill: C.bad, fontSize: 11 }} />
        {eiEnds != null && <ReferenceLine x={eiEnds} stroke={C.ink3} strokeDasharray="3 3"
          label={{ value: "EI ends", position: "insideTopRight", fill: C.ink3, fontSize: 11 }} />}
        <Tooltip content={<Tip rows={(r) => [["Good (90th)", money(r.p90 as number)], ["Typical", money(r.p50 as number)], ["Bad (10th)", money(r.p10 as number)]]} />}
          labelFormatter={(m) => `Month ${m}`} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/** Optimiser: projected bad-case balance without vs with the cut schedule; bars = monthly cut. */
export function OptimiserChart({ path, protectedPath, cuts, dip, height = 260 }:
  { path: number[]; protectedPath: number[]; cuts: number[]; dip: number; height?: number }) {
  const data = path.map((p, i) => ({ m: i + 1, without: p, with: protectedPath[i] ?? null, cut: cuts[i] ?? null }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 10, right: 12, left: 4, bottom: 0 }}>
        {grid}
        <XAxis dataKey="m" {...axis} tickFormatter={(m) => `M${m}`} />
        <YAxis {...axis} tickFormatter={kmoney} width={56} />
        <Bar dataKey="cut" fill={C.oursSoft} radius={[4, 4, 0, 0]} barSize={14} name="Monthly cut" />
        <Line dataKey="without" stroke={C.std} strokeDasharray="6 4" strokeWidth={2} dot={false} name="Without changes" />
        <Line dataKey="with" stroke={C.ours} strokeWidth={2.5} dot={false} name="With the cuts" />
        <ReferenceLine y={dip} stroke={C.bad} strokeDasharray="5 4" label={{ value: "Overdraft line", position: "insideBottomLeft", fill: C.bad, fontSize: 11 }} />
        <Tooltip content={<Tip rows={(r) => [["Without changes", money(r.without as number)], ["With cuts", money(r.with as number)], ["Cut this month", money(r.cut as number)]]} />}
          labelFormatter={(m) => `Month ${m}`} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/** Bank view: share of all customers still above zero, standard (dashed) vs realistic. */
export function PortfolioChart({ data, height = 240 }: { data: { month: number; standard: number; realistic: number }[]; height?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 10, right: 12, left: 4, bottom: 0 }}>
        {grid}
        <XAxis dataKey="month" {...axis} tickFormatter={(m) => `M${m}`} interval={3} />
        <YAxis {...axis} tickFormatter={(v) => pct(v)} domain={[0, 1]} width={44} />
        <Line dataKey="standard" stroke={C.std} strokeDasharray="6 4" strokeWidth={2} dot={false} name="Standard formula" />
        <Line dataKey="realistic" stroke={C.ours} strokeWidth={2.5} dot={false} name="Realistic" />
        <Tooltip content={<Tip rows={(r) => [["Standard formula", pct(r.standard as number)], ["Realistic", pct(r.realistic as number)]]} />}
          labelFormatter={(m) => `Month ${m}`} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/** Generic paired bars per category (e.g. riskiest 10% vs everyone else, predicted vs observed). */
export function PairBars({ data, a, b, height = 230, fmt = (v: number) => pct(v, 1) }: {
  data: Row[]; a: { key: string; name: string; color?: string }; b: { key: string; name: string; color?: string };
  height?: number; fmt?: (v: number) => string;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 10, right: 8, left: 4, bottom: 0 }} barGap={2}>
        {grid}
        <XAxis dataKey="x" {...axis} />
        <YAxis {...axis} tickFormatter={fmt} width={62} />
        <Bar dataKey={a.key} name={a.name} fill={a.color ?? C.ours} radius={[4, 4, 0, 0]} barSize={26} />
        <Bar dataKey={b.key} name={b.name} fill={b.color ?? "#cbd2dd"} radius={[4, 4, 0, 0]} barSize={26} />
        <Tooltip cursor={{ fill: "#f1f3f7" }} content={<Tip rows={(r) => [[a.name, fmt(r[a.key] as number)], [b.name, fmt(r[b.key] as number)]]} />} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function Legend({ items }: { items: { label: string; kind: "ours" | "std" | "ink" | "bad" | "soft" | "grey" }[] }) {
  const style = (k: string) => ({
    ours: { background: C.ours }, ink: { background: C.ink }, bad: { background: C.bad }, soft: { background: C.oursSoft },
    std: { background: `repeating-linear-gradient(90deg, ${C.std} 0 4px, transparent 4px 6px)` },
    grey: { background: `repeating-linear-gradient(90deg, ${C.ink3} 0 4px, transparent 4px 6px)` },
  } as Record<string, React.CSSProperties>)[k];
  return (
    <div className="chips" style={{ gap: 14 }}>
      {items.map((i) => (
        <span key={i.label} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12.5, color: "#475569" }}>
          <span style={{ width: 16, height: 3, borderRadius: 2, ...style(i.kind) }} />{i.label}
        </span>
      ))}
    </div>
  );
}


/** Kaplan-Meier: share of customers who have had a first overdraft, by month since scoring, per trough group. */
export function SurvivalChart({ curves, height = 260 }: { curves: Record<string, { overdrawn_by_month: number[] }>; height?: number }) {
  const names = Object.keys(curves);
  const colors = [C.ours, C.ink, C.ink3];   // matches Legend kinds ours / ink / grey
  const data = curves[names[0]].overdrawn_by_month.map((_, k) => Object.fromEntries([["m", k], ...names.map((n) => [n, curves[n].overdrawn_by_month[k]])]));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 10, right: 12, left: 4, bottom: 0 }}>
        {grid}
        <XAxis dataKey="m" {...axis} tickFormatter={(m) => `M${m}`} interval={2} />
        <YAxis {...axis} tickFormatter={(v) => pct(v)} width={44} />
        <ReferenceLine x={6} stroke={C.ink3} strokeDasharray="3 3" label={{ value: "6 months", position: "insideTopLeft", fill: C.ink3, fontSize: 11 }} />
        {names.map((n, i) => <Line key={n} dataKey={n} type="stepAfter" stroke={colors[i]} strokeWidth={i === 0 ? 2.5 : 2}
          strokeDasharray={i === 2 ? "5 4" : undefined} dot={false} name={n} />)}
        <Tooltip content={<Tip rows={(r) => names.map((n) => [n, pct(r[n] as number, 1)] as [string, string])} />} labelFormatter={(m) => `Month ${m}`} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}


/** The low point as a tank: the tank is the customer's average balance, the fill is their lowest balance (engine's lowest ÷ average).
 *  A meter in the dataviz sense: fill carries the state, the track is a lighter step of the same hue. Numbers are in the label and
 *  the text beside it; the level is drawn at least a hairline so a near-empty tank still reads. */
export function LowPointMeter({ ratio, avg, low }: { ratio: number; avg: string; low: string }) {
  const r = Math.min(Math.max(ratio, 0), 1), level = Math.max(r, 0.05);
  const label = `Average balance ${avg}; lowest balance ${low}, ${pct(r)} of the average`;
  return (
    <svg className="lowpoint" viewBox="0 0 28 56" width="36" height="72" role="img" aria-label={label} style={{ ["--lvl" as string]: level }}>
      <title>{label}</title>
      <defs><clipPath id="lp-clip"><rect x="2" y="2" width="24" height="52" rx="6" /></clipPath></defs>
      <g clipPath="url(#lp-clip)">
        <rect x="2" y="2" width="24" height="52" fill="var(--ours-soft)" />
        <rect className="lp-fill" x="2" y="2" width="24" height="52" fill="var(--ours-fill)" />
      </g>
      <rect x="2" y="2" width="24" height="52" rx="6" fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}


/** Months their savings last, as bars on one 0-12+ axis with a dashed "safe cushion" line. The labels come from the engine
 *  ("no shortfall (120+)"); the bar is clamped to the axis for display only. */
export function RunwayBars({ rows, cap = 12, line = 6 }: { rows: { label: string; months: number; text: string; kind: "std" | "ours" }[]; cap?: number; line?: number }) {
  const at = (m: number) => `${Math.min(Math.max(m, 0) / cap, 1) * 100}%`;
  return (
    <div className="rbars" role="img" aria-label={`${rows.map((r) => `${r.label}: ${r.text}`).join("; ")}. The dashed line marks ${line} months.`}>
      {rows.map((r) => (
        <div key={r.label} className="rbar-row">
          <span className="rbar-label">{r.label}</span>
          <div className="rbar-track"><div className={`rbar-fill ${r.kind}`} style={{ width: at(r.months) }} /><span className="rbar-line" style={{ left: at(line) }} /></div>
          <b className="rbar-val">{r.text}</b>
        </div>))}
      <div className="rbar-axis"><span className="rbar-axis-label" style={{ left: at(line) }}>{line} months: a safe cushion</span></div>
    </div>
  );
}

/** 100 customers as 100 dots: the first `hit` are filled (overdrawn the next year), the rest hollow. */
export function Dots({ hit, total, cols = 10 }: { hit: number; total: number; cols?: number }) {
  const r = 5, pitch = 15, rows = Math.ceil(total / cols), w = cols * pitch - (pitch - 2 * r), h = rows * pitch - (pitch - 2 * r);
  return (
    <svg className="dots" viewBox={`0 0 ${w} ${h}`} width={w} height={h} role="img" aria-label={`${hit} of ${total} were overdrawn the next year`}>
      {Array.from({ length: total }, (_, i) => (
        <circle key={i} cx={(i % cols) * pitch + r} cy={Math.floor(i / cols) * pitch + r} r={r - 0.75} className={i < hit ? "dot-hit" : "dot-rest"} />))}
    </svg>
  );
}

/** First overdrafts by month for a customer's group: three bars on one scale, so "most of it comes early" is visible. */
export function WhenBars({ points }: { points: { label: string; v: number }[] }) {
  const top = Math.max(...points.map((p) => p.v), 0.0001);
  return (
    <div className="wbars" role="img" aria-label={points.map((p) => `${p.label}: ${pct(p.v, 1)}`).join("; ")}>
      {points.map((p) => (
        <div key={p.label} className="rbar-row">
          <span className="rbar-label">{p.label}</span>
          <div className="rbar-track"><div className="rbar-fill ours" style={{ width: `${(p.v / top) * 100}%` }} /></div>
          <b className="rbar-val">{pct(p.v, 1)}</b>
        </div>))}
    </div>
  );
}

/** A row's last 12 months in 96x28 pixels: the average balance as a light band, the lowest balance as a line, a hairline at $0.
 *  Points are [lowest, average] per month, oldest first. Decorative: the row's text carries the numbers. */
export function Spark({ points }: { points: [number, number][] }) {
  const w = 96, h = 28, pad = 2;
  const hi = Math.max(...points.map((p) => p[1]), 1), lo = Math.min(0, ...points.map((p) => p[0]));
  const x = (i: number) => pad + (i / Math.max(points.length - 1, 1)) * (w - 2 * pad);
  const y = (v: number) => h - pad - ((v - lo) / (hi - lo || 1)) * (h - 2 * pad);
  const avg = points.map((p, i) => `${x(i)},${y(p[1])}`), low = points.map((p, i) => `${x(i)},${y(p[0])}`);
  return (
    <svg className="spark" viewBox={`0 0 ${w} ${h}`} width={w} height={h} aria-hidden="true">
      <polygon points={[...avg, ...[...low].reverse()].join(" ")} className="spark-gap" />
      <line x1={pad} x2={w - pad} y1={y(0)} y2={y(0)} className="spark-zero" />
      <polyline points={low.join(" ")} className="spark-low" fill="none" />
    </svg>
  );
}
