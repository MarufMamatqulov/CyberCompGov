from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import EvalSession, IctOfficer
from app.security import current_user, ensure_can_view, require_leadership
from app.services.scoring_engine import BLOCKS, C_MIN, DEFAULT_WEIGHTS, GAP_TRIGGER

router = APIRouter(prefix="/api/officers", tags=["officers"])

STAGE_LABELS = {"before": "O‘qitishdan oldin", "after": "O‘qitishdan keyin", "attestatsiya": "Attestatsiya"}


def session_summary(s: EvalSession) -> dict:
    return {
        "id": s.id, "stage": s.stage, "stage_label": STAGE_LABELS.get(s.stage, s.stage),
        "created_at": s.created_at.isoformat(), "i_axk": s.i_axk, "phi": s.phi_flag, "level": s.level_name,
        "c": {"C1": s.c1_score, "C2": s.c2_score, "C3": s.c3_score, "C4": s.c4_score},
        "duration_minutes": s.duration_minutes,
    }


def session_full(s: EvalSession) -> dict:
    out = session_summary(s)
    c = out["c"]
    out.update({
        "verify_code": s.verify_code,
        "k": s.k_scores_json, "s": s.s_scores_json, "a": s.a_scores_json, "sub_scores": s.sub_scores_json,
        "norm": s.norm_threshold, "decision": s.decision_text,
        "gaps": {b: max(0.0, s.norm_threshold - c[b]) for b in BLOCKS},
        "failed_blocks": [b for b in ("C2", "C3") if c[b] < C_MIN],
        "plan": [{"id": g.id, "block_code": g.block_code, "sub_code": g.sub_code, "delta_c": g.delta_c,
                  "title": g.assigned_course_title, "hours": g.course_hours, "deadline_days": g.deadline_days,
                  "status": g.status} for g in s.gaps],
        "details": s.details_json,
        "weights": DEFAULT_WEIGHTS, "gap_trigger": GAP_TRIGGER,
    })
    return out


def officer_out(o: IctOfficer) -> dict:
    return {"id": o.id, "full_name": o.full_name, "username": o.username, "pinfl": o.pinfl, "position": o.position,
            "group": o.group, "experience_years": o.experience_years, "role": o.role,
            "agency": {"id": o.agency.id, "name": o.agency.name, "category": o.agency.category,
                       "region": o.agency.region, "norm_threshold": o.agency.norm_threshold}}


@router.get("")
def list_officers(search: str = "", group: str = "", level: str = "", db: Session = Depends(get_db),
                  user: IctOfficer = Depends(require_leadership)):
    q = (select(IctOfficer).where(IctOfficer.role == "officer")
         .options(selectinload(IctOfficer.sessions), selectinload(IctOfficer.agency)).order_by(IctOfficer.id))
    if user.role == "supervisor":
        q = q.where(IctOfficer.agency_id == user.agency_id)
    rows = []
    needle = search.strip().lower()
    for o in db.scalars(q).all():
        if needle and needle not in f"{o.full_name} {o.username} {o.pinfl} {o.position} {o.agency.name}".lower():
            continue
        if group and o.group != group:
            continue
        by_stage = {}
        for s in o.sessions:
            by_stage[s.stage] = s  # sessiyalar vaqt bo‘yicha tartiblangan — oxirgisi qoladi
        latest = o.sessions[-1] if o.sessions else None
        if level and (latest is None or latest.level_name != level):
            continue
        rows.append({
            **officer_out(o),
            "before": session_summary(by_stage["before"]) if "before" in by_stage else None,
            "after": session_summary(by_stage["after"]) if "after" in by_stage else None,
            "latest": session_summary(latest) if latest else None,
        })
    return rows


@router.get("/{officer_id}/passport")
def passport(officer_id: int, session_id: int | None = Query(default=None), db: Session = Depends(get_db),
             user: IctOfficer = Depends(current_user)):
    ensure_can_view(user, officer_id, db)
    o = db.get(IctOfficer, officer_id)
    if o is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Xodim topilmadi")
    sessions = list(o.sessions)
    selected = None
    if session_id is not None:
        selected = next((s for s in sessions if s.id == session_id), None)
        if selected is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Baholash sessiyasi topilmadi")
    elif sessions:
        # Jonli attestatsiya bo‘lsa — oxirgisi; aks holda diagnostik (o‘qitishdan oldingi) baholash
        live = [s for s in sessions if s.stage == "attestatsiya"]
        selected = live[-1] if live else next((s for s in sessions if s.stage == "before"), sessions[-1])
    compare = None
    if selected is not None:
        by_stage = {s.stage: s for s in sessions}
        if selected.stage == "before":
            compare = by_stage.get("after")
        elif selected.stage == "after":
            compare = by_stage.get("before")
        else:
            idx = sessions.index(selected)
            compare = sessions[idx - 1] if idx > 0 else None
    return {
        "officer": officer_out(o),
        "sessions": [session_summary(s) for s in sessions],
        "session": session_full(selected) if selected else None,
        "compare": session_summary(compare) if compare else None,
    }
