"""Juftlangan Student t-testi (scipy'siz, NumPy va to‘liqsiz beta funksiya orqali)."""
from __future__ import annotations

import math

import numpy as np


def _betacf(a: float, b: float, x: float) -> float:
    max_iter, eps, fpmin = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > fpmin else fpmin)
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > fpmin else fpmin)
        c = 1.0 + aa / c
        c = c if abs(c) > fpmin else fpmin
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > fpmin else fpmin)
        c = 1.0 + aa / c
        c = c if abs(c) > fpmin else fpmin
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t: float, df: int) -> float:
    return _betai(df / 2.0, 0.5, df / (df + t * t))


def paired_t_test(before: list[float], after: list[float]) -> dict:
    x = np.asarray(before, dtype=float)
    y = np.asarray(after, dtype=float)
    if x.size != y.size or x.size < 2:
        raise ValueError("Juftlangan tanlamalar bir xil uzunlikda va n >= 2 bo‘lishi kerak")
    d = y - x
    n = int(d.size)
    mean_d = float(d.mean())
    sd_d = float(d.std(ddof=1))
    t = mean_d / (sd_d / math.sqrt(n)) if sd_d > 0 else float("inf")
    p = t_two_sided_p(t, n - 1) if math.isfinite(t) else 0.0
    mb, ma = float(x.mean()), float(y.mean())
    return {
        "n": n,
        "before_mean": mb,
        "before_sd": float(x.std(ddof=1)),
        "after_mean": ma,
        "after_sd": float(y.std(ddof=1)),
        "delta": ma - mb,
        "delta_pct": (ma - mb) / mb * 100 if mb else 0.0,
        "sd_diff": sd_d,
        "t": t,
        "df": n - 1,
        "p": p,
    }
