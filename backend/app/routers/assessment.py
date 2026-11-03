from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import IctOfficer, QuestionItem
from app.security import current_user
from app.services import lab_sim
from app.services.grader import SubAccumulator, grade_cases, grade_labs, grade_tests
from app.services.scoring_engine import BLOCKS, domain_score
from app.services.sessions import persist_evaluation

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


def _items(db: Session, kind: str) -> list[QuestionItem]:
    return list(db.scalars(select(QuestionItem).where(QuestionItem.kind == kind).order_by(QuestionItem.order)))


@router.get("/content")
def content(db: Session = Depends(get_db), _: IctOfficer = Depends(current_user)):
    return {
        "weights": {"alpha": 0.30, "beta": 0.40, "gamma": 0.30},
        "tests": [{"code": t.code, "block": t.block_code, "sub": t.sub_code, **t.payload_json}
                  for t in _items(db, "test")],
        "labs": [{"code": t.code, "block": t.block_code, "title": t.title, **t.payload_json}
                 for t in _items(db, "lab")],
        "cases": [{"code": t.code, "block": t.block_code, "title": t.title, **t.payload_json}
                  for t in _items(db, "case")],
    }


class ExecIn(BaseModel):
    history: list[str] = Field(default_factory=list, max_length=lab_sim.MAX_COMMANDS)
    command: str = Field(max_length=lab_sim.MAX_COMMAND_LEN)


@router.post("/labs/{code}/exec")
def lab_exec(code: str, body: ExecIn, db: Session = Depends(get_db), _: IctOfficer = Depends(current_user)):
    lab = db.scalar(select(QuestionItem).where(QuestionItem.code == code, QuestionItem.kind == "lab"))
    if lab is None or "engine" not in lab.answer_json:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Terminal laboratoriyasi topilmadi")
    try:
        output = lab_sim.execute(lab.answer_json["engine"], body.history, body.command)
    except ValueError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
    return {"output": output}


class SubmitIn(BaseModel):
    officer_id: int | None = None
    duration_seconds: float = Field(default=0, ge=0, le=6 * 3600)
    tests: dict[str, int] = Field(default_factory=dict)
    labs: dict[str, dict] = Field(default_factory=dict)
    cases: dict[str, list[dict]] = Field(default_factory=dict)


@router.post("/submit")
def submit(body: SubmitIn, db: Session = Depends(get_db), user: IctOfficer = Depends(current_user)):
    target = user
    if body.officer_id is not None and body.officer_id != user.id:
        if user.role != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat komissiya boshqa xodimni baholay oladi")
        target = db.get(IctOfficer, body.officer_id)
        if target is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Xodim topilmadi")

    subs = SubAccumulator()
    k, test_details = grade_tests(_items(db, "test"), body.tests, subs)
    s, lab_details = grade_labs(_items(db, "lab"), body.labs, subs)
    a, case_details = grade_cases(_items(db, "case"), body.cases, subs)
    c_preview = {b: domain_score(k[b], s[b], a[b]) for b in BLOCKS}

    sess = persist_evaluation(
        db, target, k, s, a, subs.result(c_preview), stage="attestatsiya",
        duration_minutes=round(body.duration_seconds / 60, 1),
        details={"tests": test_details, "labs": lab_details, "cases": case_details,
                 "lab_inputs": {code: v for code, v in body.labs.items() if isinstance(v, dict)}},
    )
    db.commit()
    return {"session_id": sess.id, "officer_id": target.id, "i_axk": sess.i_axk, "level": sess.level_name}
