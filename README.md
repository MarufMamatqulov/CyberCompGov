# CyberComp-Gov

**Davlat organlari AKT mas’ul xodimlari axborot xavfsizligi kompetensiyalarini baholash va situatsion testlash axborot tizimi** — magistrlik dissertatsiyasining dasturiy ta’minoti (Mamatqulov Ma’ruf Qosim o‘g‘li, “Cyber university” davlat universiteti, 70610302 — Axborot xavfsizligi).

## Tezkor ishga tushirish (VPS, Ubuntu 22.04/24.04)

```bash
git clone <repo> cybercomp-gov && cd cybercomp-gov
sudo bash deploy/vps-setup.sh      # Docker o‘rnatadi, .env yaratadi, konteynerlarni ishga tushiradi
```

yoki qo‘lda:

```bash
cp .env.example .env               # parollar, JWT_SECRET va PUBLIC_BASE_URL ni o‘zgartiring
docker compose up -d --build
```

Brauzerda: `http://<VPS_IP>` (port `HTTP_PORT`, standart 80). API hujjatlari: `http://<VPS_IP>/api/docs`.

| Konteyner | Vazifa | Port |
|---|---|---|
| `db` | PostgreSQL 16 (`pgdata` volume) | ichki 5432 |
| `backend` | FastAPI + Uvicorn; ishga tushganda `python -m app.seed.seed` | ichki 8000 |
| `frontend` | Nginx: React SPA + `/api` → `backend:8000` proksi | **80** |

## Kirish ma’lumotlari

| Hisob | Login | Parol (standart) |
|---|---|---|
| Komissiya Raisi (admin) | `admin` | `Admin@2026` (`ADMIN_PASSWORD`) |
| e1 — Aliyev Jamshid (Malakali) | `e1` | `Demo@2026` (`OFFICER_PASSWORD`) |
| e2 — Karimov Sardor (Shartli bazaviy, Φ=0) | `e2` | `Demo@2026` |
| e3 — Rustamov Bekzod (Kritik) | `e3` | `Demo@2026` |
| Qolgan 42 xodim | `x02` … `x45` | `Demo@2026` |

* **1-click demo** va **OneID / E-IMZO simulyatsiyasi** faqat `DEMO_MODE=true` bo‘lganda ishlaydi (ERI kaliti demo paroli: `EIMZO_DEMO_PIN`, standart `123456`). Ochiq serverda himoyadan keyin `DEMO_MODE=false` qiling — aks holda istalgan kishi admin sifatida kira oladi.
* Parollar faqat birinchi seed paytida o‘rnatiladi. Ularni o‘zgartirish uchun: `docker compose exec backend python -m app.seed.seed --reset` (barcha ma’lumotlar qayta yaratiladi).

## Ekranlar

1. `/login` — kirish, OneID/ERI modal oynasi, himoya uchun 1-click demo.
2. `/dashboard` — KPI, oldin/keyin grafiklari, malaka darajalari taqsimoti, juftlangan t-test jadvali (3.3), 45 xodim reyestri (faqat admin).
3. `/assessment` — 12 test (K), 4 virtual laboratoriya (S: aktivlar tasnifi, `LAB-C2-01` SSH/firewall terminali, `LAB-C3-02` forenzika va tiklash terminali, `LAB-C4-01` pochta/sandbox), 4 tarmoqlanuvchi keys taymer bilan (A).
4. `/passport/:officerId` — I_AXK, Φ, daraja, radar, KSA jadvali, ΔC, o‘quv trayektoriyasi, QR-kodli PDF.
5. `/catalog` — 4 blok, 12 sub-kompetensiya, 36 KSA indikatori (NIST SP 800-181, ENISA ECSF, milliy me’yorlar).
6. `/ahp-calculator` — Saaty matritsasi, g_p, w, λmax, CI, CR.
7. `/verify/:code` — QR orqali hujjat haqiqiyligini ochiq tekshirish.

## Matematik model (`backend/app/services/scoring_engine.py`)

* `Cᵢ = 0.30·Kᵢ + 0.40·Sᵢ + 0.30·Aᵢ` — **butun ballgacha yaxlitlanadi** (2.4-jadvaldagi e1/e2/e3 natijalari aynan shu qoida bilan chiqadi: masalan, e1 uchun 0.3·88 + 0.4·82 + 0.3·83 = 84.1 → 84).
* `I_AXK = 0.20·C₁ + 0.35·C₂ + 0.25·C₃ + 0.20·C₄`; `Φ = 1 ⇔ C₂ ≥ 50 ∧ C₃ ≥ 50`.
* Darajalar: `<55` Kritik; `≥55 ∧ Φ=0` Shartli bazaviy; `55–71` Bazaviy; `71–86` Malakali; `≥86` Ekspert.
* `ΔCᵢ = max(0, C_norm − Cᵢ)`, `C_norm = 80` (oddiy) / `85` (MII). `ΔCᵢ > 15` bo‘lsa eng past sub-kompetensiya bo‘yicha modul tayinlanadi (Φ=0 bloklari uchun muddat 30 kun, boshqalari 60 kun; Kritik darajada qo‘shimcha 72 soatlik bazaviy kurs).
* Tizimda topshirilgan baholashlar `stage = "attestatsiya"` bilan saqlanadi va 3.3-jadval statistikasiga (faqat `before`/`after`) aralashmaydi.

### AHP haqida muhim eslatma

Dissertatsiyadagi juftlab taqqoslash matritsasi (4/7, 4/5, 7/5, 5/4 …) **to‘liq izchil**: uning har bir elementi aynan `w_p / w_q` ga teng. Shuning uchun aniq hisob `λmax = 4.000`, `CI = 0`, `CR = 0` ni beradi (jadvaldagi 3 xonali yaxlitlangan qiymatlar bilan ham `λmax ≈ 3.9995`). Dissertatsiya matnidagi `λmax ≈ 4.031, CI = 0.0103, CR = 1.14%` qiymatlari bu matritsadan kelib chiqmaydi — ular boshqa (dastlabki ekspert) matritsaga tegishli bo‘lishi mumkin. Vaznlar `[0.20, 0.35, 0.25, 0.20]` va `CR < 10%` sharti har ikki holatda ham bajariladi.

## Eksperimental tanlama (n = 45)

`backend/app/seed/experiment_officers.json` — `app/seed/generate_experiment.py` tomonidan deterministik yaratilgan sintetik tanlama. U 3.3-jadvalning barcha agregat ko‘rsatkichlariga aniq mos keladi: o‘rtachalar (C₁…C₄, I_AXK 56.1 → 79.1, +23.0 / +41.0%), juftlangan `t = 14.82` (df = 44, p < 0.001), Malakali+Ekspert ulushi 20.0% → 68.9%, o‘rtacha attestatsiya vaqti 35 daqiqa. e1, e2, e3 ning “oldin” baholari 2.4-jadvaldagi K/S/A qiymatlari bilan bir xil. Alohida xodimlar ma’lumotlari real shaxslarga tegishli emas.

## Ishlab chiqish

```bash
# backend
cd backend && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
DATABASE_URL=sqlite:///./dev.db uvicorn app.main:app --reload     # seed avtomatik
pytest                                                           # 27 ta test

# frontend (http://localhost:5173, /api → localhost:8000)
cd frontend && npm install && npm run dev
```
