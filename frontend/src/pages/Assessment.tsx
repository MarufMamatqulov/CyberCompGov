import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BookOpenCheck, ChevronLeft, ChevronRight, FlaskConical, PlayCircle, Send, Siren, Timer } from "lucide-react";
import { api } from "../api";
import { useAuth } from "../auth";
import CaseRunner, { initialProgress } from "../assessment/CaseRunner";
import { ClassifyLab, EmailLab } from "../assessment/FormLabs";
import TerminalLab from "../assessment/TerminalLab";
import type { CaseProgress, Content, LabSubmission } from "../assessment/types";
import { Card, ErrorBox, PageHeader, Spinner } from "../components/ui";
import { BLOCK_NAMES, type RegistryRow } from "../types";

type Stage = 0 | 1 | 2 | 3;
const STAGES = [
  { title: "Nazariy bilimlar testi", sub: "K₁…K₄ · α = 0.30", icon: BookOpenCheck },
  { title: "Virtual laboratoriya", sub: "S₁…S₄ · β = 0.40", icon: FlaskConical },
  { title: "Situatsion keyslar", sub: "A₁…A₄ · γ = 0.30", icon: Siren },
];

export default function Assessment() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [content, setContent] = useState<Content | null>(null);
  const [officers, setOfficers] = useState<RegistryRow[]>([]);
  const [target, setTarget] = useState<number | "">("");
  const [error, setError] = useState("");
  const [stage, setStage] = useState<Stage>(0);
  const [started, setStarted] = useState<number | null>(null);
  const [now, setNow] = useState(Date.now());
  const [tests, setTests] = useState<Record<string, number>>({});
  const [labs, setLabs] = useState<Record<string, LabSubmission>>({});
  const [labTab, setLabTab] = useState(0);
  const [cases, setCases] = useState<Record<string, CaseProgress>>({});
  const [caseIdx, setCaseIdx] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const topRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api<Content>("/api/assessment/content").then((c) => {
      setContent(c);
      setCases(Object.fromEntries(c.cases.map((x) => [x.code, initialProgress(x)])));
    }).catch((e) => setError(e.message));
    if (user?.role === "admin") api<RegistryRow[]>("/api/officers").then(setOfficers).catch(() => setOfficers([]));
  }, [user]);

  useEffect(() => {
    if (!started) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [started]);

  const updateCase = useCallback((code: string, p: CaseProgress) => setCases((prev) => ({ ...prev, [code]: p })), []);

  const go = (s: Stage) => {
    setStage(s);
    topRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const progress = useMemo(() => {
    if (!content) return { tests: 0, labs: 0, cases: 0 };
    const labDone = content.labs.filter((l) => {
      const v = labs[l.code];
      if (!v) return false;
      if (l.type === "terminal") return (v.history?.length ?? 0) > 0;
      if (l.type === "classify") return Object.keys(v.levels ?? {}).length > 0;
      return Object.keys(v.answers ?? {}).length > 0;
    }).length;
    return {
      tests: Object.keys(tests).length,
      labs: labDone,
      cases: content.cases.filter((c) => cases[c.code]?.finished).length,
    };
  }, [content, tests, labs, cases]);

  const submit = async () => {
    if (!content || !started) return;
    const unfinished = content.cases.length - progress.cases;
    if (unfinished > 0 && !confirm(`${unfinished} ta keys yakunlanmagan — javobsiz bosqichlar 0 ball oladi. Topshirasizmi?`)) return;
    setSubmitting(true);
    setError("");
    try {
      const labPayload = Object.fromEntries(Object.entries(labs).map(([code, v]) => {
        const { transcript: _omit, ...rest } = v;
        void _omit;
        return [code, rest];
      }));
      const r = await api<{ session_id: number; officer_id: number }>("/api/assessment/submit", {
        method: "POST",
        json: {
          officer_id: target === "" ? null : target,
          duration_seconds: Math.round((Date.now() - started) / 1000),
          tests,
          labs: labPayload,
          cases: Object.fromEntries(Object.entries(cases).map(([k, v]) => [k, v.path])),
        },
      });
      navigate(`/passport/${r.officer_id}?session=${r.session_id}`);
    } catch (e) {
      setError((e as Error).message);
      setSubmitting(false);
    }
  };

  if (error && !content) return <ErrorBox message={error} />;
  if (!content) return <Spinner />;

  const elapsed = started ? Math.floor((now - started) / 1000) : 0;
  const clock = `${String(Math.floor(elapsed / 60)).padStart(2, "0")}:${String(elapsed % 60).padStart(2, "0")}`;

  if (!started) {
    return (
      <div>
        <PageHeader title="Kompleks baholash va simulyator"
          subtitle="3 bosqichli imtihon: nazariy test, virtual laboratoriya va situatsion keyslar. Topshirilgach natija dissertatsiya modeli bo‘yicha darhol hisoblanadi." />
        <div className="grid gap-4 md:grid-cols-3">
          {STAGES.map(({ title, sub, icon: Icon }, i) => (
            <div key={title} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-2 text-navy"><Icon size={20} /><span className="font-semibold">{i + 1}-bosqich</span></div>
              <div className="mt-2 font-medium">{title}</div>
              <div className="text-sm text-slate-500">{sub}</div>
              <div className="mt-2 text-xs text-slate-500">
                {i === 0 && `${content.tests.length} ta test savoli (har blokdan 3 ta)`}
                {i === 1 && `${content.labs.length} ta amaliy topshiriq: aktivlar tasnifi, SSH/firewall hardening, insident forenzikasi, fishing tahlili`}
                {i === 2 && `${content.cases.length} ta tarmoqlanuvchi keys, har biriga ${Math.round(content.cases[0].time_limit / 60)} daqiqa`}
              </div>
            </div>
          ))}
        </div>
        <Card className="mt-6" title="Baholanuvchini tanlang">
          {user?.role === "admin" ? (
            <select className="input max-w-xl" value={target} onChange={(e) => setTarget(e.target.value ? Number(e.target.value) : "")}>
              <option value="">O‘zim (Komissiya Raisi — namoyish rejimi)</option>
              {officers.map((o) => <option key={o.id} value={o.id}>{o.full_name} — {o.position} ({o.agency.name})</option>)}
            </select>
          ) : (
            <p className="text-sm text-slate-600">Baholanuvchi: <b>{user?.full_name}</b>, {user?.position}</p>
          )}
          <p className="mt-3 text-xs text-slate-500">C = 0.30·K + 0.40·S + 0.30·A; I AXK = 0.20·C₁ + 0.35·C₂ + 0.25·C₃ + 0.20·C₄; Φ = 1, agar C₂ ≥ 50 va C₃ ≥ 50.</p>
          <button className="btn-primary mt-4" onClick={() => { setStarted(Date.now()); setNow(Date.now()); }}>
            <PlayCircle size={18} /> Imtihonni boshlash
          </button>
        </Card>
      </div>
    );
  }

  return (
    <div ref={topRef} className="space-y-5">
      <div className="sticky top-[53px] z-10 -mx-4 border-b border-slate-200 bg-slate-50/95 px-4 py-3 backdrop-blur md:-mx-8 md:px-8">
        <div className="flex flex-wrap items-center gap-2">
          {STAGES.map(({ title, icon: Icon }, i) => (
            <button key={title} onClick={() => go(i as Stage)}
              className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
                stage === i ? "bg-navy text-white" : "bg-white text-slate-600 ring-1 ring-slate-200 hover:text-navy"}`}>
              <Icon size={16} /> {i + 1}. {title}
              <span className={`rounded-full px-1.5 text-[11px] ${stage === i ? "bg-white/20" : "bg-slate-100"}`}>
                {i === 0 ? `${progress.tests}/${content.tests.length}` : i === 1 ? `${progress.labs}/${content.labs.length}` : `${progress.cases}/${content.cases.length}`}
              </span>
            </button>
          ))}
          <span className="ml-auto flex items-center gap-1.5 font-mono text-sm text-slate-600"><Timer size={16} /> {clock}</span>
          <button className="btn-success" onClick={submit} disabled={submitting}>
            <Send size={16} /> {submitting ? "Hisoblanmoqda…" : "Topshirish va natijani olish"}
          </button>
        </div>
      </div>
      {error && <ErrorBox message={error} />}

      {stage === 0 && (
        <div className="space-y-4">
          {content.tests.map((t, i) => (
            <Card key={t.code} title={`${i + 1}. ${t.question}`} subtitle={`${t.block} — ${BLOCK_NAMES[t.block]} · ${t.sub}`}>
              <div className="grid gap-2">
                {t.options.map((o, j) => (
                  <label key={o} className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2.5 text-sm transition ${
                    tests[t.code] === j ? "border-slate2 bg-navy-50" : "border-slate-200 hover:bg-slate-50"}`}>
                    <input type="radio" name={t.code} className="mt-0.5" checked={tests[t.code] === j}
                      onChange={() => setTests((p) => ({ ...p, [t.code]: j }))} />
                    <span><b className="mr-1 text-slate2">{String.fromCharCode(65 + j)})</b>{o}</span>
                  </label>
                ))}
              </div>
            </Card>
          ))}
          <div className="flex justify-end"><button className="btn-primary" onClick={() => go(1)}>Laboratoriyaga o‘tish <ChevronRight size={16} /></button></div>
        </div>
      )}

      {stage === 1 && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {content.labs.map((l, i) => (
              <button key={l.code} onClick={() => setLabTab(i)}
                className={`rounded-lg px-3 py-2 text-left text-sm ${labTab === i ? "bg-white font-semibold text-navy shadow ring-1 ring-slate2" : "bg-white/60 text-slate-600 ring-1 ring-slate-200"}`}>
                <div className="text-[11px] font-mono text-slate-500">{l.code} · {l.block}</div>{l.title}
              </button>
            ))}
          </div>
          {(() => {
            const l = content.labs[labTab];
            const v = labs[l.code] ?? {};
            const set = (nv: LabSubmission) => setLabs((p) => ({ ...p, [l.code]: nv }));
            return (
              <Card title={l.title} subtitle={`${l.code} · ${l.block} — ${BLOCK_NAMES[l.block]}`}>
                {l.type === "terminal" && <TerminalLab lab={l} value={v} onChange={set} />}
                {l.type === "classify" && <ClassifyLab lab={l} value={v} onChange={set} />}
                {l.type === "email" && <EmailLab lab={l} value={v} onChange={set} />}
              </Card>
            );
          })()}
          <div className="flex justify-between">
            <button className="btn-secondary" onClick={() => (labTab > 0 ? setLabTab(labTab - 1) : go(0))}><ChevronLeft size={16} /> Orqaga</button>
            <button className="btn-primary" onClick={() => (labTab < content.labs.length - 1 ? setLabTab(labTab + 1) : go(2))}>
              {labTab < content.labs.length - 1 ? "Keyingi topshiriq" : "Situatsion keyslarga o‘tish"} <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {stage === 2 && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {content.cases.map((c, i) => (
              <button key={c.code} onClick={() => setCaseIdx(i)}
                className={`rounded-lg px-3 py-2 text-left text-sm ${caseIdx === i ? "bg-white font-semibold text-navy shadow ring-1 ring-slate2" : "bg-white/60 text-slate-600 ring-1 ring-slate-200"}`}>
                <div className="text-[11px] font-mono text-slate-500">{c.code} · {cases[c.code]?.finished ? "yakunlandi" : "faol"}</div>{c.title}
              </button>
            ))}
          </div>
          {(() => {
            const c = content.cases[caseIdx];
            return (
              <Card title={c.title} subtitle={`${c.code} · ${c.block} — ${BLOCK_NAMES[c.block]} · taymer faqat ochiq keysda ishlaydi`}>
                <CaseRunner key={c.code} item={c} progress={cases[c.code]} active
                  onChange={(p) => updateCase(c.code, p)} />
              </Card>
            );
          })()}
          <div className="flex justify-between">
            <button className="btn-secondary" onClick={() => (caseIdx > 0 ? setCaseIdx(caseIdx - 1) : go(1))}><ChevronLeft size={16} /> Orqaga</button>
            {caseIdx < content.cases.length - 1 ? (
              <button className="btn-primary" onClick={() => setCaseIdx(caseIdx + 1)}>Keyingi keys <ChevronRight size={16} /></button>
            ) : (
              <button className="btn-success" onClick={submit} disabled={submitting}><Send size={16} /> Topshirish</button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
