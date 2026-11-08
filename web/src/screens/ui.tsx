import type { ReactNode } from "react";

export function Loading({ h = 160 }: { h?: number }) {
  return <div className="skeleton" style={{ minHeight: h }} aria-label="Loading" />;
}

export function Failed({ error }: { error: unknown }) {
  return <div className="err">{error instanceof Error ? error.message : "Something went wrong."}</div>;
}

export function Kpi({ label, value, note, size, swatch }: { label: ReactNode; value: ReactNode; note?: ReactNode; size?: "md"; swatch?: "ours" | "std" }) {
  return (
    <div className="kpi">
      <span className="label">{swatch && <span className={`swatch ${swatch}`} />}{label}</span>
      <span className={`value ${size ?? ""}`}>{value}</span>
      {note && <small>{note}</small>}
    </div>
  );
}
