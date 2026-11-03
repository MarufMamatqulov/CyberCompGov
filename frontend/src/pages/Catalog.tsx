import { useEffect, useMemo, useState } from "react";
import { Brain, Search, Siren, Wrench } from "lucide-react";
import { api } from "../api";
import { Card, ErrorBox, PageHeader, Spinner, fmt } from "../components/ui";

interface Indicator { code: string; desc: string }
interface Sub {
  sub_code: string; sub_name: string; k: Indicator; s: Indicator; a: Indicator;
  nist: string; ecsf: string; law: string; course: { title: string; hours: number };
}
interface BlockRow {
  code: string; name: string; ahp_weight: number; alpha_k: number; beta_s: number; gamma_a: number;
  min_threshold: number | null; subs: Sub[];
}

export default function Catalog() {
  const [data, setData] = useState<BlockRow[] | null>(null);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [block, setBlock] = useState("");

  useEffect(() => {
    api<BlockRow[]>("/api/catalog").then(setData).catch((e) => setError(e.message));
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    const n = q.trim().toLowerCase();
    return data.filter((b) => !block || b.code === block).map((b) => ({
      ...b,
      subs: b.subs.filter((s) => !n || JSON.stringify(s).toLowerCase().includes(n)),
    })).filter((b) => b.subs.length);
  }, [data, q, block]);

  if (error) return <ErrorBox message={error} />;
  if (!data) return <Spinner />;
  const total = filtered.reduce((acc, b) => acc + b.subs.length * 3, 0);

  return (
    <div className="space-y-6">
      <PageHeader title="36 ta KSA indikatorlari katalogi"
        subtitle="4 kompetensiya bloki → 12 sub-kompetensiya → 36 indikator (K — bilim, S — ko‘nikma, A — qobiliyat). NIST SP 800-181 (NICE), ENISA ECSF va milliy me’yorlar bilan moslashtirilgan." />
      <div className="flex flex-wrap gap-2">
        <div className="relative min-w-[240px] flex-1">
          <Search size={16} className="absolute left-3 top-2.5 text-slate-400" />
          <input className="input pl-9" placeholder="Indikator, standart yoki kalit so‘z bo‘yicha qidirish…" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
        <select className="input w-auto" value={block} onChange={(e) => setBlock(e.target.value)}>
          <option value="">Barcha bloklar</option>
          {data.map((b) => <option key={b.code} value={b.code}>{b.code} — {b.name}</option>)}
        </select>
        <span className="self-center text-sm text-slate-500">{total} indikator</span>
      </div>
      {filtered.map((b) => (
        <Card key={b.code}
          title={<span><span className="mr-2 rounded bg-navy px-2 py-0.5 text-white">{b.code}</span>{b.name}</span>}
          subtitle={`AHP vazni w = ${fmt(b.ahp_weight, 2)} · α = ${b.alpha_k}, β = ${b.beta_s}, γ = ${b.gamma_a}${b.min_threshold ? ` · kritik blok: C min = ${b.min_threshold}` : ""}`}>
          <div className="space-y-4">
            {b.subs.map((s) => (
              <div key={s.sub_code} className="rounded-lg border border-slate-200">
                <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-2">
                  <span className="font-mono text-sm font-semibold text-slate2">{s.sub_code}</span>
                  <span className="font-medium text-navy">{s.sub_name}</span>
                </div>
                <div className="grid gap-px bg-slate-100 md:grid-cols-3">
                  {([["k", "Bilim", Brain], ["s", "Ko‘nikma", Wrench], ["a", "Vaziyatli qobiliyat", Siren]] as const).map(([key, label, Icon]) => (
                    <div key={key} className="bg-white p-3 text-sm">
                      <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase text-slate-500">
                        <Icon size={13} /> {s[key].code} · {label}
                      </div>
                      {s[key].desc}
                    </div>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2 px-4 py-2 text-[11px]">
                  <span className="rounded bg-blue-50 px-1.5 py-0.5 text-navy">NIST SP 800-181: {s.nist}</span>
                  <span className="rounded bg-violet-50 px-1.5 py-0.5 text-violet-800">ENISA ECSF: {s.ecsf}</span>
                  <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-emerald-800">Me’yor: {s.law}</span>
                  <span className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-700">O‘quv moduli: {s.course.title} ({s.course.hours} soat)</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}
