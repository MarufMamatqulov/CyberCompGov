"""Baholash topshiriqlari banki: 12 ta test (K), 4 ta laboratoriya (S), 4 ta situatsion keys (A).

payload — nomzodga yuboriladi; answer — faqat serverda saqlanadi.
"""

TESTS = [
    # ---------------- C1
    dict(code="T-C1-01", block="C1", sub="c1.1",
         question="O‘zbekiston Respublikasining “Kiberxavfsizlik to‘g‘risida”gi Qonuni qaysi raqam bilan qabul qilingan?",
         options=["O‘RQ-547", "O‘RQ-764", "PF-6079", "O‘RQ-560"], correct=1,
         explanation="“Kiberxavfsizlik to‘g‘risida”gi Qonun — O‘RQ-764 (2022-yil 15-aprel)."),
    dict(code="T-C1-02", block="C1", sub="c1.2",
         question="O‘z DSt ISO/IEC 27001 bo‘yicha axborot aktivlarini tasniflashda asosiy mezon nima?",
         options=["Aktivning xarid narxi va amortizatsiya muddati",
                  "Aktiv uchun konfidensiallik, yaxlitlik va foydalanuvchanlik talablari hamda uning tashkilot uchun qiymati",
                  "Aktivni ishlab chiqaruvchi mamlakat",
                  "Aktivdan foydalanuvchi xodimlar soni"], correct=1,
         explanation="Tasniflash CIA (konfidensiallik, yaxlitlik, foydalanuvchanlik) talablari va biznes qiymatiga asoslanadi."),
    dict(code="T-C1-03", block="C1", sub="c1.3",
         question="O‘RQ-547 “Shaxsga doir ma’lumotlar to‘g‘risida”gi Qonunga ko‘ra, O‘zbekiston fuqarolarining shaxsga doir ma’lumotlariga ishlov berishda qanday talab qo‘yilgan?",
         options=["Ma’lumotlar istalgan xalqaro bulut xizmatida saqlanishi mumkin",
                  "Ma’lumotlar faqat qog‘oz shaklida saqlanadi",
                  "Ma’lumotlar bazalari O‘zbekiston hududida joylashgan texnik vositalarda saqlanishi va davlat reyestrida ro‘yxatdan o‘tkazilishi kerak",
                  "Faqat shifrlangan holda xorijga uzatilishi shart"], correct=2,
         explanation="Lokalizatsiya talabi: fuqarolarning shaxsga doir ma’lumotlari O‘zbekiston hududidagi bazalarda ishlanadi va reyestrga kiritiladi."),
    # ---------------- C2
    dict(code="T-C2-01", block="C2", sub="c2.1",
         question="Ko‘p faktorli autentifikatsiya (MFA) ning mohiyati nimadan iborat?",
         options=["Bitta parolni bir necha marta kiritish",
                  "Kamida ikki xil toifadagi omildan foydalanish: bilim (parol), egalik (token/ERI kaliti), biometriya",
                  "Parolni har kuni almashtirish",
                  "Bir nechta foydalanuvchiga bitta hisob berish"], correct=1,
         explanation="MFA turli toifadagi mustaqil omillarni talab qiladi."),
    dict(code="T-C2-02", block="C2", sub="c2.2",
         question="IPSec VPN tunnelida uzatilayotgan paketlar konfidensialligini (shifrlashni) qaysi protokol ta’minlaydi?",
         options=["AH (Authentication Header)", "ESP (Encapsulating Security Payload)", "ICMP", "ARP"], correct=1,
         explanation="AH faqat yaxlitlik va autentifikatsiyani beradi; shifrlash ESP orqali amalga oshiriladi."),
    dict(code="T-C2-03", block="C2", sub="c2.3",
         question="Idora serverida ishlatilayotgan dasturiy ta’minot uchun CVSS 9.8 bahoga ega yangi CVE e’lon qilindi. To‘g‘ri birinchi harakat qaysi?",
         options=["Keyingi rejali yangilanishgacha (6 oy) kutish",
                  "Zaif versiya qaysi aktivlarda borligini aniqlash, kompensatsion chora qo‘llash va yamoqni sinov muhitida tekshirib tezkor o‘rnatish",
                  "Serverni internetdan butunlay va muddatsiz uzib qo‘yish",
                  "Faqat antivirus bazasini yangilash"], correct=1,
         explanation="Kritik zaiflik: inventarizatsiya → kompensatsion chora → tezkor patch-menejment."),
    # ---------------- C3
    dict(code="T-C3-01", block="C3", sub="c3.1",
         question="Quyidagilardan qaysi biri kompromentatsiya indikatori (IoC) hisoblanadi?",
         options=["Serverda NTP vaqt sinxronizatsiyasi",
                  "Ma’lum boshqaruv (C2) serveri IP manziliga 4444-portga chiquvchi doimiy ulanish",
                  "Xodimning ish vaqtida tizimga kirishi",
                  "Rejalashtirilgan tungi backup jarayoni"], correct=1,
         explanation="Noma’lum tashqi C2 manzilga chiquvchi ulanish — klassik IoC."),
    dict(code="T-C3-02", block="C3", sub="c3.2",
         question="Kiberinsidentlarga javob berish (NIST SP 800-61) bosqichlarining to‘g‘ri ketma-ketligi qaysi?",
         options=["Tiklash → Aniqlash → Tayyorgarlik → Tahlil",
                  "Tayyorgarlik → Aniqlash va tahlil → Lokalizatsiya, bartaraf etish va tiklash → Insidentdan keyingi faoliyat",
                  "Aniqlash → Jarima → Hisobot",
                  "Bartaraf etish → Tayyorgarlik → Aniqlash"], correct=1,
         explanation="NIST SP 800-61 ning 4 bosqichli hayot sikli."),
    dict(code="T-C3-03", block="C3", sub="c3.3",
         question="Zaxira nusxalashning “3-2-1” qoidasi nimani anglatadi?",
         options=["3 kunda 2 marta 1 ta serverga nusxa olish",
                  "Ma’lumotlarning 3 ta nusxasi, 2 xil turdagi tashuvchida, 1 tasi esa tashqi (offsite) joyda saqlanadi",
                  "3 ta administrator, 2 ta parol, 1 ta kalit",
                  "RPO 3 soat, RTO 2 soat, 1 ta zaxira"], correct=1,
         explanation="3 nusxa — 2 tur tashuvchi — 1 tasi offsite/offline."),
    # ---------------- C4
    dict(code="T-C4-01", block="C4", sub="c4.1",
         question="Elektron pochtada DMARC mexanizmi qanday vazifani bajaradi?",
         options=["Xat matnini shifrlaydi",
                  "SPF va DKIM natijalari asosida domen egasining siyosatini (none/quarantine/reject) qo‘llaydi va hisobot yuboradi",
                  "Ilova fayllarni avtomatik siqadi",
                  "Pochta qutisi hajmini kengaytiradi"], correct=1,
         explanation="DMARC — SPF/DKIM moslashuvi va domen siyosati."),
    dict(code="T-C4-02", block="C4", sub="c4.2",
         question="Idora yo‘lagida egasi noma’lum USB-flesh topildi. To‘g‘ri harakat qaysi?",
         options=["Egasini aniqlash uchun ishchi kompyuterga ulab ko‘rish",
                  "Ishchi kompyuterga ulamasdan AX bo‘limiga topshirish va izolyatsiyalangan stendda (sandbox) tekshirish",
                  "Formatlab, o‘zi uchun ishlatish",
                  "Rahbar kompyuteriga ulab berish"], correct=1,
         explanation="Noma’lum tashuvchi — zararli dastur tarqatishning keng tarqalgan usuli (USB drop)."),
    dict(code="T-C4-03", block="C4", sub="c4.3",
         question="Telefon orqali o‘zini Cert.uz xodimi deb tanishtirgan shaxs “hujumni tekshirish” uchun server administrator parolini so‘ramoqda. To‘g‘ri javob?",
         options=["Vaziyat shoshilinch bo‘lgani uchun parolni aytish",
                  "Parolni SMS orqali yuborish",
                  "Rad etish, rasmiy raqam orqali qayta qo‘ng‘iroq qilib tekshirish va hodisani AX bo‘limida qayd etish",
                  "Vaqtinchalik parol berib, keyin almashtirish"], correct=2,
         explanation="Vishing: hech qachon parol aytilmaydi; mustaqil kanal orqali tasdiqlash."),
]

# ----------------------------------------------------------------- Laboratoriyalar

LAB_C1 = dict(
    code="LAB-C1-01", block="C1", sub="c1.2", title="Davlat axborot aktivlarini tasniflash va lokalizatsiya",
    payload=dict(
        type="classify",
        intro="Idoraning 4 ta axborot aktivini konfidensiallik darajasi va saqlash talabi bo‘yicha tasniflang. "
              "Shuningdek, 1-aktiv uchun asosiy huquqiy asosni ko‘rsating.",
        levels=["Ochiq", "XDFU (xizmat doirasida foydalanish uchun)", "Konfidensial (shaxsga doir ma’lumot)",
                "Yuqori kritik (texnik maxfiy ma’lumot)"],
        storage=["O‘zbekiston hududidagi server (lokalizatsiya majburiy)", "Xorijiy bulut xizmati ruxsat etiladi",
                 "Ochiq hosting (maxsus talab yo‘q)"],
        assets=[
            {"id": "a1", "name": "Fuqarolarning PINFL, pasport ma’lumotlari va yashash manzili bazasi (murojaatlar tizimi)"},
            {"id": "a2", "name": "Idora rasmiy veb-saytidagi yangiliklar va matbuot relizlari"},
            {"id": "a3", "name": "Ichki buyruqlar loyihalari va xizmat yozishmalari"},
            {"id": "a4", "name": "Tarmoq qurilmalari konfiguratsiyasi va administrator parollari"},
        ],
        legal_question="1-aktiv (fuqarolar bazasi) uchun asosiy huquqiy asos:",
        legal_options=["O‘RQ-547 “Shaxsga doir ma’lumotlar to‘g‘risida”", "PF-6079 “Raqamli O‘zbekiston — 2030”",
                       "Mehnat kodeksi"],
    ),
    answer=dict(
        levels={"a1": 2, "a2": 0, "a3": 1, "a4": 3},
        storage={"a1": 0, "a2": 2, "a3": 0, "a4": 0},
        legal=0,
    ),
)

LAB_C2 = dict(
    code="LAB-C2-01", block="C2", sub="c2.1", title="Firewall va SSH hardening (srv-portal-01)",
    payload=dict(
        type="terminal", host="root@srv-portal-01", ip="10.10.20.10",
        intro="Davlat xizmatlari portali serveri srv-portal-01 (10.10.20.10) da xavfsizlik auditi kamchiliklar aniqladi. "
              "Topshiriqlar: (1) root orqali SSH kirishni taqiqlang va parol bilan autentifikatsiyani o‘chiring; "
              "(2) SSH xizmatini qayta ishga tushiring; (3) ochiq qolgan RDP 3389-portini yoping; "
              "(4) 22/tcp ga faqat boshqaruv tarmog‘i 10.10.99.0/24 dan ruxsat bering, kiruvchi trafik uchun "
              "standart siyosat — deny; (5) ufw ni yoqing (SSH qoidasidan keyin!); (6) zaif openssh-server paketini yangilang.",
        hints=["cat /etc/ssh/sshd_config", "ss -tlnp", "ufw status verbose", "apt list --upgradable",
               "sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config",
               "sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config",
               "systemctl restart sshd", "ufw default deny incoming", "ufw deny 3389/tcp",
               "ufw allow from 10.10.99.0/24 to any port 22 proto tcp", "ufw enable",
               "apt install --only-upgrade openssh-server"],
    ),
    answer=dict(engine="c2"),
)

LAB_C3 = dict(
    code="LAB-C3-02", block="C3", sub="c3.1", title="Insident forenzikasi va zaxiradan tiklash (db-gov-02)",
    payload=dict(
        type="terminal", host="root@db-gov-02", ip="10.10.20.15",
        intro="SIEM 10.10.20.15 (db-gov-02) serverida shubhali faollik haqida ogohlantirish berdi. "
              "Topshiriqlar: (1) /var/log/auth.log va tarmoq ulanishlarini tahlil qiling; (2) zararli faylni "
              "raqamli dalil sifatida /root/evidence/ ga saqlang (jarayonni to‘xtatishdan oldin); (3) 185.220.101.44:4444 "
              "ga ulangan zararli jarayonni to‘xtating; (4) tajovuzkor IP manzilini firewall’da bloklang; "
              "(5) buzilgan hisobni bloklang; (6) /var/backups/pg_dump dagi zaxirani SHA-256 orqali tekshirib, "
              "faqat yaxlit nusxani tiklang. Serverni o‘chirib-yoqish taqiqlanadi (dalillar yo‘qoladi).",
        hints=["cat /var/log/auth.log", "grep 'Accepted' /var/log/auth.log", "netstat -tunap", "ps aux",
               "cp /tmp/.x/kworkerd /root/evidence/", "sha256sum /tmp/.x/kworkerd", "kill -9 <PID>",
               "ufw deny from <IP>", "iptables -A OUTPUT -d <IP> -j DROP", "passwd -l <user>",
               "ls -la /var/backups/pg_dump", "cat /var/backups/pg_dump/SHA256SUMS",
               "sha256sum /var/backups/pg_dump/<fayl>", "pg_restore -d egov /var/backups/pg_dump/<fayl>"],
    ),
    answer=dict(engine="c3"),
)

LAB_C4 = dict(
    code="LAB-C4-01", block="C4", sub="c4.1", title="Pochta sarlavhalari va sandbox inspektori",
    payload=dict(
        type="email",
        intro="Devonxonaga “vazirlik” nomidan shoshilinch xat keldi. Sarlavhalarni tahlil qiling, ilovani sandbox’da "
              "ishga tushiring va xulosa bering.",
        headers=(
            "Return-Path: <bounce@digital-gov-uz.top>\n"
            "Received: from mail.digital-gov-uz.top (mail.digital-gov-uz.top [91.243.44.17])\n"
            "        by mx.hokimiyat.uz with ESMTP id 4Qx7Lm2; Mon, 02 Nov 2026 08:41:12 +0500\n"
            "Authentication-Results: mx.hokimiyat.uz;\n"
            "        spf=fail (domain of digital.gov.uz does not designate 91.243.44.17 as permitted sender)\n"
            "        smtp.mailfrom=digital.gov.uz;\n"
            "        dkim=none (message not signed);\n"
            "        dmarc=fail (p=QUARANTINE) header.from=digital.gov.uz\n"
            "From: \"Vazirlik Devonxonasi\" <devonxona@digital.gov.uz>\n"
            "Reply-To: <devon-rahbar@mail-box.top>\n"
            "To: <akt@hokimiyat.uz>\n"
            "Subject: SHOSHILINCH: Vazir buyrug‘i — 2 soat ichida tanishib, imzolang\n"
            "Date: Mon, 02 Nov 2026 08:40:55 +0500\n"
            "X-Mailer: PHPMailer 6.1.4\n"
            "Content-Type: multipart/mixed; boundary=\"b1_8f3a\"\n"
        ),
        body="Hurmatli mas’ul xodim!\n\nVazirning 2026-yil 1-noyabrdagi 1147-sonli buyrug‘i ilovada. Hujjatni ochib, "
             "“Tahrirlashni yoqish” (Enable Content) tugmasini bosing va 2 soat ichida imzolangan nusxani javob xatida "
             "yuboring. Kechikish intizomiy javobgarlikka sabab bo‘ladi.\n\nHurmat bilan,\nDevonxona",
        attachment={"name": "Buyruq_2026_1147.docm", "size": "184 KB",
                    "sha256": "9f2c4e0b7a1d3c5e8f60a2b4c6d8e0f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3"},
        sandbox_report=[
            "[00:00.4] WINWORD.EXE Buyruq_2026_1147.docm ni ochdi",
            "[00:01.2] VBA makros: AutoOpen() ishga tushdi",
            "[00:01.9] Jarayon yaratildi: powershell.exe -nop -w hidden -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBi...",
            "[00:02.7] HTTP GET hxxp://185.220.101.44/upd.exe (200 OK, 412 KB)",
            "[00:03.5] Fayl yozildi: %APPDATA%\\Microsoft\\svchost32.exe",
            "[00:04.1] Rejalashtirilgan vazifa yaratildi: \\MicrosoftEdgeUpdateCore (har 15 daqiqada)",
            "[00:05.0] Tarmoq: 185.220.101.44:4444 ga TCP ulanish (beacon)",
            "XULOSA: YUQORI XAVF — makros yuklovchi (dropper) + masofaviy boshqaruv troyani",
        ],
        questions=[
            {"id": "q1", "text": "SPF tekshiruvi natijasi:", "options": ["pass", "fail", "softfail", "neutral"]},
            {"id": "q2", "text": "DKIM imzosi holati:", "options": ["pass", "fail", "none (imzo yo‘q)"]},
            {"id": "q3", "text": "DMARC natijasi:", "options": ["pass", "fail", "bypass"]},
            {"id": "q4", "text": "Xatning haqiqiy yuboruvchi (texnik) domeni:",
             "options": ["digital.gov.uz", "digital-gov-uz.top", "hokimiyat.uz", "mail-box.top"]},
            {"id": "q5", "text": "Ilova fayldagi tahdid turi:",
             "options": ["Xavfsiz hujjat", "Makros-virus (yuklovchi/dropper)", "Faqat reklama (adware)",
                         "Shifrlangan arxiv"]},
            {"id": "q6", "text": "Bloklanishi kerak bo‘lgan asosiy IoC (IP manzil):",
             "options": ["10.10.20.15", "91.243.44.17", "185.220.101.44", "8.8.8.8"]},
        ],
        actions=[
            {"id": "x1", "text": "Xatni va ilovani karantinga olish, foydalanuvchilar qutilaridan o‘chirish"},
            {"id": "x2", "text": "185.220.101.44 va digital-gov-uz.top / mail-box.top ni shlyuz va firewall’da bloklash"},
            {"id": "x3", "text": "Kiberinsident haqida Cert.uz ga belgilangan tartibda xabar berish"},
            {"id": "x4", "text": "Xodimlarni soxta xat haqida darhol ogohlantirish"},
            {"id": "x5", "text": "Hujjatni ochib, “Enable Content” ni bosib mazmunini tekshirish"},
            {"id": "x6", "text": "Reply-To manziliga javob yozib, yuboruvchini aniqlashtirish"},
        ],
    ),
    answer=dict(
        q={"q1": 1, "q2": 2, "q3": 1, "q4": 1, "q5": 1, "q6": 2},
        q_sub={"q1": "c4.1", "q2": "c4.1", "q3": "c4.1", "q4": "c4.1", "q5": "c4.2", "q6": "c4.2"},
        good_actions=["x1", "x2", "x3", "x4"], bad_actions=["x5", "x6"],
    ),
)

LABS = [LAB_C1, LAB_C2, LAB_C3, LAB_C4]

# ----------------------------------------------------------------- Situatsion keyslar
# Har bir bosqich: id, sub, text, options[{id, text, points (0..10), next | None}]

CASES = [
    dict(code="CASE-C1", block="C1", sub="c1.1", title="Audit arafasida: fuqarolar bazasi xorijiy bulutda",
         time_limit=180, start="s1",
         stages=[
             dict(id="s1", sub="c1.3",
                  text="Ertaga idorada kiberxavfsizlik bo‘yicha rejali audit. Siz fuqarolar murojaatlari tizimining "
                       "bazasi (PINFL, manzillar) xorijiy bulut xizmatida joylashganini aniqladingiz. Harakatingiz?",
                  options=[
                      dict(id="a", text="Rahbariyatga darhol yozma xabar berib, bazani O‘zbekistondagi data-markazga "
                                        "ko‘chirish va davlat reyestrida ro‘yxatdan o‘tkazish rejasini taqdim etaman",
                           points=10, next="s2a"),
                      dict(id="b", text="Audit tugaguncha hech kimga aytmayman", points=0, next="s2b"),
                      dict(id="c", text="Bazani darhol bulutdan o‘chirib tashlayman", points=2, next="s2b"),
                  ]),
             dict(id="s2a", sub="c1.2",
                  text="Ko‘chirish jarayonida murojaatlar xizmati taxminan 4 soat to‘xtaydi. Qanday tashkil etasiz?",
                  options=[
                      dict(id="a", text="Tungi texnik oynada, oldindan to‘liq zaxira nusxa olib, fuqarolarni portal "
                                        "orqali ogohlantirgan holda", points=10, next="s3"),
                      dict(id="b", text="Kunduzi darhol, ogohlantirishsiz ko‘chiraman", points=4, next="s3"),
                  ]),
             dict(id="s2b", sub="c1.2",
                  text="Auditor bazaning xorijda ekanini o‘zi aniqladi va izoh so‘ramoqda.",
                  options=[
                      dict(id="a", text="Faktni tan olib, bartaraf etish rejasi va muddatlarini taqdim etaman",
                           points=7, next="s3"),
                      dict(id="b", text="Hujjatlarni o‘zgartirib, baza O‘zbekistonda deb ko‘rsataman", points=0,
                           next=None),
                  ]),
             dict(id="s3", sub="c1.1",
                  text="Audit dalolatnomasiga muvofiqlikni asoslash uchun qaysi hujjatlar to‘plamini taqdim etasiz?",
                  options=[
                      dict(id="a", text="AX siyosati, aktivlar reyestri, xavflarni baholash hisoboti va lokalizatsiya "
                                        "dalolatnomasi", points=10, next=None),
                      dict(id="b", text="Faqat dasturiy ta’minot litsenziyalari ro‘yxati", points=3, next=None),
                      dict(id="c", text="Og‘zaki tushuntirish yetarli", points=0, next=None),
                  ]),
         ]),
    dict(code="CASE-C2", block="C2", sub="c2.1", title="Tungi imtiyoz oshirish (privilege escalation)",
         time_limit=180, start="s1",
         stages=[
             dict(id="s1", sub="c2.1",
                  text="03:12 da SIEM ogohlantirishi: veb-serverdagi “web_user” xizmat hisobi sudo guruhiga qo‘shildi. "
                       "Bunday o‘zgarish rejalashtirilmagan. Birinchi harakatingiz?",
                  options=[
                      dict(id="a", text="Hisobni bloklayman, faol sessiyalarni uzaman, /etc/sudoers va /etc/group "
                                        "o‘zgarishlarini tekshiraman", points=10, next="s2"),
                      dict(id="b", text="Ertalab ish vaqtida rahbarga xabar beraman", points=2, next="s2late"),
                      dict(id="c", text="Serverni darhol tok manbaidan uzaman", points=4, next="s2"),
                  ]),
             dict(id="s2", sub="c2.3",
                  text="Tahlil ko‘rsatdiki, kirish CMS ning zaif plagini (CVSS 9.8) orqali amalga oshirilgan. Keyingi qadam?",
                  options=[
                      dict(id="a", text="WAF’da vaqtinchalik qoida, plaginni yangilash, barcha parol va SSH kalitlarini "
                                        "almashtirish", points=10, next="s3"),
                      dict(id="b", text="Faqat web_user parolini almashtiraman", points=3, next="s3"),
                  ]),
             dict(id="s2late", sub="c2.3",
                  text="Ertalabgacha tajovuzkor root huquqini olib, yangi administrator hisobini yaratdi.",
                  options=[
                      dict(id="a", text="Serverni tarmoqdan izolyatsiya qilib, tasdiqlangan toza obrazdan qayta "
                                        "o‘rnataman", points=6, next="s3"),
                      dict(id="b", text="Yangi hisobni o‘chirib, ishni davom ettiraman", points=1, next="s3"),
                  ]),
             dict(id="s3", sub="c2.2",
                  text="Hodisa takrorlanmasligi uchun qaysi tizimli choralarni joriy etasiz?",
                  options=[
                      dict(id="a", text="Least privilege/RBAC, administratorlar uchun MFA, sudo loglarini SIEM’ga "
                                        "uzatish, DMZ segmentatsiya va oylik zaiflik skanerlash", points=10, next=None),
                      dict(id="b", text="Yangi antivirus o‘rnatish", points=3, next=None),
                      dict(id="c", text="Hech qanday o‘zgarish kerak emas", points=0, next=None),
                  ]),
         ]),
    dict(code="CASE-C3", block="C3", sub="c3.2", title="Shifrlovchi virus (ransomware) hujumi",
         time_limit=180, start="s1",
         stages=[
             dict(id="s1", sub="c3.2",
                  text="09:40. Bo‘lim fayl serverida .locked kengaytmali fayllar ko‘paymoqda, ekranlarda to‘lov talabi "
                       "chiqdi. Birinchi 5 daqiqadagi harakatingiz?",
                  options=[
                      dict(id="a", text="Zararlangan uzel va segmentni tarmoqdan uzaman (kabel/VLAN), lekin "
                                        "kompyuterlarni o‘chirmayman", points=10, next="s2"),
                      dict(id="b", text="Barcha kompyuterlarni darhol o‘chirib qo‘yaman", points=4, next="s2"),
                      dict(id="c", text="Tajovuzkor bilan to‘lov bo‘yicha muzokara boshlayman", points=0,
                           next="s2bad"),
                  ]),
             dict(id="s2", sub="c3.1",
                  text="Tarqalish to‘xtatildi. Endi nima qilasiz?",
                  options=[
                      dict(id="a", text="Cert.uz ga belgilangan tartibda xabar beraman, xotira obrazi va loglarni "
                                        "dalil sifatida saqlayman, rahbariyatni xabardor qilaman", points=10, next="s3"),
                      dict(id="b", text="Faqat ichki chatda hamkasblarni ogohlantiraman", points=3, next="s3"),
                  ]),
             dict(id="s2bad", sub="c3.1",
                  text="Tajovuzkor summani oshirdi, shifrlash boshqa serverlarga tarqalmoqda.",
                  options=[
                      dict(id="a", text="Darhol izolyatsiya qilib, Cert.uz ga xabar beraman", points=5, next="s3"),
                      dict(id="b", text="To‘lovni amalga oshiraman", points=0, next=None),
                  ]),
             dict(id="s3", sub="c3.3",
                  text="Xizmatlarni qanday tiklaysiz?",
                  options=[
                      dict(id="a", text="Offline/immutable zaxiradan, avval SHA-256 bilan yaxlitlikni tekshirib, toza "
                                        "muhitda tiklayman", points=10, next=None),
                      dict(id="b", text="Eng so‘nggi onlayn zaxiradan darhol tiklayman", points=4, next=None),
                      dict(id="c", text="Shifrlangan fayllarni qo‘lda tiklashga urinaman", points=1, next=None),
                  ]),
         ]),
    dict(code="CASE-C4", block="C4", sub="c4.3", title="Whaling va vishing: “rahbariyat” topshirig‘i",
         time_limit=180, start="s1",
         stages=[
             dict(id="s1", sub="c4.1",
                  text="Messenjerda “vazir o‘rinbosari” profil rasmi bilan xabar: “Zudlik bilan yangi hamkor uchun VPN "
                       "hisobi yarating va loginni shu yerga yuboring. Hozir majlisdaman, qo‘ng‘iroq qilmang.”",
                  options=[
                      dict(id="a", text="Rasmiy telefon raqami yoki qabulxona orqali shaxsan tasdiqlayman",
                           points=10, next="s2"),
                      dict(id="b", text="Rahbar so‘ragani uchun tezda yaratib yuboraman", points=0, next="s2bad"),
                      dict(id="c", text="E’tiborsiz qoldiraman, hech kimga aytmayman", points=4, next="s2"),
                  ]),
             dict(id="s2", sub="c4.3",
                  text="Bir soatdan so‘ng “Cert.uz xodimi” qo‘ng‘iroq qilib, “hujumni tekshirish uchun” serverga AnyDesk "
                       "orqali kirish so‘ramoqda.",
                  options=[
                      dict(id="a", text="Rad etaman, rasmiy raqamga qayta qo‘ng‘iroq qilaman va hodisani qayd etaman",
                           points=10, next="s3"),
                      dict(id="b", text="Masofaviy kirish beraman", points=0, next="s3"),
                  ]),
             dict(id="s2bad", sub="c4.3",
                  text="Yaratilgan VPN hisobi orqali xorijiy IP dan ulanish va ichki tarmoqni skanerlash aniqlandi.",
                  options=[
                      dict(id="a", text="Hisobni darhol o‘chiraman, loglarni tahlil qilib, Cert.uz ga xabar beraman",
                           points=5, next="s3"),
                      dict(id="b", text="Kuzatib turaman", points=1, next="s3"),
                  ]),
             dict(id="s3", sub="c4.3",
                  text="Xodimlarning ijtimoiy muhandislikka bardoshliligini oshirish uchun nima qilasiz?",
                  options=[
                      dict(id="a", text="Test-fishing kampaniyasi, qisqa amaliy yo‘riqnoma va shubhali so‘rovlar "
                                        "haqida xabar berish tartibini joriy etaman", points=10, next=None),
                      dict(id="b", text="Barcha xodimlarga umumiy ogohlantirish xati yuboraman", points=4, next=None),
                      dict(id="c", text="Hech narsa qilmayman", points=0, next=None),
                  ]),
         ]),
]
