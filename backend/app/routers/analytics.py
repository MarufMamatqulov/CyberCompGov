from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import EvalSession, IctOfficer
from app.security import require_leadership
from app.services.scoring_engine import LEVELS, LEVEL_EXPERT, LEVEL_QUALIFIED
from app.services.stats import paired_t_test

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# An’anaviy (qog‘oz/og‘zaki) attestatsiyaning o‘rtacha davomiyligi, daqiqa — dissertatsiya 3-bob
TRADITIONAL_MINUTES = 120.0

GROUP_LABELS = {"ministry": "Vazirlik markaziy apparati", "regional": "Viloyat boshqarmalari",
                "district": "Tuman hokimliklari"}
INDICATORS = [("C1", "c1_score"), ("C2", "c2_score"), ("C3", "c3_score"), ("C4", "c4_score"), ("I_AXK", "i_axk")]


def _r(x: float, d: int = 2) -> float:
    return round(x, d)


@router.get("/experiment")
def experiment(db: Session = Depends(get_db), _: IctOfficer = Depends(require_leadership)):
    officers = db.scalars(select(IctOfficer).where(IctOfficer.role == "officer")
                          .options(selectinload(IctOfficer.sessions))).all()
    pairs = []
    for o in officers:
        st = {s.stage: s for s in o.sessions}
        if "before" in st and "after" in st:
            pairs.append((o, st["before"], st["after"]))
    n = len(pairs)
    if n < 2:
        return {"n": n, "table": [], "levels": [], "groups": [], "kpi": {}}

    table = []
    for label, attr in INDICATORS:
        res = paired_t_test([getattr(b, attr) for _, b, _ in pairs], [getattr(a, attr) for _, _, a in pairs])
        table.append({"indicator": label, **{k: (_r(v, 3) if k in ("t",) else v) for k, v in res.items()}})

    def dist(idx: int) -> list[int]:
        counts = [0] * len(LEVELS)
        for p in pairs:
            counts[LEVELS.index(p[idx].level_name)] += 1
        return counts

    before_c, after_c = dist(1), dist(2)
    levels = [{"level": lvl, "before": before_c[i], "after": after_c[i],
               "before_pct": before_c[i] / n * 100, "after_pct": after_c[i] / n * 100}
              for i, lvl in enumerate(LEVELS)]

    groups = []
    for key, label in GROUP_LABELS.items():
        g = [p for p in pairs if p[0].group == key]
        if not g:
            continue
        groups.append({"group": key, "label": label, "n": len(g),
                       "before": sum(p[1].i_axk for p in g) / len(g), "after": sum(p[2].i_axk for p in g) / len(g)})

    good = (LEVELS.index(LEVEL_QUALIFIED), LEVELS.index(LEVEL_EXPERT))
    all_sessions = db.scalars(select(EvalSession)).all()
    avg_minutes = sum(s.duration_minutes for s in all_sessions) / len(all_sessions)
    i_row = table[-1]
    kpi = {
        "n": n,
        "i_before": i_row["before_mean"], "i_after": i_row["after_mean"],
        "i_delta": i_row["delta"], "i_delta_pct": i_row["delta_pct"],
        "qualified_before_pct": sum(before_c[i] for i in good) / n * 100,
        "qualified_after_pct": sum(after_c[i] for i in good) / n * 100,
        "avg_minutes": avg_minutes, "traditional_minutes": TRADITIONAL_MINUTES,
        "speedup": TRADITIONAL_MINUTES / avg_minutes if avg_minutes else None,
        "phi_fail_before": sum(1 for p in pairs if p[1].phi_flag == 0),
        "phi_fail_after": sum(1 for p in pairs if p[2].phi_flag == 0),
        "total_sessions": len(all_sessions),
    }
    return {"n": n, "table": table, "levels": levels, "groups": groups, "kpi": kpi}
