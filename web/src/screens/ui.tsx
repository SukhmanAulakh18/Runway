import { useEffect, useRef, useState, type ReactNode } from "react";

export function Loading({ h = 160 }: { h?: number }) {
  return <div className="skeleton" style={{ minHeight: h }} aria-label="Loading" />;
}

export function Failed({ error }: { error: unknown }) {
  return <div className="err">{error instanceof Error ? error.message : "Something went wrong."}</div>;
}

/** Plain-language definitions shown on hover / keyboard focus, for a non-expert audience. */
export const GLOSSARY = {
  standard: "The judges' formula: savings divided by how much more goes out than comes in each month, using all-history medians.",
  realistic: "Our version: last 12 months, EI capped at $729/week and stopping after 6 months, pensions keep coming, and money that only looks saved (the in-month dip) doesn't count.",
  trough: "Lowest balance divided by average balance over 6 months. Near 0% means the account keeps dipping close to $0, even if the average looks healthy. In a banker's words: 1 minus the trough is the haircut on the average balance at the low point.",
  risk: "A real probability: tested on 2025 data the model never saw, it predicted 1.6% would go overdrawn and 1.6% did.",
  futures: "We replay random 3-month chunks of the customer's own history 2,000 times. This counts how many futures stay safe; it's a scenario, not a forecast.",
  cushion: "Overdraft protection or an automatic transfer sized to the customer's usual in-month dip. In 2025 it would have fully covered 27 of 34 caught first overdrafts.",
} as const;

export function Info({ tip }: { tip: string }) {
  return <span className="info" tabIndex={0} role="note" aria-label={tip} data-tip={tip}>?</span>;
}

export function Kpi({ label, value, note, size, swatch, tip }: { label: ReactNode; value: ReactNode; note?: ReactNode; size?: "md"; swatch?: "ours" | "std"; tip?: string }) {
  return (
    <div className="kpi">
      <span className="label">{swatch && <span className={`swatch ${swatch}`} />}{label}{tip && <Info tip={tip} />}</span>
      <span className={`value ${size ?? ""}`}>{value}</span>
      {note && <small>{note}</small>}
    </div>
  );
}


/** Counts the number inside a label (e.g. "62%", "14.6×", "$78K") up from 0 once. Text only; no maths on money.
 *  Skipped for people who prefer reduced motion, and for labels without a number. */
export function CountUp({ text, ms = 900 }: { text: string; ms?: number }) {
  const m = text.match(/-?\d[\d,]*(\.\d+)?/);
  const [shown, setShown] = useState(text);
  const done = useRef(false);
  useEffect(() => {
    if (!m || done.current || window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) { setShown(text); return; }
    done.current = true;
    const target = parseFloat(m[0].replace(/,/g, "")), dec = m[1] ? m[1].length - 1 : 0, t0 = performance.now();
    let raf = 0;
    const tick = (t: number) => {
      const k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3);   // ease-out
      const v = (target * e).toLocaleString("en-CA", { minimumFractionDigits: dec, maximumFractionDigits: dec });
      setShown(text.replace(m[0], v));
      if (k < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [text]); // eslint-disable-line react-hooks/exhaustive-deps
  return <span aria-label={text}>{shown}</span>;
}
