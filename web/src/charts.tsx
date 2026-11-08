import {
  Area, Bar, CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { kmoney, money, monthName, pct, type Month, type Sim } from "./api";

const C = { ours: "#f26a1b", oursSoft: "#ffc9a3", std: "#64748b", bad: "#dc2626", ink: "#0f172a", ink3: "#8a94a6", line: "#e6e8ee" };
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
        <YAxis {...axis} tickFormatter={fmt} width={48} />
        <Bar dataKey={a.key} name={a.name} fill={a.color ?? C.ours} radius={[4, 4, 0, 0]} barSize={26} />
        <Bar dataKey={b.key} name={b.name} fill={b.color ?? "#cbd2dd"} radius={[4, 4, 0, 0]} barSize={26} />
        <Tooltip cursor={{ fill: "#f1f3f7" }} content={<Tip rows={(r) => [[a.name, fmt(r[a.key] as number)], [b.name, fmt(r[b.key] as number)]]} />} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function Legend({ items }: { items: { label: string; kind: "ours" | "std" | "ink" | "bad" | "soft" }[] }) {
  const style = (k: string) => ({
    ours: { background: C.ours }, ink: { background: C.ink }, bad: { background: C.bad }, soft: { background: C.oursSoft },
    std: { background: `repeating-linear-gradient(90deg, ${C.std} 0 4px, transparent 4px 6px)` },
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
