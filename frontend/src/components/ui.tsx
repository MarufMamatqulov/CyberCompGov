import type { ReactNode } from "react";
import { AlertTriangle, Award, CheckCircle2, ShieldAlert, TrendingUp } from "lucide-react";

export function Card({ title, subtitle, action, children, className = "" }: {
  title?: ReactNode;
  subtitle?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>
      {(title || action) && (
        <header className="flex flex-wrap items-start justify-between gap-2 border-b border-slate-100 px-5 py-3">
          <div>
            {title && <h2 className="text-[15px] font-semibold text-navy">{title}</h2>}
            {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      <div className="p-5">{children}</div>
    </section>
  );
}

export function Stat({ label, value, hint, icon }: { label: string; value: ReactNode; hint?: ReactNode; icon?: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
        {icon && <span className="text-slate2">{icon}</span>}
      </div>
      <div className="mt-2 text-2xl font-bold text-navy tabular-nums">{value}</div>
      {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
    </div>
  );
}

const LEVEL_STYLE: Record<number, { cls: string; icon: ReactNode }> = {
  0: { cls: "bg-red-50 text-red-700 ring-red-200", icon: <ShieldAlert size={14} /> },
  1: { cls: "bg-orange-50 text-orange-700 ring-orange-200", icon: <AlertTriangle size={14} /> },
  2: { cls: "bg-amber-50 text-amber-800 ring-amber-200", icon: <TrendingUp size={14} /> },
  3: { cls: "bg-emerald-50 text-emerald-700 ring-emerald-200", icon: <CheckCircle2 size={14} /> },
  4: { cls: "bg-blue-50 text-navy ring-blue-200", icon: <Award size={14} /> },
};

export function levelIndex(level: string): number {
  if (level.startsWith("Kritik")) return 0;
  if (level.startsWith("Shartli")) return 1;
  if (level.startsWith("Bazaviy")) return 2;
  if (level.startsWith("Malakali")) return 3;
  return 4;
}

export function LevelBadge({ level, size = "sm" }: { level: string; size?: "sm" | "lg" }) {
  const st = LEVEL_STYLE[levelIndex(level)];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ring-1 ring-inset ${st.cls} ${
      size === "lg" ? "px-3 py-1.5 text-sm" : "px-2 py-0.5 text-xs"}`}>
      {st.icon}
      {level}
    </span>
  );
}

export function PhiBadge({ phi }: { phi: number }) {
  return phi === 1 ? (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200">
      <CheckCircle2 size={13} /> Φ = 1
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-200">
      <ShieldAlert size={13} /> Φ = 0
    </span>
  );
}

export function Spinner({ label = "Yuklanmoqda…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 p-8 text-sm text-slate-500">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-navy border-t-transparent" />
      {label}
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      <AlertTriangle size={16} className="mt-0.5 shrink-0" /> {message}
    </div>
  );
}

export function fmt(n: number | null | undefined, d = 1): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toFixed(d);
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: ReactNode; action?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-xl font-bold text-navy md:text-2xl">{title}</h1>
        {subtitle && <p className="mt-1 max-w-3xl text-sm text-slate-500">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
