import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ShieldCheck, ShieldX } from "lucide-react";
import { api } from "../api";
import { Emblem } from "../components/Layout";
import { LevelBadge, PhiBadge, Spinner, fmt } from "../components/ui";

interface VerifyOut { valid: boolean; code: string; officer: string; agency: string; date: string; i_axk: number; phi: number; level: string }

export default function Verify() {
  const { code } = useParams();
  const [data, setData] = useState<VerifyOut | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<VerifyOut>(`/api/verify/${code}`).then(setData).catch((e) => setError(e.message));
  }, [code]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
          <Emblem size={44} />
          <div>
            <div className="font-bold text-navy">CyberComp-Gov</div>
            <div className="text-xs text-slate-500">Attestatsiya pasportining haqiqiyligini tekshirish</div>
          </div>
        </div>
        {!data && !error && <Spinner />}
        {error && (
          <div className="mt-5 flex items-center gap-3 rounded-lg bg-red-50 p-4 text-red-700"><ShieldX /> {error}</div>
        )}
        {data && (
          <div className="mt-5 space-y-3 text-sm">
            <div className="flex items-center gap-2 rounded-lg bg-emerald-50 p-3 font-medium text-emerald-800"><ShieldCheck /> Hujjat haqiqiy — № {data.code}</div>
            <div><span className="text-slate-500">Xodim:</span> <b>{data.officer}</b></div>
            <div><span className="text-slate-500">Tashkilot:</span> {data.agency}</div>
            <div><span className="text-slate-500">Sana:</span> {new Date(data.date).toLocaleDateString("uz-UZ")}</div>
            <div className="flex items-center gap-2"><span className="text-slate-500">I AXK:</span> <b>{fmt(data.i_axk, 2)}</b> <PhiBadge phi={data.phi} /></div>
            <LevelBadge level={data.level} />
          </div>
        )}
        <Link to="/login" className="mt-6 block text-center text-xs text-slate2 hover:underline">Tizimga kirish</Link>
      </div>
    </div>
  );
}
