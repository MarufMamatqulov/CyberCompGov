"""Nomzod javoblarini K, S, A ballariga aylantirish va o‘quv trayektoriyasini shakllantirish."""
from __future__ import annotations

from collections import defaultdict

from app.seed.catalog_data import BASE_COURSE, TRAINING_CATALOG
from app.services import lab_sim
from app.services.scoring_engine import BLOCKS, GAP_TRIGGER, LEVEL_CRITICAL, Evaluation, round_half_up


class SubAccumulator:
    def __init__(self) -> None:
        self._items: dict[str, list[float]] = defaultdict(list)

    def add(self, sub: str, score: float) -> None:
        self._items[sub].append(score)

    def result(self, c: dict[str, float]) -> dict[str, list[float]]:
        out = {}
        for b in BLOCKS:
            n = b[1]
            vals = []
            for j in (1, 2, 3):
                items = self._items.get(f"c{n}.{j}")
                vals.append(round_half_up(sum(items) / len(items), 1) if items else c[b])
            out[b] = vals
        return out


# ---------------------------------------------------------------- K: testlar

def grade_tests(tests: list, answers: dict[str, int], subs: SubAccumulator):
    per_block: dict[str, list[int]] = defaultdict(list)
    details = []
    for t in tests:
        chosen = answers.get(t.code)
        ok = chosen is not None and chosen == t.answer_json["correct"]
        per_block[t.block_code].append(int(ok))
        subs.add(t.sub_code, 100.0 if ok else 0.0)
        details.append({"code": t.code, "block": t.block_code, "chosen": chosen,
                        "correct": t.answer_json["correct"], "ok": ok,
                        "explanation": t.answer_json.get("explanation", "")})
    k = {b: round_half_up(sum(v) / len(v) * 100, 1) if (v := per_block.get(b)) else 0.0 for b in BLOCKS}
    return k, details


# ---------------------------------------------------------------- S: laboratoriyalar

def _grade_classify(lab, sub: dict, subs: SubAccumulator) -> dict:
    ans = lab.answer_json
    checks = []
    for aid, lvl in ans["levels"].items():
        ok = (sub.get("levels") or {}).get(aid) == lvl
        checks.append({"id": f"{aid}-level", "sub": "c1.2", "title": f"{aid}: konfidensiallik darajasi", "weight": 1,
                       "passed": ok})
    for aid, st in ans["storage"].items():
        ok = (sub.get("storage") or {}).get(aid) == st
        checks.append({"id": f"{aid}-storage", "sub": "c1.3", "title": f"{aid}: saqlash/lokalizatsiya talabi",
                       "weight": 1, "passed": ok})
    checks.append({"id": "legal", "sub": "c1.1", "title": "Huquqiy asos", "weight": 1,
                   "passed": sub.get("legal") == ans["legal"]})
    for c in checks:
        subs.add(c["sub"], 100.0 if c["passed"] else 0.0)
    score = sum(c["passed"] for c in checks) / len(checks) * 100
    return {"score": round_half_up(score, 1), "checks": checks, "penalties": []}


def _grade_email(lab, sub: dict, subs: SubAccumulator) -> dict:
    ans = lab.answer_json
    checks = []
    for qid, correct in ans["q"].items():
        ok = (sub.get("answers") or {}).get(qid) == correct
        checks.append({"id": qid, "sub": ans["q_sub"][qid], "title": qid, "weight": 1, "passed": ok})
    checks.append({"id": "sandbox", "sub": "c4.2", "title": "Ilova sandbox muhitida tekshirildi", "weight": 1,
                   "passed": bool(sub.get("sandbox_run"))})
    chosen = set(sub.get("actions") or [])
    good, bad = set(ans["good_actions"]), set(ans["bad_actions"])
    action_ratio = max(0.0, (len(chosen & good) - len(chosen & bad)) / len(good))
    checks.append({"id": "actions", "sub": "c4.3", "title": "Javob choralari to‘g‘ri tanlandi", "weight": 2,
                   "passed": action_ratio == 1.0, "ratio": round(action_ratio, 2)})
    penalties = [f"Xavfli chora tanlandi: {a}" for a in sorted(chosen & bad)]
    total = sum(c["weight"] for c in checks)
    got = sum(c["weight"] for c in checks[:-1] if c["passed"]) + 2 * action_ratio
    for c in checks:
        subs.add(c["sub"], 100.0 * (c.get("ratio", 1.0 if c["passed"] else 0.0)))
    return {"score": round_half_up(got / total * 100, 1), "checks": checks, "penalties": penalties}


def grade_labs(labs: list, submissions: dict[str, dict], subs: SubAccumulator):
    s = {b: 0.0 for b in BLOCKS}
    details = {}
    for lab in labs:
        sub = submissions.get(lab.code) or {}
        kind = lab.payload_json["type"]
        if kind == "classify":
            res = _grade_classify(lab, sub, subs)
        elif kind == "email":
            res = _grade_email(lab, sub, subs)
        else:
            r = lab_sim.grade(lab.answer_json["engine"], list(sub.get("history") or []))
            res = r.as_dict()
            for c in r.checks:
                subs.add(c.sub, 100.0 if c.passed else 0.0)
        s[lab.block_code] = res["score"]
        details[lab.code] = res
    return s, details


# ---------------------------------------------------------------- A: keyslar

def _best_path(stages: dict, sid: str | None) -> float:
    if sid is None:
        return 0.0
    st = stages[sid]
    return max(o["points"] + _best_path(stages, o["next"]) for o in st["options"])


def grade_case(case, path: list[dict], subs: SubAccumulator) -> dict:
    stages = {s["id"]: s for s in case.answer_json["stages"]}
    best = _best_path(stages, case.answer_json["start"])
    sid = case.answer_json["start"]
    got = 0.0
    trail = []
    for step in path:
        if sid is None or step.get("stage") != sid:
            break
        st = stages[sid]
        opt = next((o for o in st["options"] if o["id"] == step.get("option")), None)
        if opt is None:
            break
        got += opt["points"]
        subs.add(st["sub"], opt["points"] * 10.0)
        trail.append({"stage": sid, "option": opt["id"], "points": opt["points"]})
        sid = opt["next"]
    # vaqt tugagani sababli javobsiz qolgan bosqich(lar) 0 ball bilan hisoblanadi
    while sid is not None:
        subs.add(stages[sid]["sub"], 0.0)
        trail.append({"stage": sid, "option": None, "points": 0})
        sid = stages[sid]["options"][0]["next"]
    return {"score": round_half_up(got / best * 100, 1) if best else 0.0, "points": got, "max_points": best,
            "trail": trail}


def grade_cases(cases: list, paths: dict[str, list[dict]], subs: SubAccumulator):
    a = {b: 0.0 for b in BLOCKS}
    details = {}
    for case in cases:
        res = grade_case(case, paths.get(case.code) or [], subs)
        a[case.block_code] = res["score"]
        details[case.code] = res
    return a, details


# ---------------------------------------------------------------- O‘quv reja

def build_training_plan(ev: Evaluation, sub_scores: dict[str, list[float]]) -> list[dict]:
    plan = []
    if ev.level == LEVEL_CRITICAL:
        title, hours = BASE_COURSE
        plan.append({"block_code": "BASE", "sub_code": "", "delta_c": max(ev.gaps.values()),
                     "assigned_course_title": title, "course_hours": hours, "deadline_days": 90})
    for b in BLOCKS:
        delta = ev.gaps[b]
        if delta <= GAP_TRIGGER:
            continue
        subs = sub_scores.get(b) or [ev.c[b]] * 3
        j = min(range(3), key=lambda idx: subs[idx])
        sub_code = f"c{b[1]}.{j + 1}"
        title, hours = TRAINING_CATALOG[sub_code]
        deadline = 30 if b in ev.failed_blocks else 60
        plan.append({"block_code": b, "sub_code": sub_code, "delta_c": delta,
                     "assigned_course_title": title, "course_hours": hours, "deadline_days": deadline})
    return plan
