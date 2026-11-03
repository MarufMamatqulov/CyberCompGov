import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Fingerprint, KeyRound, Lock, PlayCircle, ShieldCheck, User as UserIcon, X } from "lucide-react";
import { api } from "../api";
import { useAuth } from "../auth";
import { Emblem } from "../components/Layout";
import { ErrorBox } from "../components/ui";
import type { User } from "../types";

interface TokenOut { access_token: string; user: User }
interface Cert { pinfl: string; full_name: string; organization: string; serial: string; valid_to: string }

const DEMO_HINTS: Record<string, string> = {
  admin: "Rahbariyat paneli, 45 xodim reyestri, statistik tahlil",
  e1: "I = 80.55 · Φ = 1 · ΔC₃ = 4",
  e2: "I = 61.75 · C₃ = 44 < 50 → majburiy qayta tayyorlash",
  e3: "I = 48.35 · barcha bloklarda bo‘shliq",
};

export default function Login() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [demo, setDemo] = useState<{ key: string; label: string }[]>([]);
  const [eimzoOpen, setEimzoOpen] = useState(false);

  useEffect(() => {
    if (user) navigate(user.role === "admin" ? "/dashboard" : `/passport/${user.id}`, { replace: true });
  }, [user, navigate]);

  useEffect(() => {
    api<{ key: string; label: string }[]>("/api/auth/demo-accounts").then(setDemo).catch(() => setDemo([]));
  }, []);

  const finish = (r: TokenOut) => signIn(r.access_token, r.user);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      finish(await api<TokenOut>("/api/auth/login", { method: "POST", json: { username, password } }));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const demoLogin = async (key: string) => {
    setError("");
    try {
      finish(await api<TokenOut>(`/api/auth/demo/${key}`, { method: "POST" }));
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy to-slate2">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-8">
        <header className="flex items-center gap-4 text-white">
          <Emblem size={56} />
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-blue-200">O‘zbekiston Respublikasi</div>
            <h1 className="text-2xl font-bold md:text-3xl">CyberComp-Gov</h1>
          </div>
        </header>
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-blue-100 md:text-base">
          Davlat organlari AKT mas’ul xodimlari axborot xavfsizligi kompetensiyalarini baholash va situatsion
          testlash axborot tizimi
        </p>

        <div className="mt-8 grid flex-1 gap-6 lg:grid-cols-5">
          <div className="rounded-2xl bg-white p-6 shadow-xl lg:col-span-2">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-navy"><Lock size={18} /> Tizimga kirish</h2>
            <form onSubmit={submit} className="mt-5 space-y-3">
              <label className="block text-sm">
                <span className="mb-1 block text-slate-600">Login</span>
                <div className="relative">
                  <UserIcon size={16} className="absolute left-3 top-2.5 text-slate-400" />
                  <input className="input pl-9" value={username} onChange={(e) => setUsername(e.target.value)}
                    autoComplete="username" required />
                </div>
              </label>
              <label className="block text-sm">
                <span className="mb-1 block text-slate-600">Parol</span>
                <div className="relative">
                  <KeyRound size={16} className="absolute left-3 top-2.5 text-slate-400" />
                  <input className="input pl-9" type="password" value={password}
                    onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required />
                </div>
              </label>
              {error && <ErrorBox message={error} />}
              <button className="btn-primary w-full" disabled={busy}>{busy ? "Tekshirilmoqda…" : "Kirish"}</button>
            </form>
            <div className="my-5 flex items-center gap-3 text-xs text-slate-400">
              <span className="h-px flex-1 bg-slate-200" /> yoki <span className="h-px flex-1 bg-slate-200" />
            </div>
            <button className="btn-secondary w-full" onClick={() => setEimzoOpen(true)} disabled={!demo.length}>
              <Fingerprint size={18} /> OneID / ERI (E-IMZO) orqali kirish
            </button>
            {!demo.length && (
              <p className="mt-2 text-xs text-slate-400">ERI simulyatsiyasi faqat demo rejimida mavjud.</p>
            )}
          </div>

          {demo.length > 0 && (
            <div className="rounded-2xl border border-white/15 bg-white/10 p-6 text-white backdrop-blur lg:col-span-3">
              <h2 className="flex items-center gap-2 text-lg font-semibold"><PlayCircle size={18} /> Dissertatsiya himoyasi uchun 1-click demo</h2>
              <p className="mt-1 text-sm text-blue-100">2.4-jadvaldagi etalon xodimlar va komissiya raisi sifatida bir bosishda kirish.</p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {demo.map((d) => (
                  <button key={d.key} onClick={() => demoLogin(d.key)}
                    className="group rounded-xl border border-white/20 bg-white/5 p-4 text-left transition hover:border-emerald-300 hover:bg-white/15">
                    <div className="flex items-center gap-2 font-semibold">
                      <ShieldCheck size={16} className="text-emerald-300" /> {d.label}
                    </div>
                    <div className="mt-1 text-xs text-blue-100">{DEMO_HINTS[d.key]}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        <footer className="mt-8 text-xs text-blue-200">
          Magistrlik dissertatsiyasi dasturiy ta’minoti · Mamatqulov Ma’ruf Qosim o‘g‘li · “Cyber university” davlat
          universiteti · 70610302 — Axborot xavfsizligi
        </footer>
      </div>
      {eimzoOpen && <EimzoModal onClose={() => setEimzoOpen(false)} onDone={finish} />}
    </div>
  );
}

function EimzoModal({ onClose, onDone }: { onClose: () => void; onDone: (r: TokenOut) => void }) {
  const [certs, setCerts] = useState<Cert[]>([]);
  const [pinfl, setPinfl] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<Cert[]>("/api/auth/eimzo/certificates").then((c) => {
      setCerts(c);
      if (c[0]) setPinfl(c[0].pinfl);
    }).catch((e) => setError(e.message));
  }, []);

  const sign = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      // Haqiqiy E-IMZO’da bu bosqichda challenge kriptografik imzolanadi; bu yerda simulyatsiya
      await new Promise((r) => setTimeout(r, 600));
      onDone(await api<TokenOut>("/api/auth/eimzo", { method: "POST", json: { pinfl, pin } }));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal>
      <form onSubmit={sign} className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-navy"><Fingerprint /> E-IMZO — ERI kalitini tanlang</h3>
          <button type="button" onClick={onClose} aria-label="Yopish"><X /></button>
        </div>
        <p className="mt-1 text-xs text-slate-500">Simulyatsiya: kompyuterda o‘rnatilgan demo ERI kalitlari (PFX). Demo parol: 123456</p>
        <div className="mt-4 max-h-72 space-y-2 overflow-y-auto">
          {certs.map((c) => (
            <label key={c.pinfl} className={`flex cursor-pointer gap-3 rounded-lg border p-3 text-sm ${
              pinfl === c.pinfl ? "border-slate2 bg-navy-50" : "border-slate-200"}`}>
              <input type="radio" name="cert" checked={pinfl === c.pinfl} onChange={() => setPinfl(c.pinfl)} />
              <div>
                <div className="font-medium text-navy">{c.full_name}</div>
                <div className="text-xs text-slate-500">{c.organization}</div>
                <div className="text-xs text-slate-400">PINFL {c.pinfl} · Seriya {c.serial} · {c.valid_to} gacha</div>
              </div>
            </label>
          ))}
        </div>
        <label className="mt-4 block text-sm">
          <span className="mb-1 block text-slate-600">Kalit paroli</span>
          <input className="input" type="password" value={pin} onChange={(e) => setPin(e.target.value)} required />
        </label>
        {error && <div className="mt-3"><ErrorBox message={error} /></div>}
        <div className="mt-5 flex justify-end gap-2">
          <button type="button" className="btn-secondary" onClick={onClose}>Bekor qilish</button>
          <button className="btn-primary" disabled={busy || !pinfl}>{busy ? "Imzolanmoqda…" : "Imzolash va kirish"}</button>
        </div>
      </form>
    </div>
  );
}
