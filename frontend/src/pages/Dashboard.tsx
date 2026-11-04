import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Award, Clock, Search, TrendingUp, Users } from "lucide-react";
import { api } from "../api";
import { Card, ErrorBox, LevelBadge, PageHeader, PhiBadge, Spinner, Stat, fmt } from "../components/ui";
import { GROUP_LABELS, LEVELS, type Experiment, type RegistryRow } from "../types";

export const SERIES = { before: "#D9822B", after: "#3A6FB0" };
const AXIS = { fontSize: 12, fill: "#64748b" };

function pText(p: number) {
  return p < 0.001 ? "p < 0.001" : `p = ${p.toFixed(3)}`;
}

export default function Dashboard() {
  const [exp, setExp] = useState<Experiment | null>(null);
  const [rows, setRows] = useState<RegistryRow[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api<Experiment>("/api/analytics/experiment"), api<RegistryRow[]>("/api/officers")])
      .then(([e, r]) => { setExp(e); setRows(r); })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!exp || !rows) return <Spinner />;
  const k = exp.kpi;

  const barData = exp.table.map((r) => ({
    name: r.indicator === "I_AXK" ? "I AXK" : r.indicator,
    before: Number(r.before_mean.toFixed(1)),
    after: Number(r.after_mean.toFixed(1)),
  }));
  const levelData = exp.levels.map((l) => ({
    name: l.level.split(" (")[0],
    full: l.level,
    before: Number(l.before_pct.toFixed(1)),
    after: Number(l.after_pct.toFixed(1)),
    nb: l.before,
    na: l.after,
  }));

  return (
    <div className="space-y-6">
      <PageHeader title="Rahbariyat va analitika paneli"
        subtitle="Davlat organlari va tashkilotlari AKT mas’ul xodimlari axborot xavfsizligi kompetensiyalari monitoringi va dinamikasi" />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Jami baholangan xodimlar" value={`n = ${k.n}`} icon={<Users size={18} />}
          hint={`15 vazirlik · 15 viloyat · 15 tuman · ${k.total_sessions} ta sessiya`} />
        <Stat label="Integral indeks o‘sishi" icon={<TrendingUp size={18} />}
          value={<span>{fmt(k.i_before)} → {fmt(k.i_after)}</span>}
          hint={`+${fmt(k.i_delta)} ball · +${fmt(k.i_delta_pct)}%`} />
        <Stat label="Malakali va Ekspert ulushi" icon={<Award size={18} />}
          value={<span>{fmt(k.qualified_before_pct)}% → {fmt(k.qualified_after_pct)}%</span>}
          hint={`Φ = 0 holatlar: ${k.phi_fail_before} → ${k.phi_fail_after}`} />
        <Stat label="O‘rtacha attestatsiya vaqti" icon={<Clock size={18} />}
          value={`${fmt(k.avg_minutes, 0)} daqiqa`}
          hint={`An’anaviy ${k.traditional_minutes} daqiqaga nisbatan ${fmt(k.speedup)}x tejamkorlik`} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Manzilli o‘qitishdan oldingi va keyingi ko‘rsatkichlar"
          subtitle="Eksperimental guruh (n = 45), o‘rtacha ball (C₁…C₄ va I AXK)">
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={barData} barGap={2} barCategoryGap="22%">
                <CartesianGrid vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={AXIS} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={AXIS} axisLine={false} tickLine={false} width={32} />
                <Tooltip cursor={{ fill: "rgba(148,163,184,0.12)" }} formatter={(v) => fmt(Number(v))} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="before" name="O‘qitishdan oldin" fill={SERIES.before} radius={[4, 4, 0, 0]} />
                <Bar dataKey="after" name="O‘qitishdan keyin" fill={SERIES.after} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="Kvalimetrik malaka darajalari taqsimoti o‘zgarishi (%)"
          subtitle="Xodimlar ulushi har bir daraja bo‘yicha">
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={levelData} barGap={2} barCategoryGap="22%">
                <CartesianGrid vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={AXIS} axisLine={false} tickLine={false} interval={0} />
                <YAxis tick={AXIS} axisLine={false} tickLine={false} width={32} unit="%" />
                <Tooltip cursor={{ fill: "rgba(148,163,184,0.12)" }}
                  labelFormatter={(_, p) => (p?.[0]?.payload as { full?: string } | undefined)?.full ?? ""}
                  formatter={(v, name, item) => {
                    const pl = item.payload as { nb: number; na: number };
                    const cnt = item.dataKey === "before" ? pl.nb : pl.na;
                    return [`${fmt(Number(v))}% (${cnt} nafar)`, name];
                  }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="before" name="O‘qitishdan oldin" fill={SERIES.before} radius={[4, 4, 0, 0]} />
                <Bar dataKey="after" name="O‘qitishdan keyin" fill={SERIES.after} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card title="Statistik verifikatsiya va tahlil: juftlangan Student t-testi"
        subtitle={`df = ${exp.n - 1}; H₀: o‘qitishdan oldingi va keyingi o‘rtachalar teng (p < 0.001 da statistik ahamiyatli)`}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-3 py-2">Ko‘rsatkich</th>
                <th className="px-3 py-2 text-right">Oldin (M ± SD)</th>
                <th className="px-3 py-2 text-right">Keyin (M ± SD)</th>
                <th className="px-3 py-2 text-right">Δ, ball</th>
                <th className="px-3 py-2 text-right">Δ, %</th>
                <th className="px-3 py-2 text-right">t</th>
                <th className="px-3 py-2 text-right">p</th>
              </tr>
            </thead>
            <tbody className="tabular-nums">
              {exp.table.map((r) => (
                <tr key={r.indicator} className={`border-t border-slate-100 ${r.indicator === "I_AXK" ? "bg-navy-50 font-semibold" : ""}`}>
                  <td className="px-3 py-2">{r.indicator === "I_AXK" ? "I AXK (integral)" : r.indicator}</td>
                  <td className="px-3 py-2 text-right">{fmt(r.before_mean)} ± {fmt(r.before_sd)}</td>
                  <td className="px-3 py-2 text-right">{fmt(r.after_mean)} ± {fmt(r.after_sd)}</td>
                  <td className="px-3 py-2 text-right">+{fmt(r.delta)}</td>
                  <td className="px-3 py-2 text-right">+{fmt(r.delta_pct)}%</td>
                  <td className="px-3 py-2 text-right">{fmt(r.t, 2)}</td>
                  <td className="px-3 py-2 text-right">{pText(r.p)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {exp.groups.map((g) => (
            <div key={g.group} className="rounded-lg border border-slate-200 p-3 text-sm">
              <div className="font-medium text-navy">{g.label} (n = {g.n})</div>
              <div className="mt-1 tabular-nums text-slate-600">I AXK: {fmt(g.before)} → <b>{fmt(g.after)}</b>
                <span className="ml-1 text-emerald-700">(+{fmt(g.after - g.before)})</span></div>
            </div>
          ))}
        </div>
      </Card>

      <Registry rows={rows} />
    </div>
  );
}

function Registry({ rows }: { rows: RegistryRow[] }) {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [group, setGroup] = useState("");
  const [level, setLevel] = useState("");
  const [stage, setStage] = useState<"before" | "after">("after");

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return rows.filter((r) => {
      const s = r[stage];
      if (group && r.group !== group) return false;
      if (level && s?.level !== level) return false;
      if (needle && !`${r.full_name} ${r.username} ${r.pinfl} ${r.position} ${r.agency.name}`.toLowerCase().includes(needle)) return false;
      return true;
    });
  }, [rows, q, group, level, stage]);

  return (
    <Card title="AKT mas’ul xodimlari reyestri" subtitle={`${filtered.length} / ${rows.length} xodim · qatorni bosib, diagnostika pasportini oching`}>
      <div className="mb-4 flex flex-wrap gap-2">
        <div className="relative min-w-[220px] flex-1">
          <Search size={16} className="absolute left-3 top-2.5 text-slate-400" />
          <input className="input pl-9" placeholder="F.I.Sh., PINFL, lavozim yoki tashkilot…" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
        <select className="input w-auto" value={group} onChange={(e) => setGroup(e.target.value)}>
          <option value="">Barcha guruhlar</option>
          {Object.entries(GROUP_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select className="input w-auto" value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="">Barcha darajalar</option>
          {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
        <div className="flex rounded-lg border border-slate-300 p-0.5 text-sm">
          {(["before", "after"] as const).map((s) => (
            <button key={s} onClick={() => setStage(s)}
              className={`rounded-md px-3 py-1.5 ${stage === s ? "bg-navy text-white" : "text-slate-600"}`}>
              {s === "before" ? "Oldin" : "Keyin"}
            </button>
          ))}
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2">#</th>
              <th className="px-3 py-2">Xodim</th>
              <th className="px-3 py-2">Tashkilot</th>
              <th className="px-3 py-2 text-right">C1</th>
              <th className="px-3 py-2 text-right">C2</th>
              <th className="px-3 py-2 text-right">C3</th>
              <th className="px-3 py-2 text-right">C4</th>
              <th className="px-3 py-2 text-right">I AXK</th>
              <th className="px-3 py-2">Φ</th>
              <th className="px-3 py-2">Daraja</th>
            </tr>
          </thead>
          <tbody className="tabular-nums">
            {filtered.map((r, i) => {
              const s = r[stage];
              return (
                <tr key={r.id} onClick={() => navigate(`/passport/${r.id}`)}
                  className="cursor-pointer border-t border-slate-100 hover:bg-navy-50/60">
                  <td className="px-3 py-2 text-slate-400">{i + 1}</td>
                  <td className="px-3 py-2">
                    <div className="font-medium text-navy">{r.full_name}
                      {["e1", "e2", "e3"].includes(r.username) && <span className="ml-1.5 rounded bg-slate-100 px-1.5 text-[10px] font-semibold text-slate-600">{r.username}</span>}
                    </div>
                    <div className="text-xs text-slate-500">{r.position}</div>
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-600">{r.agency.name}
                    {r.agency.category === "MII" && <span className="ml-1 rounded bg-amber-100 px-1 text-[10px] font-semibold text-amber-800">MII</span>}
                  </td>
                  {s ? (
                    <>
                      {(["C1", "C2", "C3", "C4"] as const).map((b) => (
                        <td key={b} className={`px-3 py-2 text-right ${(b === "C2" || b === "C3") && s.c[b] < 50 ? "font-semibold text-red-600" : ""}`}>{fmt(s.c[b], 0)}</td>
                      ))}
                      <td className="px-3 py-2 text-right font-semibold">{fmt(s.i_axk, 2)}</td>
                      <td className="px-3 py-2"><PhiBadge phi={s.phi} /></td>
                      <td className="px-3 py-2"><LevelBadge level={s.level} /></td>
                    </>
                  ) : <td colSpan={7} className="px-3 py-2 text-slate-400">Baholanmagan</td>}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
