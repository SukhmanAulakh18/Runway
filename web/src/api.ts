// API client + types. React never calculates money: every number below comes from api.py (engine.py).
export type Asof = "2024-12" | "2023-12" | null;

export interface Scenario {
  job_loss: boolean; ei_rate: number; ei_months: number; ei_cap: boolean; income_cut: number;
  bills_increase_pct: number; spending_increase: number; one_off_cost: number;
  one_off_months_of_spending: number; return_to_work_month: number | null; employment_share: number;
}
export const NO_SHOCK: Scenario = {
  job_loss: false, ei_rate: 0.55, ei_months: 6, ei_cap: true, income_cut: 0, bills_increase_pct: 0,
  spending_increase: 0, one_off_cost: 0, one_off_months_of_spending: 0, return_to_work_month: null, employment_share: 1,
};
export interface RunwayRes { runway: number; label: string; income_after: number; spending_after: number; one_off: number;
  buffer_left?: number; usable_buffer?: number; monthly_gap: number; ei_monthly?: number; ei_capped?: boolean }
export interface Trough { ltr: number; min_balance: number; avg_balance: number; pct_rank: number | null; bottom_10: boolean;
  neg_days_recent: number; scorable: boolean; n_months: number }
export interface Cushion { buffer: number; alert_level: number; top_up_now: number; last_balance: number; as_of: string;
  dip_day: number | null; dip_day_share: number | null; dip_day_reliable: boolean }
export interface Month { month: string; money_in: number; money_out: number; avg_daily_balance: number; min_balance: number;
  month_end_balance: number; days_below_zero: number }
export interface Customer {
  account_id: number; asof: string | null; owner_age: number | null; flags: string[];
  profile: { income: number; spending: number; buffer: number; household_bills: number; fixed_costs: number; loan_payment: number; months_of_data: number };
  standard_runway: RunwayRes; realistic: { income: number; spending: number; dip: number; window_months: number; protected_income: number };
  realistic_runway: RunwayRes; trough: Trough | null; risk: { p_12m: number; validated_population: boolean };
  cushion: Cushion; last_activity: string; history: Month[];
  committed: { total: number; orders: number; by_purpose: Record<string, number> } | null;  // standing orders, today only
  loan: { amount: number; monthly_payment: number; status_meaning: string; defaulted: boolean; overdrawn_before_loan: boolean; loan_start: string } | null;
  what_happened_next?: { month: string; days_below_zero: number; min_balance: number }[];
}
export interface Sim { months: number[]; p10: number[]; p50: number[]; p90: number[]; dip: number; start: number;
  p_survive_6: number; p_survive_12: number; insufficient_history: boolean; n_paths: number; history_months: number }
export interface ShockRes { scenario: Scenario; standard: RunwayRes; realistic: RunwayRes; why_different: string[]; simulation: Sim;
  judge_check: { I: number; S: number; B: number; H: number } }
export interface PlanRes {
  cushion: Cushion;
  goal: { have: number; milestones: { name: string; target: number; need: number; done: boolean; months_steady: number | null; months_stretch: number | null }[];
    stretch_saving: number };
  backup: { base_runway: number; levers: { action: string; how: string; monthly_saving: number; runway: number; gain: number | null }[] };
  optimiser: { base_months: number; protected_months: number; horizon: number; cuts: number[]; avg_monthly_cut: number;
    max_monthly_cut: number; path: number[]; protected_path: number[]; dip: number; outcome: string; share_of_futures_protected?: number | null };
  facts: Record<string, unknown>;
}
export interface WatchRow { account_id: number; ltr: number; ltr_pct_rank: number | null; min_balance: number; avg_balance: number;
  realistic_runway_ei: number; answer_key_runway_ei: number; reasons: string; overdraft_next_12m?: boolean | null }
export interface Watch { asof: string | null; n_in_view: number; rows: WatchRow[]; reveal?: { top_hit: number; base_rate: number } }
export interface Twist { settings: Scenario; source: string; disagree: string[]; chips: string[] }
// evidence.json is large; screens read the fields they need.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Evidence = any;

async function call<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(path, body === undefined ? undefined
    : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) {
    const e = await r.json().catch(() => ({}));
    throw new Error(typeof e.detail === "string" ? e.detail : `Request failed (${r.status})`);
  }
  return r.json();
}
const q = (asof: Asof) => (asof ? `?asof=${asof}` : "");
export const api = {
  health: () => call<{ ai: string; accounts: number }>("/api/health"),
  accounts: () => call<number[]>("/api/accounts"),
  customer: (a: number, asof: Asof) => call<Customer>(`/api/customer/${a}${q(asof)}`),
  shock: (a: number, asof: Asof, scenario: Scenario) => call<ShockRes>(`/api/shock/${a}`, { scenario, asof }),
  plan: (a: number, asof: Asof, scenario: Scenario) => call<PlanRes>(`/api/plan/${a}`, { scenario, asof }),
  writePlan: (facts: Record<string, unknown>) => call<{ text: string; source: string }>("/api/write-plan", facts),
  twist: (text: string) => call<Twist>("/api/twist", { text }),
  brief: (a: number, asof: Asof) => call<{ text: string; source: string }>(`/api/ai/brief/${a}${q(asof)}`, {}),
  message: (a: number, asof: Asof, lang: "en" | "fr") =>
    call<{ text: string; source: string }>(`/api/ai/message/${a}${asof ? `?asof=${asof}&lang=${lang}` : `?lang=${lang}`}`, {}),
  watchlist: (asof: Asof) => call<Watch>(`/api/watchlist${q(asof)}`),
  portfolio: (scenario: Scenario) => call<{ month: number; standard: number; realistic: number }[]>("/api/portfolio", { scenario }),
  evidence: () => call<Evidence>("/api/evidence"),
};

// ---- formatting only (no arithmetic on money beyond display rounding) ----
export const money = (n: number | null | undefined) =>
  n == null ? "–" : `${n < 0 ? "−" : ""}$${Math.abs(Math.round(n)).toLocaleString("en-CA")}`;
export const kmoney = (n: number) => (Math.abs(n) >= 1e6 ? `$${(n / 1e6).toFixed(1)}M` : Math.abs(n) >= 1e3 ? `$${Math.round(n / 1e3)}K` : money(n));
export const pct = (n: number | null | undefined, d = 0) => (n == null ? "–" : `${(n * 100).toFixed(d)}%`);
export const monthName = (ym: string) => new Date(`${ym}-15`).toLocaleDateString("en-CA", { month: "short", year: "numeric" });
export const ASOF_LABEL: Record<string, string> = { "": "Today (Dec 2025)", "2024-12": "Dec 2024", "2023-12": "Dec 2023" };
