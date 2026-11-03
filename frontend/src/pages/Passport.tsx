import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Legend, PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from "recharts";
import { QRCodeSVG } from "qrcode.react";
import { AlertOctagon, BookOpen, Building2, CheckCircle2, Download, GraduationCap, Printer } from "lucide-react";
import { api, downloadFile } from "../api";
import { Card, ErrorBox, LevelBadge, PageHeader, PhiBadge, Spinner, fmt } from "../components/ui";
import { BLOCKS, BLOCK_NAMES, type Passport } from "../types";
import { SERIES } from "./Dashboard";

export default function PassportPage() {
  const { officerId } = useParams();
  const [params, setParams] = useSearchParams();
  const sessionId = params.get("session");
  const [data, setData] = useState<Passport | null>(null);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    setData(null);
    setError("");
    const q = sessionId ? `?session_id=${sessionId}` : "";
    api<Passport>(`/api/officers/${officerId}/passport${q}`).then(setData).catch((e) => setError(e.message));
  }, [officerId, sessionId]);

  if (error) return <ErrorBox message={error} />;
  if (!data) return <Spinner />;
  const { officer, session: s, sessions, compare } = data;

  if (!s) {
    return (
      <div>
        <PageHeader title="Individual diagnostika pasporti" subtitle={officer.full_name} />
        <Card>
          <p className="text-sm text-slate-600">Ushbu xodim hali baholanmagan.</p>
          <Link to="/assessment" className="btn-primary mt-4">Kompleks baholashni boshlash</Link>
        </Card>
      </div>
    );
  }

  const verifyUrl = `${window.location.origin}/verify/${s.verify_code}`;
  const radar = BLOCKS.map((b) => ({
    block: b,
    current: s.c[b],
    compare: compare?.c[b],
    norm: s.norm,
    min: 50,
  }));

  const download = async () => {
    setDownloading(true);
    try {
      await downloadFile(`/api/reports/session/${s.id}/pdf`, `attestatsiya_pasporti_${officer.username}_${s.id}.pdf`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Individual diagnostika pasporti va Skill Gap Matrix"
        subtitle={`Hujjat № ${s.verify_code} · ${new Date(s.created_at).toLocaleDateString("uz-UZ")} · ${s.stage_label}`}
        action={
          <div className="no-print flex flex-wrap gap-2">
            <button className="btn-primary" onClick={download} disabled={downloading}>
              <Download size={16} /> {downloading ? "Tayyorlanmoqda…" : "Rasmiy attestatsiya pasporti va o‘quv reja (PDF)"}
            </button>
            <button className="btn-secondary" onClick={() => window.print()}><Printer size={16} /> Bosma</button>
          </div>
        }
      />

      {sessions.length > 1 && (
        <div className="no-print flex flex-wrap gap-2">
          {sessions.map((x) => (
            <button key={x.id} onClick={() => setParams({ session: String(x.id) })}
              className={`rounded-lg px-3 py-1.5 text-sm ${x.id === s.id ? "bg-navy text-white" : "bg-white text-slate-600 ring-1 ring-slate-200"}`}>
              {x.stage_label} · {fmt(x.i_axk, 2)}
            </button>
          ))}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="flex flex-wrap gap-6">
            <div className="min-w-[240px] flex-1 space-y-2 text-sm">
              <div className="text-lg font-semibold text-navy">{officer.full_name}</div>
              <div className="text-slate-600">{officer.position}</div>
              <div className="flex items-center gap-2 text-slate-600"><Building2 size={15} /> {officer.agency.name}</div>
              <div className="flex flex-wrap gap-2 pt-1 text-xs">
                <span className={`rounded-full px-2 py-0.5 font-semibold ${officer.agency.category === "MII" ? "bg-amber-100 text-amber-800" : "bg-slate-100 text-slate-700"}`}>
                  {officer.agency.category === "MII" ? "MII obyekti" : "Oddiy davlat organi"} · C norm = {fmt(s.norm, 0)}
                </span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-700">PINFL {officer.pinfl}</span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-700">Staj {officer.experience_years} yil</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs uppercase tracking-wide text-slate-500">Integral indeks I AXK</div>
              <div className="text-5xl font-bold tabular-nums text-navy">{fmt(s.i_axk, 2)}</div>
              {compare && (
                <div className="text-xs text-slate-500">
                  {compare.stage_label}: {fmt(compare.i_axk, 2)} ({s.i_axk - compare.i_axk >= 0 ? "+" : ""}{fmt(s.i_axk - compare.i_axk, 2)})
                </div>
              )}
              <div className="mt-2 flex justify-end gap-2"><PhiBadge phi={s.phi} /></div>
            </div>
          </div>
          <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-slate-100 pt-4">
            <LevelBadge level={s.level} size="lg" />
            <p className="text-sm text-slate-700">{s.decision}</p>
          </div>
          {s.phi === 0 ? (
            <div className="mt-4 flex gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
              <AlertOctagon className="shrink-0" />
              <div>
                <b>Kompensatsiyalanmaydigan chegara buzildi (Φ = 0).</b>{" "}
                {s.failed_blocks.map((b) => `${b} = ${fmt(s.c[b], 0)}`).join(", ")} &lt; C min = 50. Kritik texnik (C₂) yoki
                insident (C₃) bloki boshqa bloklardagi yuqori ball hisobiga qoplanmaydi — ushbu bloklar bo‘yicha 30 kun
                ichida majburiy maqsadli qayta tayyorlash va qayta imtihon belgilanadi.
              </div>
            </div>
          ) : (
            <div className="mt-4 flex gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
              <CheckCircle2 className="shrink-0" size={18} /> Kritik bloklar chegarasi bajarilgan: C₂ = {fmt(s.c.C2, 0)} ≥ 50, C₃ = {fmt(s.c.C3, 0)} ≥ 50.
            </div>
          )}
        </Card>

        <Card title="Kompetensiya profili" subtitle={`C norm = ${fmt(s.norm, 0)} va C min = 50 bilan taqqoslash`}>
          <div className="h-72">
            <ResponsiveContainer>
              <RadarChart data={radar} outerRadius="72%">
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="block" tick={{ fontSize: 12, fill: "#334155", fontWeight: 600 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#94a3b8" }} angle={90} tickCount={6} />
                <Radar name={`C norm = ${s.norm}`} dataKey="norm" stroke="#64748b" strokeDasharray="5 4" fill="none" strokeWidth={1.5} />
                <Radar name="C min = 50" dataKey="min" stroke="#EF4444" strokeDasharray="3 3" fill="none" strokeWidth={1.5} />
                {compare && <Radar name={compare.stage_label} dataKey="compare" stroke={SERIES.before} fill={SERIES.before} fillOpacity={0.08} strokeWidth={2} />}
                <Radar name={s.stage_label} dataKey="current" stroke={SERIES.after} fill={SERIES.after} fillOpacity={0.22} strokeWidth={2} dot={{ r: 4 }} />
                <Tooltip formatter={(v) => fmt(Number(v), 0)} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card title="KSA dekompozitsiyasi va ko‘nikmalar bo‘shlig‘i matritsasi"
        subtitle={`Cᵢ = 0.30·K + 0.40·S + 0.30·A · ΔCᵢ = max(0, ${fmt(s.norm, 0)} − Cᵢ) · ΔCᵢ > ${s.gap_trigger} bo‘lsa — o‘quv moduli tayinlanadi`}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-3 py-2">Blok</th>
                <th className="px-3 py-2 text-right">wᵢ</th>
                <th className="px-3 py-2 text-right">K (bilim)</th>
                <th className="px-3 py-2 text-right">S (ko‘nikma)</th>
                <th className="px-3 py-2 text-right">A (qobiliyat)</th>
                <th className="px-3 py-2 text-right">Cᵢ</th>
                <th className="px-3 py-2 text-right">ΔCᵢ</th>
                <th className="px-3 py-2">Sub-kompetensiyalar (cᵢ.₁ / cᵢ.₂ / cᵢ.₃)</th>
              </tr>
            </thead>
            <tbody className="tabular-nums">
              {BLOCKS.map((b) => {
                const critical = (b === "C2" || b === "C3") && s.c[b] < 50;
                const gap = s.gaps[b];
                return (
                  <tr key={b} className="border-t border-slate-100">
                    <td className="px-3 py-2"><b className="text-navy">{b}</b> <span className="text-slate-600">{BLOCK_NAMES[b]}</span></td>
                    <td className="px-3 py-2 text-right">{fmt(s.weights[b], 2)}</td>
                    <td className="px-3 py-2 text-right">{fmt(s.k[b])}</td>
                    <td className="px-3 py-2 text-right">{fmt(s.s[b])}</td>
                    <td className="px-3 py-2 text-right">{fmt(s.a[b])}</td>
                    <td className={`px-3 py-2 text-right font-semibold ${critical ? "text-red-600" : "text-navy"}`}>{fmt(s.c[b], 0)}{critical && " ⚠"}</td>
                    <td className="px-3 py-2 text-right">
                      <span className={`rounded px-1.5 py-0.5 ${gap > s.gap_trigger ? "bg-amber-100 font-semibold text-amber-900" : gap > 0 ? "text-slate-700" : "text-emerald-700"}`}>{fmt(gap)}</span>
                    </td>
                    <td className="px-3 py-2 text-xs text-slate-600">{(s.sub_scores[b] ?? []).map((v) => fmt(v, 0)).join(" / ")}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2" title={<span className="flex items-center gap-2"><GraduationCap size={18} /> Avtomatik shakllantirilgan individual o‘quv trayektoriyasi</span>}
          subtitle="Eng past sub-kompetensiya bo‘yicha manzilli modul tanlanadi">
          {s.plan.length === 0 ? (
            <p className="flex items-center gap-2 text-sm text-emerald-700"><CheckCircle2 size={16} /> ΔCᵢ &gt; {s.gap_trigger} bo‘lgan blok yo‘q — majburiy qayta tayyorlash talab etilmaydi.</p>
          ) : (
            <ol className="space-y-3">
              {s.plan.map((p, i) => (
                <li key={p.id} className="flex gap-3 rounded-lg border border-slate-200 p-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-navy text-xs font-bold text-white">{i + 1}</span>
                  <div className="flex-1 text-sm">
                    <div className="font-medium text-navy">{p.title}</div>
                    <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-600">
                      <span className="rounded bg-slate-100 px-1.5 py-0.5">{p.block_code === "BASE" ? "Barcha bloklar" : `${p.block_code} · ${p.sub_code}`}</span>
                      <span className="rounded bg-amber-50 px-1.5 py-0.5 text-amber-800">ΔC = {fmt(p.delta_c)}</span>
                      <span className="rounded bg-slate-100 px-1.5 py-0.5">{p.hours} soat</span>
                      <span className={`rounded px-1.5 py-0.5 ${p.deadline_days <= 30 ? "bg-red-50 text-red-700" : "bg-slate-100"}`}>Muddat: {p.deadline_days} kun</span>
                      <span className="rounded bg-blue-50 px-1.5 py-0.5 text-navy">{p.status}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          )}
          <Link to="/catalog" className="no-print mt-4 inline-flex items-center gap-1 text-sm text-slate2 hover:underline"><BookOpen size={14} /> 36 ta KSA indikatori katalogi</Link>
        </Card>
        <Card title="Hujjat haqiqiyligini tekshirish">
          <div className="flex flex-col items-center gap-3 text-center">
            <QRCodeSVG value={verifyUrl} size={148} fgColor="#1B365D" />
            <div className="break-all font-mono text-xs text-slate-500">{verifyUrl}</div>
            <div className="text-xs text-slate-500">Baholash davomiyligi: {fmt(s.duration_minutes, 0)} daqiqa</div>
          </div>
        </Card>
      </div>
    </div>
  );
}
