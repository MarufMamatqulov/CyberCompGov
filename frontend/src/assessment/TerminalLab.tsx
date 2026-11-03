import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { RotateCcw, Terminal } from "lucide-react";
import { api } from "../api";
import type { TerminalLab as Lab, TerminalSubmission } from "./types";

export default function TerminalLab({ lab, value, onChange }: {
  lab: Lab;
  value: Partial<TerminalSubmission>;
  onChange: (v: TerminalSubmission) => void;
}) {
  const history = value.history ?? [];
  const transcript = value.transcript ?? [];
  const [cmd, setCmd] = useState("");
  const [busy, setBusy] = useState(false);
  const [cursor, setCursor] = useState<number | null>(null);
  const screen = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    screen.current?.scrollTo({ top: screen.current.scrollHeight });
  }, [transcript.length]);

  const run = async (command: string) => {
    const c = command.trim();
    if (!c || busy) return;
    setBusy(true);
    try {
      if (c === "clear") {
        onChange({ history: [...history, c], transcript: [] });
      } else {
        const r = await api<{ output: string }>(`/api/assessment/labs/${lab.code}/exec`, {
          method: "POST", json: { history, command: c },
        });
        onChange({ history: [...history, c], transcript: [...transcript, { cmd: c, out: r.output }] });
      }
      setCmd("");
      setCursor(null);
    } catch (e) {
      onChange({ history, transcript: [...transcript, { cmd: c, out: `xato: ${(e as Error).message}` }] });
    } finally {
      setBusy(false);
      input.current?.focus();
    }
  };

  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") run(cmd);
    if (e.key === "ArrowUp" && history.length) {
      e.preventDefault();
      const i = cursor === null ? history.length - 1 : Math.max(0, cursor - 1);
      setCursor(i);
      setCmd(history[i]);
    }
    if (e.key === "ArrowDown" && cursor !== null) {
      e.preventDefault();
      const i = cursor + 1;
      if (i >= history.length) { setCursor(null); setCmd(""); } else { setCursor(i); setCmd(history[i]); }
    }
  };

  return (
    <div className="space-y-3">
      <p className="text-sm leading-relaxed text-slate-700">{lab.intro}</p>
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-[#0B1220] shadow-inner">
        <div className="flex items-center gap-2 border-b border-slate-700 bg-slate-800 px-3 py-2 text-xs text-slate-300">
          <Terminal size={14} /> {lab.host} ({lab.ip}) — {lab.code}
          <button
            className="ml-auto flex items-center gap-1 rounded px-2 py-0.5 hover:bg-slate-700"
            onClick={() => onChange({ history: [], transcript: [] })}
            title="Laboratoriya holatini boshlang‘ich holatga qaytarish"
          >
            <RotateCcw size={12} /> Qayta boshlash
          </button>
        </div>
        <div ref={screen} onClick={() => input.current?.focus()}
          className="h-80 overflow-y-auto p-3 font-mono text-[12.5px] leading-relaxed text-slate-200">
          <div className="text-emerald-400">CyberComp-Gov virtual laboratoriyasi. “help” — mavjud buyruqlar.</div>
          {transcript.map((t, i) => (
            <div key={i} className="mt-1">
              <div><span className="text-emerald-400">{lab.host}</span>:<span className="text-sky-400">~</span># {t.cmd}</div>
              {t.out && <pre className="whitespace-pre-wrap text-slate-300">{t.out}</pre>}
            </div>
          ))}
          <div className="mt-1 flex items-center">
            <span className="shrink-0"><span className="text-emerald-400">{lab.host}</span>:<span className="text-sky-400">~</span>#&nbsp;</span>
            <input ref={input} value={cmd} onChange={(e) => setCmd(e.target.value)} onKeyDown={onKey}
              className="flex-1 bg-transparent text-slate-100 caret-emerald-400 outline-none" spellCheck={false}
              autoCapitalize="off" autoComplete="off" disabled={busy} aria-label="Terminal buyrug‘i" />
          </div>
        </div>
      </div>
      <div>
        <div className="mb-1.5 text-xs font-medium text-slate-500">Buyruqlar paneli (bosing — terminalga qo‘yiladi, Enter bilan bajaring; &lt;…&gt; ni o‘zingiz to‘ldiring):</div>
        <div className="flex flex-wrap gap-1.5">
          {lab.hints.map((h) => (
            <button key={h} onClick={() => { setCmd(h); input.current?.focus(); }}
              className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-[11px] text-slate-700 hover:border-slate2 hover:bg-navy-50">
              {h}
            </button>
          ))}
        </div>
      </div>
      <div className="text-xs text-slate-500">Bajarilgan buyruqlar: {history.length}. Natija server tomonida buyruqlar ketma-ketligi bo‘yicha baholanadi.</div>
    </div>
  );
}
