import { useEffect, useState } from "react";
import { CheckCircle2, RotateCcw, XCircle } from "lucide-react";
import { api } from "../api";
import { Card, ErrorBox, PageHeader, Spinner, fmt } from "../components/ui";
import { BLOCK_NAMES, type Block } from "../types";

interface AhpOut {
  labels: string[]; matrix: number[][]; geometric_means: number[]; weights: number[];
  lambda_max: number; ci: number; cr: number; ri: number; consistent: boolean;
}

// Saaty shkalasi: 1/9 … 9 hamda dissertatsiya matritsasidagi kasr qiymatlar
const SCALE: { v: number; label: string }[] = [
  ...[9, 8, 7, 6, 5, 4, 3, 2].map((d) => ({ v: 1 / d, label: `1/${d}` })),
  { v: 4 / 7, label: "4/7" }, { v: 5 / 7, label: "5/7" }, { v: 4 / 5, label: "4/5" },
  { v: 1, label: "1" },
  { v: 5 / 4, label: "5/4" }, { v: 7 / 5, label: "7/5" }, { v: 7 / 4, label: "7/4" },
  ...[2, 3, 4, 5, 6, 7, 8, 9].map((d) => ({ v: d, label: String(d) })),
];

function nearest(v: number) {
  return SCALE.reduce((best, s) => (Math.abs(Math.log(s.v / v)) < Math.abs(Math.log(best.v / v)) ? s : best));
}

export default function AhpCalculator() {
  const [matrix, setMatrix] = useState<number[][] | null>(null);
  const [res, setRes] = useState<AhpOut | null>(null);
  const [error, setError] = useState("");
  const [defaultM, setDefaultM] = useState<number[][]>([]);

  useEffect(() => {
    api<AhpOut>("/api/ahp/default").then((r) => {
      setMatrix(r.matrix);
      setDefaultM(r.matrix);
      setRes(r);
    }).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!matrix) return;
    const t = setTimeout(() => {
      api<AhpOut>("/api/ahp/compute", { method: "POST", json: { matrix } }).then((r) => { setRes(r); setError(""); })
        .catch((e) => setError(e.message));
    }, 150);
    return () => clearTimeout(t);
  }, [matrix]);

  if (!matrix || !res) return error ? <ErrorBox message={error} /> : <Spinner />;
  const n = matrix.length;
  const labels = res.labels;

  const setCell = (p: number, q: number, v: number) => {
    const m = matrix.map((r) => [...r]);
    m[p][q] = v;
    m[q][p] = 1 / v;
    setMatrix(m);
  };

  return (
    <div className="space-y-6">
      <PageHeader title="AHP ekspert vazn kalkulyatori (T. Saaty)"
        subtitle="Juftlab taqqoslash matritsasining yuqori uchburchagini o‘zgartiring — teskari elementlar (a_qp = 1/a_pq), geometrik o‘rtachalar, vaznlar, λmax, CI va CR darhol qayta hisoblanadi."
        action={<button className="btn-secondary" onClick={() => setMatrix(defaultM.map((r) => [...r]))}><RotateCcw size={16} /> Dissertatsiya matritsasi</button>} />
      {error && <ErrorBox message={error} />}
      <div className="grid gap-6 xl:grid-cols-5">
        <Card className="xl:col-span-3" title="Juftlab taqqoslash matritsasi A = ‖a_pq‖">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-sm">
              <thead>
                <tr className="text-xs text-slate-500">
                  <th className="px-2 py-2 text-left">Blok</th>
                  {labels.map((l) => <th key={l} className="px-2 py-2">{l}</th>)}
                  <th className="px-2 py-2">g_p</th>
                </tr>
              </thead>
              <tbody className="tabular-nums">
                {matrix.map((row, p) => (
                  <tr key={p} className="border-t border-slate-100">
                    <th className="px-2 py-2 text-left font-semibold text-navy" title={BLOCK_NAMES[labels[p] as Block]}>{labels[p]}</th>
                    {row.map((v, q) => (
                      <td key={q} className="px-1 py-1.5 text-center">
                        {p === q ? (
                          <span className="text-slate-400">1</span>
                        ) : q > p ? (
                          <select className="input px-1 py-1 text-center" value={nearest(v).label}
                            onChange={(e) => setCell(p, q, SCALE.find((s) => s.label === e.target.value)!.v)}>
                            {SCALE.map((s) => <option key={s.label} value={s.label}>{s.label}</option>)}
                          </select>
                        ) : (
                          <span className="text-slate-500">{fmt(v, 3)}</span>
                        )}
                      </td>
                    ))}
                    <td className="px-2 py-2 text-center font-medium">{fmt(res.geometric_means[p], 4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-slate-500">g_p = (∏ a_pq)^(1/{n}); w_p = g_p / Σ g_k; λmax = (1/n)·Σ (A·w)_p / w_p; CI = (λmax − n)/(n − 1); CR = CI / RI_{n} (RI_{n} = {res.ri}).</p>
        </Card>
        <div className="space-y-4 xl:col-span-2">
          <Card title="Normallashgan ustuvorlik vektori w">
            <div className="space-y-3">
              {res.weights.map((w, i) => (
                <div key={i}>
                  <div className="flex justify-between text-sm">
                    <span><b className="text-navy">{labels[i]}</b> <span className="text-xs text-slate-500">{BLOCK_NAMES[labels[i] as Block]}</span></span>
                    <span className="font-semibold tabular-nums">{fmt(w, 4)}</span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-slate-100">
                    <div className="h-2 rounded-full bg-slate2" style={{ width: `${Math.min(100, w * 100 / Math.max(...res.weights))}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </Card>
          <Card title="Izchillik ko‘rsatkichlari">
            <dl className="grid grid-cols-3 gap-3 text-center">
              <div><dt className="text-xs text-slate-500">λmax</dt><dd className="text-xl font-bold tabular-nums text-navy">{fmt(res.lambda_max, 4)}</dd></div>
              <div><dt className="text-xs text-slate-500">CI</dt><dd className="text-xl font-bold tabular-nums text-navy">{fmt(res.ci, 4)}</dd></div>
              <div><dt className="text-xs text-slate-500">CR</dt><dd className={`text-xl font-bold tabular-nums ${res.consistent ? "text-emerald-600" : "text-red-600"}`}>{fmt(res.cr * 100, 2)}%</dd></div>
            </dl>
            <div className={`mt-4 flex items-center gap-2 rounded-lg p-3 text-sm ${res.consistent ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-800"}`}>
              {res.consistent ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
              {res.consistent ? "CR < 10% — ekspert baholari izchil, vaznlardan foydalanish mumkin." : "CR ≥ 10% — matritsa izchil emas, ekspert baholarini qayta ko‘rib chiqing."}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
