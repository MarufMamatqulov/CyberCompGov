import secrets
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import EvalSession, IctOfficer, SkillGapPlan
from app.services.grader import build_training_plan
from app.services.scoring_engine import evaluate, norm_for_category


def persist_evaluation(db: Session, officer: IctOfficer, k: dict, s: dict, a: dict, sub_scores: dict | None,
                       stage: str, duration_minutes: float, details: dict | None = None,
                       created_at: datetime | None = None) -> EvalSession:
    norm = norm_for_category(officer.agency.category)
    ev = evaluate(k, s, a, norm=norm)
    subs = sub_scores or {b: [ev.c[b]] * 3 for b in ev.c}
    sess = EvalSession(
        verify_code=secrets.token_hex(8).upper(),
        officer=officer,
        duration_minutes=duration_minutes,
        k_scores_json=ev.k, s_scores_json=ev.s, a_scores_json=ev.a,
        sub_scores_json=subs,
        details_json=details or {},
        c1_score=ev.c["C1"], c2_score=ev.c["C2"], c3_score=ev.c["C3"], c4_score=ev.c["C4"],
        i_axk=ev.i_axk, phi_flag=ev.phi, level_name=ev.level, decision_text=ev.decision,
        norm_threshold=norm, stage=stage,
    )
    if created_at is not None:
        sess.created_at = created_at
    for item in build_training_plan(ev, subs):
        sess.gaps.append(SkillGapPlan(**item))
    db.add(sess)
    return sess
