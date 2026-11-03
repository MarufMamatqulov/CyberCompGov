import { useEffect } from "react";
import { AlarmClock, CheckCircle2, Siren } from "lucide-react";
import type { CaseItem, CaseProgress } from "./types";

export function initialProgress(c: CaseItem): CaseProgress {
  return { path: [], current: c.start, remaining: c.time_limit, finished: false };
}

/** Bitta tarmoqlanuvchi keys: har bir tanlov keyingi bosqichni belgilaydi; vaqt tugasa, keys yakunlanadi. */
export default function CaseRunner({ item, progress, onChange, active }: {
  item: CaseItem;
  progress: CaseProgress;
  onChange: (p: CaseProgress) => void;
  active: boolean;
}) {
  const stages = Object.fromEntries(item.stages.map((s) => [s.id, s]));
  const stage = progress.current ? stages[progress.current] : null;

  useEffect(() => {
    if (!active || progress.finished) return;
    const t = setInterval(() => {
      onChange({ ...progress, remaining: Math.max(0, progress.remaining - 1), finished: progress.remaining - 1 <= 0 });
    }, 1000);
    return () => clearInterval(t);
  }, [active, progress, onChange]);

  const choose = (optionId: string) => {
    if (!stage) return;
    const path = [...progress.path, { stage: stage.id, option: optionId }];
    // O‘tishlar ochiq, ballar esa faqat serverda saqlanadi
    const next = stage.options.find((o) => o.id === optionId)?.next ?? null;
    onChange({ ...progress, path, current: next, finished: next === null });
  };

  const mm = String(Math.floor(progress.remaining / 60)).padStart(2, "0");
  const ss = String(progress.remaining % 60).padStart(2, "0");
  const low = progress.remaining <= 30;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className="inline-flex items-center gap-2 rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-700 ring-1 ring-red-200">
          <Siren size={14} /> Faol kiberinsident
        </span>
        <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 font-mono text-sm font-semibold ring-1 ${
          low ? "bg-red-600 text-white ring-red-600" : "bg-slate-100 text-navy ring-slate-200"}`}>
          <AlarmClock size={14} /> {mm}:{ss}
        </span>
        <span className="text-xs text-slate-500">Bosqich {Math.min(progress.path.length + 1, 3)} / 3</span>
      </div>
      {progress.finished || !stage ? (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
          <CheckCircle2 size={18} />
          {progress.remaining <= 0 && progress.current ? "Vaqt tugadi — javobsiz bosqichlar 0 ball bilan baholanadi." : "Keys yakunlandi. Qarorlaringiz qayd etildi."}
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 p-4">
          <p className="text-[15px] leading-relaxed text-slate-800">{stage.text}</p>
          <div className="mt-4 space-y-2">
            {stage.options.map((o) => (
              <button key={o.id} onClick={() => choose(o.id)}
                className="w-full rounded-lg border border-slate-200 px-4 py-3 text-left text-sm transition hover:border-slate2 hover:bg-navy-50">
                <span className="mr-2 font-semibold uppercase text-slate2">{o.id})</span>{o.text}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
