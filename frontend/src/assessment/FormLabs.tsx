import { useState } from "react";
import { FlaskConical, Mail, Paperclip } from "lucide-react";
import type { ClassifyLab as CLab, ClassifySubmission, EmailLab as ELab, EmailSubmission } from "./types";

export function ClassifyLab({ lab, value, onChange }: {
  lab: CLab; value: Partial<ClassifySubmission>; onChange: (v: ClassifySubmission) => void;
}) {
  const v: ClassifySubmission = { levels: value.levels ?? {}, storage: value.storage ?? {}, legal: value.legal };
  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-700">{lab.intro}</p>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr><th className="px-3 py-2">Axborot aktivi</th><th className="px-3 py-2">Konfidensiallik darajasi</th><th className="px-3 py-2">Saqlash talabi (O‘RQ-547)</th></tr>
          </thead>
          <tbody>
            {lab.assets.map((a, i) => (
              <tr key={a.id} className="border-t border-slate-100 align-top">
                <td className="px-3 py-3"><span className="mr-1 font-semibold text-navy">{i + 1}.</span>{a.name}</td>
                <td className="px-3 py-3">
                  <select className="input" value={v.levels[a.id] ?? ""}
                    onChange={(e) => onChange({ ...v, levels: { ...v.levels, [a.id]: Number(e.target.value) } })}>
                    <option value="" disabled>Tanlang…</option>
                    {lab.levels.map((l, j) => <option key={l} value={j}>{l}</option>)}
                  </select>
                </td>
                <td className="px-3 py-3">
                  <select className="input" value={v.storage[a.id] ?? ""}
                    onChange={(e) => onChange({ ...v, storage: { ...v.storage, [a.id]: Number(e.target.value) } })}>
                    <option value="" disabled>Tanlang…</option>
                    {lab.storage.map((l, j) => <option key={l} value={j}>{l}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <fieldset className="rounded-lg border border-slate-200 p-3">
        <legend className="px-1 text-sm font-medium text-navy">{lab.legal_question}</legend>
        <div className="flex flex-wrap gap-3">
          {lab.legal_options.map((o, j) => (
            <label key={o} className="flex items-center gap-2 text-sm">
              <input type="radio" name="legal" checked={v.legal === j} onChange={() => onChange({ ...v, legal: j })} /> {o}
            </label>
          ))}
        </div>
      </fieldset>
    </div>
  );
}

export function EmailLab({ lab, value, onChange }: {
  lab: ELab; value: Partial<EmailSubmission>; onChange: (v: EmailSubmission) => void;
}) {
  const v: EmailSubmission = { answers: value.answers ?? {}, sandbox_run: value.sandbox_run ?? false, actions: value.actions ?? [] };
  const [running, setRunning] = useState(false);
  const [shown, setShown] = useState(v.sandbox_run ? lab.sandbox_report.length : 0);

  const runSandbox = () => {
    setRunning(true);
    setShown(0);
    lab.sandbox_report.forEach((_, i) => setTimeout(() => {
      setShown(i + 1);
      if (i === lab.sandbox_report.length - 1) {
        setRunning(false);
        onChange({ ...v, sandbox_run: true });
      }
    }, 450 * (i + 1)));
  };

  const toggle = (id: string) =>
    onChange({ ...v, actions: v.actions.includes(id) ? v.actions.filter((x) => x !== id) : [...v.actions, id] });

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-700">{lab.intro}</p>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-3">
          <div className="rounded-lg border border-slate-200">
            <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600"><Mail size={14} /> Xatning to‘liq sarlavhalari (raw headers)</div>
            <pre className="max-h-64 overflow-auto whitespace-pre-wrap p-3 font-mono text-[11.5px] leading-relaxed text-slate-800">{lab.headers}</pre>
          </div>
          <div className="rounded-lg border border-slate-200 p-3 text-sm">
            <pre className="whitespace-pre-wrap font-sans text-slate-700">{lab.body}</pre>
            <div className="mt-3 flex items-center gap-2 rounded-md bg-slate-50 p-2 text-xs text-slate-600">
              <Paperclip size={14} /> <b>{lab.attachment.name}</b> · {lab.attachment.size}
              <span className="truncate font-mono text-[10px] text-slate-400">SHA-256 {lab.attachment.sha256}</span>
            </div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-[#0B1220] p-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="flex items-center gap-2 text-xs font-semibold text-slate-200"><FlaskConical size={14} /> Izolyatsiyalangan sandbox (Windows 10, Office 2019)</span>
              <button className="btn-secondary px-3 py-1 text-xs" onClick={runSandbox} disabled={running}>
                {running ? "Tahlil qilinmoqda…" : "Ilovani sandbox’da ishga tushirish"}
              </button>
            </div>
            <div className="min-h-[60px] font-mono text-[11.5px] leading-relaxed text-slate-300">
              {lab.sandbox_report.slice(0, shown).map((l) => (
                <div key={l} className={l.startsWith("XULOSA") ? "mt-1 font-semibold text-red-400" : ""}>{l}</div>
              ))}
              {!shown && !running && <span className="text-slate-500">Hisobot hali yo‘q.</span>}
            </div>
          </div>
        </div>
        <div className="space-y-3">
          {lab.questions.map((q) => (
            <fieldset key={q.id} className="rounded-lg border border-slate-200 p-3">
              <legend className="px-1 text-sm font-medium text-navy">{q.text}</legend>
              <div className="flex flex-wrap gap-x-4 gap-y-1">
                {q.options.map((o, j) => (
                  <label key={o} className="flex items-center gap-2 text-sm">
                    <input type="radio" name={q.id} checked={v.answers[q.id] === j}
                      onChange={() => onChange({ ...v, answers: { ...v.answers, [q.id]: j } })} />
                    <span className="font-mono text-[12.5px]">{o}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          ))}
          <fieldset className="rounded-lg border border-slate-200 p-3">
            <legend className="px-1 text-sm font-medium text-navy">Qaysi choralarni ko‘rasiz? (bir nechtasini tanlang)</legend>
            <div className="space-y-1.5">
              {lab.actions.map((a) => (
                <label key={a.id} className="flex items-start gap-2 text-sm">
                  <input type="checkbox" className="mt-0.5" checked={v.actions.includes(a.id)} onChange={() => toggle(a.id)} /> {a.text}
                </label>
              ))}
            </div>
          </fieldset>
        </div>
      </div>
    </div>
  );
}
