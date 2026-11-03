"""Ma’lumotlar bazasini yaratish va ma’lumotnomalar bilan to‘ldirish.

Ilova ishga tushganda avtomatik chaqiriladi (SEED_ON_STARTUP=true). Qo‘lda:
    python -m app.seed.seed            # bo‘sh bazani to‘ldirish
    python -m app.seed.seed --reset    # barcha jadvallarni qayta yaratish
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Agency, CompetencyBlock, IctOfficer, KsaIndicator, QuestionItem
from app.seed.catalog_data import BLOCKS, KSA
from app.seed.questions_data import CASES, LABS, TESTS
from app.security import hash_password
from app.services.scoring_engine import ALPHA, BETA, BLOCKS as BLOCK_CODES, GAMMA, NORM_MII, NORM_REGULAR
from app.services.sessions import persist_evaluation

EXPERIMENT_FILE = Path(__file__).with_name("experiment_officers.json")
BEFORE_DATE = datetime(2026, 3, 10, 10, 0, tzinfo=timezone.utc)
AFTER_DATE = datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc)


def seed_reference(db: Session) -> None:
    for b in BLOCKS:
        db.add(CompetencyBlock(code=b["code"], name=b["name"], ahp_weight=b["ahp_weight"], alpha_k=ALPHA,
                               beta_s=BETA, gamma_a=GAMMA, min_threshold=b["min_threshold"]))
    db.flush()
    for sub_code, sub_name, k, s, a, nist, ecsf, law in KSA:
        idx = sub_code[1:]
        db.add(KsaIndicator(block_code=f"C{sub_code[1]}", sub_code=sub_code, sub_name=sub_name,
                            k_code=f"K{idx}", k_desc=k, s_code=f"S{idx}", s_desc=s, a_code=f"A{idx}", a_desc=a,
                            nist_ref=nist, ecsf_ref=ecsf, law_ref=law))
    for order, t in enumerate(TESTS):
        db.add(QuestionItem(code=t["code"], kind="test", block_code=t["block"], sub_code=t["sub"], title=t["code"],
                            order=order, payload_json={"question": t["question"], "options": t["options"]},
                            answer_json={"correct": t["correct"], "explanation": t["explanation"]}))
    for order, lab in enumerate(LABS):
        db.add(QuestionItem(code=lab["code"], kind="lab", block_code=lab["block"], sub_code=lab["sub"],
                            title=lab["title"], order=order, payload_json=lab["payload"], answer_json=lab["answer"]))
    for order, case in enumerate(CASES):
        # Bosqich nomlari (masalan, "s2bad") javobga ishora qilmasligi uchun neytral identifikatorlar
        ids = {s["id"]: f"b{i + 1}" for i, s in enumerate(case["stages"])}
        stages = [{**s, "id": ids[s["id"]],
                   "options": [{**o, "next": ids.get(o["next"])} for o in s["options"]]} for s in case["stages"]]
        public = {
            "start": ids[case["start"]], "time_limit": case["time_limit"],
            "stages": [{"id": s["id"], "text": s["text"],
                        "options": [{"id": o["id"], "text": o["text"], "next": o["next"]} for o in s["options"]]}
                       for s in stages],
        }
        db.add(QuestionItem(code=case["code"], kind="case", block_code=case["block"], sub_code=case["sub"],
                            title=case["title"], order=order, payload_json=public,
                            answer_json={"start": ids[case["start"]], "stages": stages}))


def seed_people(db: Session) -> None:
    s = get_settings()
    data = json.loads(EXPERIMENT_FILE.read_text(encoding="utf-8"))
    agencies = {}
    for code, name, category, region in data["agencies"]:
        ag = Agency(code=code, name=name, category=category, region=region,
                    norm_threshold=NORM_MII if category == "MII" else NORM_REGULAR)
        db.add(ag)
        agencies[code] = ag
    hq = Agency(code="hq", name="Attestatsiya komissiyasi (Kiberxavfsizlik markazi)", category="Oddiy",
                region="Toshkent shahri", norm_threshold=NORM_REGULAR)
    db.add(hq)
    db.flush()

    db.add(IctOfficer(pinfl="30000000000001", full_name="Komissiya Raisi", position="Attestatsiya komissiyasi raisi",
                      agency=hq, experience_years=20, role="admin", group="hq", username="admin",
                      password_hash=hash_password(s.admin_password)))

    officer_hash = hash_password(s.officer_password)
    for o in data["officers"]:
        off = IctOfficer(pinfl=o["pinfl"], full_name=o["full_name"], position=o["position"],
                         agency=agencies[o["agency"]], experience_years=o["experience_years"], role="officer",
                         group=o["group"], username=o["username"], password_hash=officer_hash)
        db.add(off)
        for stage, base in (("before", BEFORE_DATE), ("after", AFTER_DATE)):
            sess = o["sessions"][stage]
            ksa = sess["ksa"]
            k = {b: float(ksa[b][0]) for b in BLOCK_CODES}
            sv = {b: float(ksa[b][1]) for b in BLOCK_CODES}
            a = {b: float(ksa[b][2]) for b in BLOCK_CODES}
            persist_evaluation(db, off, k, sv, a, sess["sub_scores"], stage, sess["duration_minutes"],
                               details={"source": "Dissertatsiya 3.3-jadval eksperimental tanlamasi"},
                               created_at=base + timedelta(hours=o["index"]))


def seed(reset: bool = False) -> bool:
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(CompetencyBlock).limit(1)) is not None:
            return False
        seed_reference(db)
        seed_people(db)
        db.commit()
    return True


if __name__ == "__main__":
    created = seed(reset="--reset" in sys.argv)
    print("Ma’lumotlar bazasi to‘ldirildi" if created else "Ma’lumotlar bazasi allaqachon to‘ldirilgan")
