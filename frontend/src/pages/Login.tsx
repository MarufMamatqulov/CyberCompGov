import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  ChevronDown,
  ChevronUp,
  ClipboardCheck,
  Eye,
  EyeOff,
  FileCheck2,
  Fingerprint,
  IdCard,
  KeyRound,
  Lock,
  Search,
  ShieldCheck,
  User as UserIcon,
} from "lucide-react";
import { api } from "../api";
import { useAuth } from "../auth";
import { Emblem } from "../components/Layout";
import { ErrorBox } from "../components/ui";
import type { User } from "../types";

interface TokenOut {
  access_token: string;
  user: User;
}

interface Cert {
  pinfl: string;
  full_name: string;
  organization: string;
  serial: string;
  valid_to: string;
}

export default function Login() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();

  // Auth form state
  const [authTab, setAuthTab] = useState<"login" | "eimzo">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showRolesHint, setShowRolesHint] = useState(false);

  // E-IMZO state
  const [certs, setCerts] = useState<Cert[]>([]);
  const [pinfl, setPinfl] = useState("");
  const [pin, setPin] = useState("123456");

  // Certificate / Passport Verification search box on Hero
  const [verifyCode, setVerifyCode] = useState("");
  const [verifyError, setVerifyError] = useState("");

  useEffect(() => {
    if (user) {
      if (user.role === "officer") {
        navigate(`/passport/${user.id}`, { replace: true });
      } else {
        navigate("/dashboard", { replace: true });
      }
    }
  }, [user, navigate]);

  useEffect(() => {
    api<Cert[]>("/api/auth/eimzo/certificates")
      .then((c) => {
        setCerts(c);
        if (c[0]) setPinfl(c[0].pinfl);
      })
      .catch(() => setCerts([]));
  }, []);

  const finish = (r: TokenOut) => signIn(r.access_token, r.user);

  const submitLogin = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api<TokenOut>("/api/auth/login", {
        method: "POST",
        json: { username: username.trim(), password },
      });
      finish(res);
    } catch (err) {
      setError((err as Error).message || "Login yoki parol noto‘g‘ri");
    } finally {
      setBusy(false);
    }
  };

  const submitEimzo = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await new Promise((r) => setTimeout(r, 400));
      const res = await api<TokenOut>("/api/auth/eimzo", {
        method: "POST",
        json: { pinfl, pin },
      });
      finish(res);
    } catch (err) {
      setError((err as Error).message || "ERI kaliti paroli noto‘g‘ri");
    } finally {
      setBusy(false);
    }
  };

  const fillAccount = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setAuthTab("login");
  };

  const handleVerifySearch = (e: FormEvent) => {
    e.preventDefault();
    const clean = verifyCode.trim();
    if (!clean) {
      setVerifyError("Iltimos, tekshirish kodini kiriting");
      return;
    }
    navigate(`/verify/${clean}`);
  };

  return (
    <div className="min-h-screen bg-[#F4F6FA] text-slate-800 font-sans">
      {/* 1. TOP UTILITY BAR */}
      <div className="border-b border-slate-200 bg-white text-xs text-slate-600">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2 md:px-8">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-0.5 text-[11px] font-semibold text-amber-800 border border-amber-200/80">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
              Sinov va ishlab chiqish bosqichida (Beta)
            </span>
            <span className="hidden text-slate-500 md:inline text-[11px]">
              Tizim sinov rejimida ishlamoqda, funksional va ma’lumotlarga o‘zgartirishlar kiritilmoqda
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-slate-500">
            <span className="hidden sm:inline">Qonunchilik: <strong>O‘RQ-764 & O‘RQ-547</strong></span>
            <span>·</span>
            <span className="font-semibold text-[#0B4379]">O‘zbekcha</span>
          </div>
        </div>
      </div>

      {/* 2. MAIN HEADER */}
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 md:px-8">
          {/* Brand Logo & Title */}
          <Link to="/" className="flex items-center gap-3.5">
            <Emblem size={46} />
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  Axborot tizimi loyihasi
                </span>
                <span className="rounded bg-amber-100 px-1.5 py-0.2 text-[9px] font-bold text-amber-800">
                  BETA
                </span>
              </div>
              <div className="text-xl font-bold tracking-tight text-[#0B4379] md:text-2xl">
                CyberComp-Gov
              </div>
              <div className="hidden text-[11px] text-slate-500 sm:block">
                AKT mas’ul xodimlari axborot xavfsizligi kompetensiyalarini baholash tizimi
              </div>
            </div>
          </Link>

          {/* Navigation & Action */}
          <div className="flex items-center gap-3">
            <a
              href="#verify-section"
              className="hidden items-center gap-1.5 rounded-lg border border-slate-300 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 lg:flex"
            >
              <Search size={14} className="text-[#0B4379]" /> Pasportni tekshirish
            </a>
            <a
              href="#login-box"
              className="inline-flex items-center gap-2 rounded-xl bg-[#0B4379] px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-[#08335d]"
            >
              <Lock size={14} /> Tizimga kirish
            </a>
          </div>
        </div>
      </header>

      {/* 3. HERO BANNER (Classic attestat.egov.uz rich blue gradient) */}
      <section className="relative overflow-hidden bg-gradient-to-r from-[#09355f] via-[#0B4379] to-[#0A6CB5] py-12 text-white md:py-16">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]" />
        
        <div className="relative mx-auto max-w-7xl px-4 md:px-8">
          <div className="grid items-center gap-8 lg:grid-cols-12">
            {/* Left side: Heading and Description */}
            <div className="space-y-4 lg:col-span-7">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3.5 py-1 text-xs font-medium backdrop-blur">
                <ShieldCheck size={14} className="text-emerald-400" />
                AKT xodimlari axborot xavfsizligi kompetensiyalari diagnostikasi · Sinov talqini
              </div>

              <h1 className="text-2xl font-extrabold leading-snug tracking-tight text-white md:text-4xl">
                Axborot xavfsizligi kompetensiyalarini baholash va situatsion testlash tizimi
              </h1>

              <p className="max-w-2xl text-sm leading-relaxed text-blue-100 md:text-base">
                Davlat organlari va tashkilotlarining axborot xavfsizligiga mas’ul xodimlarining kasbiy kompetensiyalarini
                36 ta KSA indikatori bo‘yicha diagnostika qilish, situatsion sinovdan o‘tkazish va elektron pasportini yuritish.
              </p>

              {/* Instant Verification Search Box on Hero */}
              <div id="verify-section" className="pt-2">
                <div className="rounded-2xl border border-white/20 bg-white/10 p-4 backdrop-blur md:p-5">
                  <div className="text-xs font-semibold text-blue-100 flex items-center gap-1.5 mb-2">
                    <FileCheck2 size={16} className="text-emerald-300" /> Attestatsiya pasporti haqiqiyligini tekshirish
                  </div>
                  <form onSubmit={handleVerifySearch} className="flex flex-col gap-2 sm:flex-row">
                    <div className="relative flex-1">
                      <Search size={16} className="absolute left-3.5 top-3 text-slate-400" />
                      <input
                        type="text"
                        value={verifyCode}
                        onChange={(e) => {
                          setVerifyCode(e.target.value);
                          setVerifyError("");
                        }}
                        placeholder="Tekshirish kodi (masalan: EV-2026-X45-C9D1)"
                        className="w-full rounded-xl border border-transparent bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 shadow-sm focus:border-sky-400 focus:outline-none"
                      />
                    </div>
                    <button
                      type="submit"
                      className="rounded-xl bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-white shadow-md transition hover:bg-emerald-600 sm:w-auto"
                    >
                      Tekshirish
                    </button>
                  </form>
                  {verifyError && (
                    <div className="mt-2 text-xs text-amber-200">{verifyError}</div>
                  )}
                  <div className="mt-2 text-[11px] text-blue-200/80">
                    QR-kod orqali yoki berilgan pasportning verifikatsiya kodi bilan haqiqiyligini tekshirishingiz mumkin.
                  </div>
                </div>
              </div>
            </div>

            {/* Right side: Authentication Card (OneID & Login) */}
            <div id="login-box" className="lg:col-span-5">
              <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xl text-slate-800 md:p-7">
                {/* Auth Mode Tabs */}
                <div className="mb-5 flex rounded-xl bg-slate-100 p-1">
                  <button
                    type="button"
                    onClick={() => { setAuthTab("login"); setError(""); }}
                    className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-2 text-xs font-semibold transition ${
                      authTab === "login"
                        ? "bg-white text-[#0B4379] shadow-sm"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    <UserIcon size={14} /> Login va parol
                  </button>
                  <button
                    type="button"
                    onClick={() => { setAuthTab("eimzo"); setError(""); }}
                    className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-2 text-xs font-semibold transition ${
                      authTab === "eimzo"
                        ? "bg-white text-[#0B4379] shadow-sm"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    <Fingerprint size={14} /> E-IMZO / ERI
                  </button>
                </div>

                {authTab === "login" ? (
                  /* Standard Login Form */
                  <form onSubmit={submitLogin} className="space-y-3.5">
                    <div>
                      <label className="mb-1 block text-xs font-medium text-slate-700">
                        Login (Foydalanuvchi nomi)
                      </label>
                      <div className="relative">
                        <UserIcon size={16} className="absolute left-3.5 top-3 text-slate-400" />
                        <input
                          type="text"
                          className="w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 transition focus:border-[#0B4379] focus:outline-none focus:ring-1 focus:ring-[#0B4379]"
                          placeholder="Loginingizni kiriting"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          autoComplete="username"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="mb-1 block text-xs font-medium text-slate-700">
                        Parol
                      </label>
                      <div className="relative">
                        <KeyRound size={16} className="absolute left-3.5 top-3 text-slate-400" />
                        <input
                          type={showPassword ? "text" : "password"}
                          className="w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder-slate-400 transition focus:border-[#0B4379] focus:outline-none focus:ring-1 focus:ring-[#0B4379]"
                          placeholder="Parolingizni kiriting"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          autoComplete="current-password"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-3 text-slate-400 hover:text-slate-700"
                        >
                          {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>

                    {error && <ErrorBox message={error} />}

                    <button
                      type="submit"
                      disabled={busy}
                      className="w-full rounded-xl bg-[#0B4379] py-3 text-sm font-semibold text-white shadow-md transition hover:bg-[#08335d] disabled:opacity-60"
                    >
                      {busy ? "Tekshirilmoqda…" : "Tizimga kirish"}
                    </button>
                  </form>
                ) : (
                  /* E-IMZO Authentication */
                  <form onSubmit={submitEimzo} className="space-y-3.5">
                    <div>
                      <label className="mb-1 block text-xs font-medium text-slate-700">
                        ERI kalitini tanlang
                      </label>
                      <div className="max-h-48 space-y-2 overflow-y-auto pr-1">
                        {certs.map((c) => (
                          <label
                            key={c.pinfl}
                            className={`flex cursor-pointer gap-2.5 rounded-xl border p-2.5 text-xs transition ${
                              pinfl === c.pinfl
                                ? "border-[#0B4379] bg-blue-50/70 ring-1 ring-[#0B4379]"
                                : "border-slate-200 hover:bg-slate-50"
                            }`}
                          >
                            <input
                              type="radio"
                              name="cert"
                              checked={pinfl === c.pinfl}
                              onChange={() => setPinfl(c.pinfl)}
                              className="mt-0.5"
                            />
                            <div className="min-w-0 flex-1">
                              <div className="font-semibold text-slate-900 truncate">{c.full_name}</div>
                              <div className="text-[11px] text-slate-600 truncate">{c.organization}</div>
                              <div className="text-[10px] text-slate-400">JShShIR: {c.pinfl} · Seriya: {c.serial}</div>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="mb-1 block text-xs font-medium text-slate-700">
                        ERI kaliti paroli
                      </label>
                      <input
                        type="password"
                        value={pin}
                        onChange={(e) => setPin(e.target.value)}
                        placeholder="Kalit parolini kiriting"
                        className="w-full rounded-xl border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-[#0B4379] focus:outline-none focus:ring-1 focus:ring-[#0B4379]"
                        required
                      />
                    </div>

                    {error && <ErrorBox message={error} />}

                    <button
                      type="submit"
                      disabled={busy || !pinfl}
                      className="w-full rounded-xl bg-emerald-600 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-emerald-700 disabled:opacity-60"
                    >
                      {busy ? "Imzolanmoqda…" : "Imzolash va kirish"}
                    </button>
                  </form>
                )}

                {/* Role Accounts Quick Drawer */}
                <div className="mt-5 border-t border-slate-200 pt-3">
                  <button
                    type="button"
                    onClick={() => setShowRolesHint(!showRolesHint)}
                    className="flex w-full items-center justify-between text-xs text-slate-500 hover:text-[#0B4379]"
                  >
                    <span className="font-medium">Tizim rollari va hisoblari</span>
                    {showRolesHint ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>

                  {showRolesHint && (
                    <div className="mt-2.5 space-y-1.5 rounded-xl bg-slate-50 p-2.5 text-xs text-slate-700 border border-slate-200">
                      <div
                        onClick={() => fillAccount("admin", "Admin@2026")}
                        className="cursor-pointer rounded-lg p-1.5 transition hover:bg-white"
                      >
                        <strong className="text-amber-800">1. Komissiya Raisi (Admin):</strong> <code>admin</code>
                      </div>
                      <div
                        onClick={() => fillAccount("expert", "Expert@2026")}
                        className="cursor-pointer rounded-lg p-1.5 transition hover:bg-white"
                      >
                        <strong className="text-purple-800">2. Mustaqil Ekspert:</strong> <code>expert</code>
                      </div>
                      <div
                        onClick={() => fillAccount("supervisor", "Supervisor@2026")}
                        className="cursor-pointer rounded-lg p-1.5 transition hover:bg-white"
                      >
                        <strong className="text-emerald-800">3. Tashkilot AKT rahbari:</strong> <code>supervisor</code>
                      </div>
                      <div
                        onClick={() => fillAccount("officer", "Officer@2026")}
                        className="cursor-pointer rounded-lg p-1.5 transition hover:bg-white"
                      >
                        <strong className="text-blue-800">4. AKT mas’ul xodimi:</strong> <code>officer</code>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. KEY SERVICES / CAPABILITIES (eGov tile cards) */}
      <section className="mx-auto max-w-7xl px-4 py-12 md:px-8">
        <div className="mb-8 text-center">
          <div className="text-xs font-semibold uppercase tracking-wider text-[#0B4379]">
            Tizim imkoniyatlari
          </div>
          <h2 className="mt-1 text-2xl font-bold text-slate-900 md:text-3xl">
            Axborot xavfsizligi attestatsiyasi yo‘nalishlari
          </h2>
          <p className="mx-auto mt-2 max-w-2xl text-xs text-slate-500 md:text-sm">
            Tizim xalqaro standartlar va milliy me’yoriy talablar asosida kadrlar tayyorgarligini to‘liq diagnostika qiladi
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {/* Card 1 */}
          <div className="group rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-[#0B4379]/40">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-[#0B4379]">
              <ClipboardCheck size={24} />
            </div>
            <h3 className="mt-4 text-base font-bold text-slate-900 group-hover:text-[#0B4379] transition">
              Kompleks attestatsiya
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-slate-600">
              Nazariy testlar (K), virtual Linux/SSH terminallari (S) va tarmoqlanuvchi real kiberinsident keyslari (A).
            </p>
          </div>

          {/* Card 2 */}
          <div className="group rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-[#0B4379]/40">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <IdCard size={24} />
            </div>
            <h3 className="mt-4 text-base font-bold text-slate-900 group-hover:text-emerald-700 transition">
              Elektron diagnostika pasporti
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-slate-600">
              Integral indeks (I_AXK), radar diagramma, malaka darajasi va rasmiy QR-kodli elektron PDF pasport.
            </p>
          </div>

          {/* Card 3 */}
          <div className="group rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-[#0B4379]/40">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
              <BookOpen size={24} />
            </div>
            <h3 className="mt-4 text-base font-bold text-slate-900 group-hover:text-purple-700 transition">
              36 ta KSA indikatori
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-slate-600">
              NIST SP 800-181 (NICE) va ENISA ECSF standartlari bilan uyg‘unlashtirilgan to‘liq kompetensiyalar reyestri.
            </p>
          </div>

          {/* Card 4 */}
          <div className="group rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-[#0B4379]/40">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
              <BarChart3 size={24} />
            </div>
            <h3 className="mt-4 text-base font-bold text-slate-900 group-hover:text-amber-700 transition">
              AHP tahlil va monitoring
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-slate-600">
              Saaty matritsasi bo‘yicha ko‘p mezonli tahlil, tashkilotlar bo‘yicha taqqoslash va o‘quv trayektoriyasi.
            </p>
          </div>
        </div>
      </section>

      {/* 5. STATS & COMPLIANCE BANNER */}
      <section className="border-y border-slate-200 bg-white py-10">
        <div className="mx-auto max-w-7xl px-4 md:px-8">
          <div className="grid grid-cols-2 gap-6 text-center md:grid-cols-4">
            <div>
              <div className="text-3xl font-extrabold text-[#0B4379] md:text-4xl">45</div>
              <div className="mt-1 text-xs text-slate-500">Davlat organlari va idoralari</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-[#0B4379] md:text-4xl">36</div>
              <div className="mt-1 text-xs text-slate-500">KSA kompetensiya indikatori</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-emerald-600 md:text-4xl">+41%</div>
              <div className="mt-1 text-xs text-slate-500">Kompetensiya o‘sish samaradorligi</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-[#0B4379] md:text-4xl">100%</div>
              <div className="mt-1 text-xs text-slate-500">Raqamlashtirilgan avtomat baholash</div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. OFFICIAL eGov 4-COLUMN FOOTER */}
      <footer className="border-t border-slate-200 bg-slate-900 text-slate-400 text-xs">
        <div className="mx-auto max-w-7xl px-4 py-12 md:px-8">
          <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-4">
            {/* Col 1 */}
            <div>
              <div className="flex items-center gap-2.5 text-white font-bold text-base">
                <Emblem size={28} /> CyberComp-Gov
              </div>
              <p className="mt-3 text-xs leading-relaxed text-slate-400">
                Davlat organlari AKT mas’ul xodimlari axborot xavfsizligi kompetensiyalarini baholash va situatsion testlash axborot tizimi.
              </p>
            </div>

            {/* Col 2 */}
            <div>
              <div className="font-semibold uppercase tracking-wider text-slate-200 text-xs">
                Asosiy bo‘limlar
              </div>
              <ul className="mt-3 space-y-2">
                <li><Link to="/login" className="hover:text-white transition">Tizimga kirish</Link></li>
                <li><Link to="/catalog" className="hover:text-white transition">KSA katalogi (36)</Link></li>
                <li><Link to="/ahp-calculator" className="hover:text-white transition">AHP kalkulyatori</Link></li>
              </ul>
            </div>

            {/* Col 3 */}
            <div>
              <div className="font-semibold uppercase tracking-wider text-slate-200 text-xs">
                Me’yoriy hujjatlar
              </div>
              <ul className="mt-3 space-y-2">
                <li><Link to="/privacy-policy" className="hover:text-white transition">Maxfiylik siyosati</Link></li>
                <li><Link to="/terms" className="hover:text-white transition">Foydalanish shartlari</Link></li>
                <li><span className="text-slate-500">«Kiberxavfsizlik to‘g‘risida»gi Qonun</span></li>
                <li><span className="text-slate-500">«Shaxsga doir ma’lumotlar to‘g‘risida»gi Qonun</span></li>
              </ul>
            </div>

            {/* Col 4 */}
            <div>
              <div className="font-semibold uppercase tracking-wider text-slate-200 text-xs">
                Xavfsizlik va nazorat
              </div>
              <p className="mt-3 leading-relaxed text-slate-400">
                Tizim yopiq idoraviy tarmoqda faoliyat yuritadi. Barcha sessiyalar va autentifikatsiya jurnallari himoyalangan.
              </p>
            </div>
          </div>

          <div className="mt-10 border-t border-slate-800 pt-6 text-center text-slate-500 text-[11px] md:flex md:justify-between md:text-left">
            <div>
              © 2026 CyberComp-Gov. Barcha huquqlar himoyalangan.
            </div>
            <div className="mt-2 md:mt-0">
              Saytdagi ma’lumotlardan foydalanilganda manbaga havola ko‘rsatilishi shart.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
