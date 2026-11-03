"""3.3-jadvalga mos eksperimental tanlama (n=45) generatori.

Ishga tushirish (faqat ma’lumotlarni qayta yaratish kerak bo‘lganda):
    python -m app.seed.generate_experiment

Natija: app/seed/experiment_officers.json (repoda saqlanadi, seed.py uni o‘qiydi).
Tanlama deterministik (random.seed) va quyidagi cheklovlarni aniq qanoatlantiradi:
  * oldin:  C1=61.4, C2=53.8, C3=48.2, C4=64.5, I_AXK=56.1
  * keyin:  C1=81.2, C2=78.6, C3=74.8, C4=83.4, I_AXK=79.1
  * juftlangan t = 14.82 (df=44), Malakali+Ekspert ulushi 20.0% -> 68.9%
  * e1, e2, e3 xodimlarining "oldin" qiymatlari 2.4-jadvaldagidek
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from app.services.scoring_engine import BLOCKS, evaluate
from app.services.stats import paired_t_test

OUT = Path(__file__).with_name("experiment_officers.json")
N = 45
SEED = 20260515

TARGET_SUMS = {
    # yig‘indilar o‘rtachalarning yaxlitlash oralig‘ida tanlangan: I_AXK 56.10 -> 79.09 (+22.99; +40.98%)
    "before": {"C1": 2765, "C2": 2423, "C3": 2171, "C4": 2904},
    "after": {"C1": 3652, "C2": 3535, "C3": 3364, "C4": 3751},
}
TARGET_T = 14.82
# daraja taqsimoti: Kritik, Shartli, Bazaviy, Malakali, Ekspert
TARGET_LEVELS = {"before": [20, 10, 6, 9, 0], "after": [0, 3, 11, 24, 7]}

NAMED = {
    0: ("e1", {"C1": (88, 82, 83), "C2": (80, 85, 77), "C3": (78, 75, 75), "C4": (85, 80, 82)},
        {"C1": 90, "C2": 88, "C3": 85, "C4": 89}),
    15: ("e2", {"C1": (80, 70, 67), "C2": (70, 60, 53), "C3": (60, 40, 33), "C4": (80, 75, 70)},
         {"C1": 82, "C2": 78, "C3": 75, "C4": 84}),
    30: ("e3", {"C1": (60, 50, 47), "C2": (52, 45, 41), "C3": (48, 40, 35), "C4": (65, 55, 55)},
         {"C1": 72, "C2": 70, "C3": 66, "C4": 76}),
}

FIRST = ["Aziz", "Bobur", "Dilshod", "Elyor", "Farrux", "G‘ayrat", "Hasan", "Ilhom", "Javohir", "Kamol",
         "Laziz", "Mansur", "Nodir", "Otabek", "Po‘lat", "Rustam", "Sanjar", "Temur", "Ulug‘bek", "Valijon",
         "Xurshid", "Yusuf", "Zafar", "Shoxrux", "Sherzod", "Nilufar", "Dilnoza", "Gulnora", "Madina", "Zarina",
         "Shahlo", "Malika", "Feruza", "Sevara", "Kamola", "Umida", "Nargiza", "Lola", "Barno", "Muxlisa",
         "Akmal", "Jahongir"]
LAST_M = ["Abdullayev", "Botirov", "Davronov", "Ergashev", "Fayziyev", "G‘aniyev", "Hamidov", "Ismoilov",
          "Jo‘rayev", "Komilov", "Latipov", "Mirzayev", "Nazarov", "Olimov", "Qodirov", "Rahimov", "Sobirov",
          "Toshpo‘latov", "Usmonov", "Valiyev", "Xolmatov", "Yo‘ldoshev", "Zokirov", "Sharipov", "Tursunov"]

GROUPS = [
    ("ministry", "Vazirlik markaziy apparati", [
        "AKT bosh mutaxassisi", "Axborot xavfsizligi bo‘limi yetakchi mutaxassisi", "Tizim ma’muri",
        "Raqamlashtirish bo‘limi boshlig‘i o‘rinbosari", "Tarmoq muhandisi"]),
    ("regional", "Viloyat boshqarmasi", [
        "Tarmoq ma’muri", "AKT bo‘limi bosh mutaxassisi", "Axborot xavfsizligi mutaxassisi",
        "Tizim ma’muri", "Raqamlashtirish sektori mudiri"]),
    ("district", "Tuman hokimligi", [
        "AKT mas’ul xodimi", "Kompyuter tarmoqlari mutaxassisi", "Raqamlashtirish bo‘yicha mas’ul",
        "Texnik xizmat ko‘rsatish mutaxassisi", "Axborot tizimlari operatori"]),
]

AGENCIES = [
    # (kalit, nomi, toifa, hudud)
    ("min-1", "Vazirlik markaziy apparati (A)", "Oddiy", "Toshkent shahri"),
    ("min-2", "Vazirlik markaziy apparati (B)", "Oddiy", "Toshkent shahri"),
    ("min-3", "Qo‘mita markaziy apparati (C) — MII obyekti", "MII", "Toshkent shahri"),
    ("reg-1", "Samarqand viloyati boshqarmasi", "Oddiy", "Samarqand viloyati"),
    ("reg-2", "Farg‘ona viloyati boshqarmasi", "Oddiy", "Farg‘ona viloyati"),
    ("reg-3", "Qashqadaryo viloyati boshqarmasi — MII obyekti", "MII", "Qashqadaryo viloyati"),
    ("dis-1", "Urgut tumani hokimligi", "Oddiy", "Samarqand viloyati"),
    ("dis-2", "Qo‘qon tumani hokimligi", "Oddiy", "Farg‘ona viloyati"),
    ("dis-3", "Shahrisabz tumani hokimligi", "Oddiy", "Qashqadaryo viloyati"),
]


def level_index(c: dict[str, int]) -> int:
    i = 0.20 * c["C1"] + 0.35 * c["C2"] + 0.25 * c["C3"] + 0.20 * c["C4"]
    if i < 55.0 - 1e-9:
        return 0
    if c["C2"] < 50 or c["C3"] < 50:
        return 1
    if i < 71.0 - 1e-9:
        return 2
    if i < 86.0 - 1e-9:
        return 3
    return 4


def i_of(c):
    return 0.20 * c["C1"] + 0.35 * c["C2"] + 0.25 * c["C3"] + 0.20 * c["C4"]


class State:
    """Agregatlar (yig‘indilar, daraja soni, sum d, sum d^2) inkremental yangilanadi."""

    def __init__(self, data):
        self.data = data
        self.sums = {st: {b: sum(o[st][b] for o in data) for b in BLOCKS} for st in ("before", "after")}
        self.counts = {st: [0] * 5 for st in ("before", "after")}
        self.levels = []
        self.sd = 0.0
        self.sd2 = 0.0
        self.viol = 0
        for o in data:
            lv = {st: level_index(o[st]) for st in ("before", "after")}
            self.levels.append(lv)
            for st in lv:
                self.counts[st][lv[st]] += 1
            d = i_of(o["after"]) - i_of(o["before"])
            self.sd += d
            self.sd2 += d * d
            self.viol += sum(o["after"][b] < o["before"][b] + 1 for b in BLOCKS)

    def remove(self, i):
        o = self.data[i]
        for st in ("before", "after"):
            self.counts[st][self.levels[i][st]] -= 1
        d = i_of(o["after"]) - i_of(o["before"])
        self.sd -= d
        self.sd2 -= d * d
        self.viol -= sum(o["after"][b] < o["before"][b] + 1 for b in BLOCKS)

    def add(self, i):
        o = self.data[i]
        lv = {st: level_index(o[st]) for st in ("before", "after")}
        self.levels[i] = lv
        for st in lv:
            self.counts[st][lv[st]] += 1
        d = i_of(o["after"]) - i_of(o["before"])
        self.sd += d
        self.sd2 += d * d
        self.viol += sum(o["after"][b] < o["before"][b] + 1 for b in BLOCKS)

    def t(self):
        n = len(self.data)
        mean = self.sd / n
        var = (self.sd2 - n * mean * mean) / (n - 1)
        return mean / math.sqrt(var / n) if var > 0 else 1e9

    def cost(self):
        c = 0.0
        for st in ("before", "after"):
            for b in BLOCKS:
                c += 50.0 * abs(self.sums[st][b] - TARGET_SUMS[st][b])
            c += 20.0 * sum(abs(x - y) for x, y in zip(self.counts[st], TARGET_LEVELS[st]))
        c += 400.0 * max(0.0, abs(self.t() - TARGET_T) - 0.003)
        c += 5.0 * self.viol
        return c


def initial(rng: random.Random):
    base_before = {"C1": 61.4, "C2": 53.8, "C3": 48.2, "C4": 64.5}
    base_after = {"C1": 81.2, "C2": 78.6, "C3": 74.8, "C4": 83.4}
    data = []
    for i in range(N):
        if i in NAMED:
            _, ksa, after = NAMED[i]
            from app.services.scoring_engine import domain_score
            before = {b: int(domain_score(*ksa[b])) for b in BLOCKS}
            data.append({"before": before, "after": dict(after), "fixed": True})
            continue
        ab = rng.gauss(0, 9)
        gain = rng.gauss(0, 7)
        before = {b: int(round(min(88, max(25, base_before[b] + ab + rng.gauss(0, 4))))) for b in BLOCKS}
        after = {b: int(round(min(98, max(before[b] + 4, base_after[b] + ab * 0.6 + gain + rng.gauss(0, 3)))))
                 for b in BLOCKS}
        data.append({"before": before, "after": after, "fixed": False})
    return data


def optimise(rng: random.Random, data):
    free = [i for i, o in enumerate(data) if not o["fixed"]]
    st = State(data)
    cost = st.cost()
    temp = 8.0
    for step in range(1_500_000):
        if cost == 0:
            break
        i = rng.choice(free)
        stage = rng.choice(("before", "after"))
        b = rng.choice(BLOCKS)
        delta = rng.choice((-1, 1)) * rng.choice((1, 1, 2, 3))
        old = data[i][stage][b]
        new = old + delta
        if not 20 <= new <= 99:
            continue
        # juft o‘zgarish: yig‘indini saqlash uchun boshqa xodimda teskari qadam
        j = rng.choice(free) if rng.random() < 0.7 else None
        if j == i or (j is not None and not 20 <= data[j][stage][b] - delta <= 99):
            j = None
        st.remove(i)
        data[i][stage][b] = new
        st.add(i)
        st.sums[stage][b] += delta
        if j is not None:
            st.remove(j)
            data[j][stage][b] -= delta
            st.add(j)
            st.sums[stage][b] -= delta
        nc = st.cost()
        if nc <= cost or rng.random() < math.exp((cost - nc) / max(temp, 1e-3)):
            cost = nc
        else:
            st.remove(i)
            data[i][stage][b] = old
            st.add(i)
            st.sums[stage][b] -= delta
            if j is not None:
                st.remove(j)
                data[j][stage][b] += delta
                st.add(j)
                st.sums[stage][b] += delta
        temp = max(0.05, temp * 0.99999)
    return cost


def decompose(rng: random.Random, c: int) -> tuple[int, int, int]:
    """C ni K, S, A ga ajratish: 0.3K + 0.4S + 0.3A = C aniq bajariladi."""
    from app.services.scoring_engine import domain_score
    for _ in range(50):
        m = rng.randint(0, 3)
        d = rng.randint(-5, 7)
        k, s, a = c + 4 * m + d, c - 3 * m, c - d
        if all(0 <= v <= 100 for v in (k, s, a)) and domain_score(k, s, a) == c:
            return k, s, a
    return c, c, c


def sub_scores(rng: random.Random, c: int) -> list[int]:
    offs = [rng.randint(-9, 9) for _ in range(2)]
    offs.append(-sum(offs))
    rng.shuffle(offs)
    return [max(0, min(100, c + o)) for o in offs]


def main():
    for seed in range(SEED, SEED + 20):
        rng = random.Random(seed)
        data = initial(rng)
        cost = optimise(rng, data)
        print(f"seed={seed} cost={cost}")
        if cost == 0:
            break
    else:
        raise SystemExit("Cheklovlar to‘liq qanoatlantirilmadi")

    names_rng = random.Random(SEED + 1)
    used = set()
    officers = []
    for i, o in enumerate(data):
        g_idx = i // 15
        group_key, _, positions = GROUPS[g_idx]
        agency_key = AGENCIES[g_idx * 3 + (i % 3)][0]
        if i in NAMED:
            key, ksa, _ = NAMED[i]
            meta = {
                "e1": ("Aliyev Jamshid", "Vazirlik markaziy apparati AKT bosh mutaxassisi", "min-1", 9),
                "e2": ("Karimov Sardor", "Viloyat boshqarmasi tarmoq ma’muri", "reg-1", 5),
                "e3": ("Rustamov Bekzod", "Tuman hokimligi AKT mas’ul xodimi", "dis-1", 2),
            }[key]
            full_name, position, agency_key, exp = meta
            username = key
            before_ksa = {b: list(ksa[b]) for b in BLOCKS}
        else:
            while True:
                fn = names_rng.choice(FIRST)
                ln = names_rng.choice(LAST_M)
                if fn in ("Nilufar", "Dilnoza", "Gulnora", "Madina", "Zarina", "Shahlo", "Malika", "Feruza",
                          "Sevara", "Kamola", "Umida", "Nargiza", "Lola", "Barno", "Muxlisa"):
                    ln = ln[:-2] + "eva" if ln.endswith("ev") else ln + "a"
                full_name = f"{ln} {fn}"
                if full_name not in used:
                    break
            position = names_rng.choice(positions)
            exp = names_rng.randint(1, 15)
            username = f"x{i + 1:02d}"
            before_ksa = {b: list(decompose(rng, o["before"][b])) for b in BLOCKS}
        used.add(full_name)
        after_ksa = {b: list(decompose(rng, o["after"][b])) for b in BLOCKS}
        pinfl = f"3{(10 ** 12 + i * 7919 + 1234567) % 10 ** 13:013d}"
        officers.append({
            "index": i + 1,
            "username": username,
            "full_name": full_name,
            "position": position,
            "group": group_key,
            "agency": agency_key,
            "experience_years": exp,
            "pinfl": pinfl,
            "sessions": {
                stage: {
                    "ksa": ksa_map,
                    "sub_scores": {b: sub_scores(rng, o[stage][b]) for b in BLOCKS},
                    "duration_minutes": 35 + (i % 11) - 5,
                }
                for stage, ksa_map in (("before", before_ksa), ("after", after_ksa))
            },
        })

    # yakuniy tekshiruv
    bi, ai = [], []
    for off in officers:
        ev = {st: evaluate(*(
            {b: off["sessions"][st]["ksa"][b][n] for b in BLOCKS} for n in range(3))) for st in ("before", "after")}
        bi.append(ev["before"].i_axk)
        ai.append(ev["after"].i_axk)
    res = paired_t_test(bi, ai)
    print(f"oldin={res['before_mean']:.2f} keyin={res['after_mean']:.2f} t={res['t']:.3f} p={res['p']:.2e}")

    OUT.write_text(json.dumps({"agencies": AGENCIES, "officers": officers}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"Yozildi: {OUT}")


if __name__ == "__main__":
    main()
