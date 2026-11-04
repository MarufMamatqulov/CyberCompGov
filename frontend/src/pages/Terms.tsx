import { Link } from "react-router-dom";
import { AlertTriangle, ArrowLeft, BookCheck, FileText, Scale, ShieldAlert } from "lucide-react";
import { Emblem } from "../components/Layout";

export default function Terms() {
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
            <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
              <Scale size={14} /> Foydalanish reglamenti
            </div>
            <h1 className="mt-3 text-2xl font-bold text-navy md:text-3xl">
              Tizimdan foydalanish shartlari va attestatsiya reglamenti
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              Davlat organlari va tashkilotlari AKT mas’ul xodimlari axborot xavfsizligi attestatsiyasi qoidalari
            </p>
          </div>

          <div className="space-y-8 text-sm leading-relaxed text-slate-700 md:text-base">
            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <FileText size={20} className="text-emerald-600" /> 1. Tizim maqomi va kirish huquqi
              </h2>
              <p className="mt-2">
                1.1. «CyberComp-Gov» tizimi O‘zbekiston Respublikasi davlat organlari, vazirliklar, idoralar, mahalliy davlat hokimiyati organlari 
                hamda muhim axborot infratuzilmasi obyektlarining AKT va axborot xavfsizligiga mas’ul xodimlari uchun yagona idoraviy baholash portalidir.
              </p>
              <p className="mt-2">
                1.2. Tizimga kirish huquqi faqat vakolatli davlat organlari buyurtmasiga binoan, Attestatsiya komissiyasi yoki tashkilot AKT rahbariyati 
                tomonidan rasmiy tartibda tasdiqlangan xodimlarga beriladi.
              </p>
            </section>

            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <BookCheck size={20} className="text-emerald-600" /> 2. Attestatsiya va sinov jarayoni qoidalari
              </h2>
              <p className="mt-2">
                2.1. Attestatsiya topshiruvchi xodim barcha nazariy testlar (K), virtual laboratoriyalar (S) va tarmoqlanuvchi situatsion keyslarni (A) 
                <strong>shaxsan o‘zi</strong> bajarishi shart.
              </p>
              <p className="mt-2">
                2.2. Baholash davomida uchinchi shaxslar yordamidan foydalanish, javoblarni ko‘chirish, avtomatlashtirilgan botlar yoki skriptlar qo‘llash 
                qat’iyan taqiqlanadi. Har qanday shubhali faoliyat tizim monitoringi tomonidan qayd etiladi va natijalar bekor qilinishi mumkin.
              </p>
              <p className="mt-2">
                2.3. Baholash yakunlangach, tizim O‘zbekiston Respublikasi kiberxavfsizlik metodologiyasiga muvofiq integral indeksni (I_AXK) hamda 
                kritik bloklar ko‘rsatkichini (Φ) avtomatik hisoblab chiqadi.
              </p>
            </section>

            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <AlertTriangle size={20} className="text-amber-600" /> 3. Xizmat siri va konfidensiallik
              </h2>
              <p className="mt-2">
                3.1. Laboratoriya topshiriqlarida keltirilgan virtual tarmoq topologiyalari, konfiguratsiya parametrlari, test savollari va situatsion 
                stsenariylar xizmat doirasida foydalanish uchun mo‘ljallangan bo‘lib, ularni ommaga oshkor qilish yoki uchinchi shaxslarga berish taqiqlanadi.
              </p>
              <p className="mt-2">
                3.2. Foydalanuvchi o‘z hisob ma’lumotlari (login, parol, ERI yopiq kaliti) xavfsizligi va daxlsizligi uchun shaxsan javobgardir.
              </p>
            </section>

            <section>
              <h2 className="flex items-center gap-2 text-lg font-bold text-navy">
                <ShieldAlert size={20} className="text-red-600" /> 4. Javobgarlik va xavfsizlik talablari
              </h2>
              <p className="mt-2">
                4.1. Tizim resurslariga ruxsatsiz kirish, xizmat ko‘rsatishni rad etish (DoS/DDoS) hujumlarini uyushtirish, zaifliklarni qidirish yoki ekspluatatsiya qilish 
                urinishlari O‘zbekiston Respublikasi Jinoyat kodeksining tegishli moddalariga (Axborot texnologiyalari sohasidagi jinoyatlar) muvofiq javobgarlikka sabab bo‘ladi.
              </p>
              <p className="mt-2">
                4.2. Attestatsiya komissiyasi ushbu qoidalarni buzgan xodimning natijalarini haqiqiy emas deb topish va tashkilot rahbariyatiga taqdimnoma kiritish huquqiga ega.
              </p>
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

