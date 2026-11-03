"""CyberComp-Gov baholash yadrosi (dissertatsiya II bob modeli).

Formulalar:
    C_i   = alpha*K_i + beta*S_i + gamma*A_i            (alpha=0.30, beta=0.40, gamma=0.30)
    I_AXK = sum(w_i * C_i)                               (w = AHP vaznlari)
    Phi   = 1, agar C2 >= 50 va C3 >= 50, aks holda 0    (kompensatsiyalanmaydigan chegara)
    dC_i  = max(0, C_norm - C_i)                         (C_norm = 80 oddiy, 85 MII)

Dissertatsiyadagi 2.4-jadval qiymatlari bilan moslik uchun C_i butun ballgacha
yaxlitlanadi (ROUND_HALF_UP), I_AXK esa 2 xona aniqlikda hisoblanadi.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

import numpy as np

BLOCKS = ("C1", "C2", "C3", "C4")
DEFAULT_WEIGHTS = {"C1": 0.20, "C2": 0.35, "C3": 0.25, "C4": 0.20}
ALPHA, BETA, GAMMA = 0.30, 0.40, 0.30
C_MIN = 50.0
CRITICAL_BLOCKS = ("C2", "C3")
NORM_REGULAR = 80.0
NORM_MII = 85.0
GAP_TRIGGER = 15.0
DOMAIN_PRECISION = 0  # C_i butun ballgacha

# Saaty tasodifiy izchillik indekslari (RI_n)
RANDOM_INDEX = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}

THESIS_AHP_MATRIX = [
    [1.0, 4 / 7, 4 / 5, 1.0],
    [7 / 4, 1.0, 7 / 5, 7 / 4],
    [5 / 4, 5 / 7, 1.0, 5 / 4],
    [1.0, 4 / 7, 4 / 5, 1.0],
]

LEVEL_CRITICAL = "Kritik (Boshlang‘ich) daraja"
LEVEL_CONDITIONAL = "Shartli bazaviy (Kritik blok oqsagan)"
LEVEL_BASIC = "Bazaviy (Rivojlanayotgan) daraja"
LEVEL_QUALIFIED = "Malakali (Yetarli) daraja"
LEVEL_EXPERT = "Ekspert (Yuqori) daraja"

LEVELS = [LEVEL_CRITICAL, LEVEL_CONDITIONAL, LEVEL_BASIC, LEVEL_QUALIFIED, LEVEL_EXPERT]

DECISIONS = {
    LEVEL_CRITICAL: "Lavozimga nomuvofiq; mustaqil administrator huquqlarini cheklash va to‘liq bazaviy kursga yuborish.",
    LEVEL_CONDITIONAL: "Kritik texnik (C2) yoki insident (C3) bloki 50 balldan past; 1 oy muddatda maqsadli qayta tayyorlash va qayta imtihon.",
    LEVEL_BASIC: "Shartli muvofiq; bo‘shliq aniqlangan bloklar bo‘yicha amaliy trening va mentor biriktirish.",
    LEVEL_QUALIFIED: "Davlat organi AKT va axborot xavfsizligi mas’ul xodimi lavozimiga to‘liq muvofiq.",
    LEVEL_EXPERT: "Muhim axborot infratuzilmasi (MII) obyektlariga rahbarlik qilish va ichki trener sifatida jalb etish.",
}


def round_half_up(value: float, digits: int = 0) -> float:
    q = Decimal(1).scaleb(-digits)
    return float(Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------- AHP (Saaty)

@dataclass
class AHPResult:
    matrix: list[list[float]]
    geometric_means: list[float]
    weights: list[float]
    lambda_max: float
    ci: float
    cr: float
    ri: float
    consistent: bool


def compute_ahp_weights(matrix: list[list[float]] | None = None) -> AHPResult:
    """Geometrik o‘rtacha usuli bilan ustuvorlik vektori va izchillik ko‘rsatkichlari."""
    a = np.array(matrix if matrix is not None else THESIS_AHP_MATRIX, dtype=float)
    n = a.shape[0]
    if a.ndim != 2 or a.shape[1] != n:
        raise ValueError("Matritsa kvadrat bo‘lishi kerak")
    if np.any(a <= 0):
        raise ValueError("Matritsa elementlari musbat bo‘lishi kerak")

    g = np.prod(a, axis=1) ** (1.0 / n)
    w = g / g.sum()
    # lambda_max: (A·w)_p / w_p o‘rtachasi (Saaty bahosi)
    lambda_max = float(np.mean((a @ w) / w))
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    ri = RANDOM_INDEX.get(n, 1.49)
    cr = ci / ri if ri > 0 else 0.0
    # sonli shovqin tufayli -1e-16 kabi qiymatlarni nolga keltiramiz
    ci = max(ci, 0.0) if abs(ci) < 1e-12 else ci
    cr = max(cr, 0.0) if abs(cr) < 1e-12 else cr
    return AHPResult(
        matrix=a.tolist(),
        geometric_means=g.tolist(),
        weights=w.tolist(),
        lambda_max=lambda_max,
        ci=ci,
        cr=cr,
        ri=ri,
        consistent=cr < 0.10,
    )


# ------------------------------------------------------------ Domen va indeks

def domain_score(k: float, s: float, a: float,
                 alpha: float = ALPHA, beta: float = BETA, gamma: float = GAMMA) -> float:
    for v in (k, s, a):
        if not 0 <= v <= 100:
            raise ValueError("K, S, A qiymatlari [0, 100] oralig‘ida bo‘lishi kerak")
    return round_half_up(alpha * k + beta * s + gamma * a, DOMAIN_PRECISION)


def integral_index(c: dict[str, float], weights: dict[str, float] | None = None) -> float:
    w = weights or DEFAULT_WEIGHTS
    return round_half_up(sum(w[b] * c[b] for b in BLOCKS), 2)


def phi_flag(c: dict[str, float], c_min: float = C_MIN) -> int:
    return int(all(c[b] >= c_min for b in CRITICAL_BLOCKS))


def classify(i_axk: float, phi: int) -> str:
    if i_axk < 55.0:
        return LEVEL_CRITICAL
    if phi == 0:
        # 55 <= I_AXK; kritik blok oqsagan. I_AXK > 85 bo‘lsa ham ekspert maqomi berilmaydi.
        return LEVEL_CONDITIONAL
    if i_axk < 71.0:
        return LEVEL_BASIC
    if i_axk < 86.0:
        return LEVEL_QUALIFIED
    return LEVEL_EXPERT


def skill_gaps(c: dict[str, float], norm: float = NORM_REGULAR) -> dict[str, float]:
    return {b: round_half_up(max(0.0, norm - c[b]), 2) for b in BLOCKS}


def failed_critical_blocks(c: dict[str, float], c_min: float = C_MIN) -> list[str]:
    return [b for b in CRITICAL_BLOCKS if c[b] < c_min]


@dataclass
class Evaluation:
    k: dict[str, float]
    s: dict[str, float]
    a: dict[str, float]
    c: dict[str, float]
    i_axk: float
    phi: int
    level: str
    decision: str
    norm: float
    gaps: dict[str, float]
    failed_blocks: list[str] = field(default_factory=list)
    gap_blocks: list[str] = field(default_factory=list)


def evaluate(k: dict[str, float], s: dict[str, float], a: dict[str, float],
             norm: float = NORM_REGULAR, weights: dict[str, float] | None = None) -> Evaluation:
    c = {b: domain_score(k[b], s[b], a[b]) for b in BLOCKS}
    i = integral_index(c, weights)
    phi = phi_flag(c)
    level = classify(i, phi)
    gaps = skill_gaps(c, norm)
    return Evaluation(
        k=dict(k), s=dict(s), a=dict(a), c=c, i_axk=i, phi=phi, level=level,
        decision=DECISIONS[level], norm=norm, gaps=gaps,
        failed_blocks=failed_critical_blocks(c),
        gap_blocks=[b for b in BLOCKS if gaps[b] > GAP_TRIGGER],
    )


def norm_for_category(category: str) -> float:
    return NORM_MII if category == "MII" else NORM_REGULAR
