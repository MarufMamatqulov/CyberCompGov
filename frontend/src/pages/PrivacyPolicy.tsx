import { Link } from "react-router-dom";
import { ArrowLeft, CheckCircle2, FileText, Lock, Shield, UserCheck } from "lucide-react";
import { Emblem } from "../components/Layout";

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 md:px-8">
          <Link to="/" className="flex items-center gap-3">
            <Emblem size={44} />
            <div>
              <div className="text-xs uppercase tracking-wider text-slate-500">O‘zbekiston Respublikasi</div>
              <div className="text-lg font-bold text-navy">CyberComp-Gov</div>
            </div>
          </Link>
          <Link to="/login" className="inline-flex items-center gap-1.5 text-sm font-medium text-navy hover:underline">
            <ArrowLeft size={16} /> Tizimga qaytish
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-5xl px-4 py-8 md:px-8 md:py-12">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-10">
          <div className="mb-8 border-b border-slate-200 pb-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-800">
              <Shield size={14} /> Rasmiy me’yoriy hujjat
            </div>
            <h1 className="mt-3 text-2xl font-bold text-navy md:text-3xl">
              Shaxsga doir ma’lumotlarni qayta ishlash va maxfiylik siyosati
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              Kuchga kirish sanasi: 2026-yil 1-yanvar · Versiya: 2.1 (Rasmiy nashr)
            </p>
          </div>

          <div className="space-y-8 text-sm leading-relaxed text-slate-700 md:text-base">
            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <FileText size={20} className="text-blue-600" /> 1. Umumiy qoidalar va huquqiy asoslar
              </h2>
              <p className="mt-2">
                Ushbu Maxfiylik siyosati O‘zbekiston Respublikasining 2019-yil 2-iyuldagi <strong>O‘RQ-547-son «Shaxsga doir ma’lumotlar to‘g‘risida»gi</strong> hamda 
                2022-yil 15-apreldagi <strong>O‘RQ-764-son «Kiberxavfsizlik to‘g‘risida»gi</strong> Qonunlari, shuningdek axborot xavfsizligini ta’minlash bo‘yicha milliy 
                va xalqaro standartlar (NIST SP 800-181, ISO/IEC 27001) talablariga muvofiq ishlab chiqilgan.
              </p>
              <p className="mt-2">
                «CyberComp-Gov» axborot tizimi davlat organlari va xo‘jalik birlashmalarining axborot-kommunikatsiya texnologiyalari (AKT) va axborot xavfsizligi mas’ul xodimlarining 
                kasbiy kompetensiyalarini baholash, situatsion sinovdan o‘tkazish hamda diagnostika pasportini yuritish uchun mo‘ljallangan idoraviy yopiq axborot tizimidir.
              </p>
            </section>

            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <UserCheck size={20} className="text-blue-600" /> 2. Qayta ishlanadigan shaxsga doir ma’lumotlar tarkibi
              </h2>
              <p className="mt-2">Tizimda attestatsiyani tashkil etish va amalga oshirish doirasida quyidagi ma’lumotlar qayta ishlanadi:</p>
              <ul className="mt-2 list-inside list-disc space-y-1.5 pl-2">
                <li><strong>Identifikatsiya ma’lumotlari:</strong> Jismoniy shaxsning shaxsiy identifikatsiya raqami (JShShIR / PINFL), familiyasi, ismi va otasining ismi;</li>
                <li><strong>Xizmat va ish joyi ma’lumotlari:</strong> Ishlayotgan davlat organi yoki tashkiloti nomi, tarkibiy bo‘linmasi, egallab turgan lavozimi va umumiy sohaviy ish staji;</li>
                <li><strong>Autentifikatsiya ma’lumotlari:</strong> Foydalanuvchi nomi (login), kriptografik xesh-paroli, E-IMZO elektron raqamli imzo ochiq kaliti seriya raqami va sertifikat ma’lumotlari;</li>
                <li><strong>Kompetensiya va attestatsiya natijalari:</strong> Nazariy testlar (K), virtual laboratoriyalar (S), situatsion keyslar (A) bo‘yicha olingan ballar, integral kiberxavfsizlik indeksi (I_AXK), kompetensiya darajasi va avtomatik shakllantirilgan individual o‘quv trayektoriyasi tavsiyalari;</li>
                <li><strong>Tizimli va texnik jurnallar:</strong> Kirish vaqti, sessiya davomiyligi, autentifikatsiya urinishlari hamda axborot xavfsizligi audit loglari.</li>
              </ul>
            </section>

            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <CheckCircle2 size={20} className="text-blue-600" /> 3. Ma’lumotlarni qayta ishlashning qonuniy maqsadlari
              </h2>
              <p className="mt-2">Foydalanuvchilar ma’lumotlari faqatgina quyidagi aniq va qonuniy maqsadlarda qayta ishlanadi:</p>
              <ol className="mt-2 list-inside list-decimal space-y-1.5 pl-2">
                <li>Davlat organlari AKT mas’ul xodimlarining axborot xavfsizligi sohasidagi bilim, ko‘nikma va qobiliyatlarini xolis va shaffof baholash;</li>
                <li>Milliy muhim axborot infratuzilmasi (MII) obyektlarida axborot xavfsizligiga mas’ul kadrlarning tayyorgarlik darajasini monitoring qilish;</li>
                <li>Aniqlangan kompetensiyaviy bo‘shliqlarni (ΔC) bartaraf etish uchun manzilli va shaxsiylashtirilgan o‘quv modullarini tavsiya etish;</li>
                <li>Attestatsiya komissiyasi tomonidan tasdiqlanadigan QR-kodli rasmiy diagnostika pasportini shakllantirish va uning haqiqiyligini tekshirish.</li>
              </ol>
            </section>

            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <Lock size={20} className="text-blue-600" /> 4. Axborot xavfsizligi va ma’lumotlarni himoyalash choralari
              </h2>
              <p className="mt-2">
                Tizim operatori shaxsga doir ma’lumotlarning maxfiyligi, yaxlitligi va foydalanish imkoniyatini ta’minlash maqsadida quyidagi texnik va tashkiliy choralarni amalga oshiradi:
              </p>
              <ul className="mt-2 list-inside list-disc space-y-1.5 pl-2">
                <li><strong>Shifrlash:</strong> Barcha tarmoq trafigi zamonaviy TLS 1.3 shifrlash protokoli orqali uzatiladi. Foydalanuvchi parollari pbkdf2_sha256 usuli bilan xeshlanadi;</li>
                <li><strong>Kirish nazorati (RBAC):</strong> Tizimda qat’iy rollarga asoslangan kirish nazorati o‘rnatilgan. Xodimlar faqat o‘z natijalarini, tashkilot rahbarlari faqat o‘z xodimlarini, Attestatsiya komissiyasi esa umumiy reyestrni ko‘ra oladi;</li>
                <li><strong>Tarmoq himoyasi:</strong> API so‘rovlariga cheklov (Rate Limiting), kiberhujumlarga qarshi himoya filtrlari (WAF qoidalari), HTTP xavfsizlik sarlavhalari (CSP, HSTS, X-Frame-Options) to‘liq joriy etilgan;</li>
                <li><strong>Zaxiralash:</strong> Ma’lumotlar bazasi muntazam ravishda zaxiralanadi va ruxsatsiz o‘zgartirishlardan ishonchli himoyalanadi.</li>
              </ul>
            </section>

            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <Shield size={20} className="text-blue-600" /> 5. Foydalanuvchilarning huquqlari
              </h2>
              <p className="mt-2">
                O‘RQ-547-son Qonunning 12-moddasiga muvofiq, har bir xodim o‘zining shaxsga doir ma’lumotlari, test natijalari va individual diagnostika pasporti bilan 
                tizimdagi shaxsiy kabinet orqali tanishish, uning PDF nusxasini yuklab olish, noto‘g‘ri yoki eskirgan ma’lumotlarni tuzatish bo‘yicha Attestatsiya komissiyasiga 
                murojaat qilish huquqiga ega.
              </p>
            </section>

            <section className="rounded-xl bg-slate-100 p-5">
              <h2 className="text-base font-bold text-navy">6. Tizim operatori va aloqa ma’lumotlari</h2>
              <p className="mt-1 text-sm text-slate-600">
                Savollar, murojaatlar yoki texnik muammolar yuzaga kelganda quyidagi manzillar orqali bog‘lanishingiz mumkin:
              </p>
              <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2 md:text-sm">
                <div><strong>Tashkilot:</strong> Attestatsiya komissiyasi ma’muriyati</div>
                <div><strong>Elektron pochta:</strong> info@cybercomp.uz / support@cybercomp.uz</div>
              </div>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        © 2026 CyberComp-Gov. Barcha huquqlar himoyalangan.
      </footer>
    </div>
  );
}

