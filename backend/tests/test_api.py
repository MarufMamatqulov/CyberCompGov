import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import lab_sim


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _auth(client, key="admin"):
    token = client.post(f"/api/auth/demo/{key}").json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_and_passport_e2(client):
    r = client.post("/api/auth/login", json={"username": "e2", "password": "Demo@2026"})
    assert r.status_code == 200
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    me = client.get("/api/auth/me", headers=h).json()
    p = client.get(f"/api/officers/{me['id']}/passport", headers=h).json()
    s = p["session"]
    assert s["stage"] == "before"
    assert s["i_axk"] == pytest.approx(61.75)
    assert s["phi"] == 0
    assert s["failed_blocks"] == ["C3"]
    assert {g["block_code"] for g in s["plan"]} == {"C2", "C3"}
    assert all(g["deadline_days"] == 30 for g in s["plan"] if g["block_code"] == "C3")
    assert p["compare"]["stage"] == "after"


def test_officer_cannot_see_others(client):
    h = _auth(client, "e1")
    assert client.get("/api/officers", headers=h).status_code == 403
    officers = client.get("/api/officers", headers=_auth(client)).json()
    other = next(o for o in officers if o["username"] == "e3")
    assert client.get(f"/api/officers/{other['id']}/passport", headers=h).status_code == 403


def test_registry_and_experiment(client):
    h = _auth(client)
    officers = client.get("/api/officers", headers=h).json()
    assert len(officers) == 45
    exp = client.get("/api/analytics/experiment", headers=h).json()
    kpi = exp["kpi"]
    assert kpi["n"] == 45
    assert round(kpi["i_before"], 1) == 56.1 and round(kpi["i_after"], 1) == 79.1
    assert round(kpi["qualified_before_pct"], 1) == 20.0 and round(kpi["qualified_after_pct"], 1) == 68.9
    assert round(kpi["i_delta"], 1) == 23.0 and round(kpi["i_delta_pct"], 1) == 41.0
    assert round(kpi["avg_minutes"]) == 35 and round(kpi["speedup"], 1) == 3.4
    assert round(exp["table"][-1]["t"], 2) == 14.82


def test_catalog_has_36_indicators(client):
    cat = client.get("/api/catalog").json()
    assert len(cat) == 4
    assert sum(len(b["subs"]) for b in cat) == 12
    assert sum(len(b["subs"]) * 3 for b in cat) == 36


def test_ahp_endpoints(client):
    d = client.get("/api/ahp/default").json()
    assert d["weights"] == pytest.approx([0.2, 0.35, 0.25, 0.2])
    bad = client.post("/api/ahp/compute", json={"matrix": [[1, 9, 1 / 9, 1], [1 / 9, 1, 9, 1], [9, 1 / 9, 1, 9],
                                                           [1, 1, 1 / 9, 1]]}).json()
    assert bad["consistent"] is False
    assert client.post("/api/ahp/compute", json={"matrix": [[1, 20], [0.05, 1]]}).status_code == 422


def test_content_hides_answers(client):
    c = client.get("/api/assessment/content", headers=_auth(client, "e1")).json()
    assert len(c["tests"]) == 12 and len(c["labs"]) == 4 and len(c["cases"]) == 4
    raw = str(c)
    assert "correct" not in raw and "points" not in raw and "'engine'" not in raw


C2_PERFECT = [
    "sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config",
    "sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config",
    "systemctl restart sshd",
    "ufw default deny incoming",
    "ufw deny 3389/tcp",
    "ufw allow from 10.10.99.0/24 to any port 22 proto tcp",
    "ufw enable",
    "apt install --only-upgrade openssh-server",
]
C3_PERFECT = [
    "cat /var/log/auth.log", "netstat -tunap", "mkdir -p /root/evidence", "cp /tmp/.x/kworkerd /root/evidence/",
    "kill -9 4721", "ufw deny from 185.220.101.44", "passwd -l backup_user",
    "sha256sum -c /var/backups/pg_dump/SHA256SUMS", "pg_restore -d egov /var/backups/pg_dump/egov_2026-11-01.dump",
]


def test_lab_simulators():
    assert lab_sim.grade("c2", C2_PERFECT).score == 100.0
    assert lab_sim.grade("c3", C3_PERFECT).score == 100.0
    lockout = lab_sim.grade("c2", ["ufw default deny incoming", "ufw enable"])
    assert lockout.penalties and lockout.score < 10
    assert not next(c for c in lockout.checks if c.id == "enable").passed
    bad_restore = lab_sim.grade("c3", ["pg_restore -d egov /var/backups/pg_dump/egov_2026-11-02.dump"])
    assert bad_restore.penalties
    out = lab_sim.execute("c3", ["kill -9 4721"], "netstat -tunap")
    assert "185.220.101.44:4444" not in out


def test_full_assessment_submission_and_pdf(client):
    h = _auth(client, "e3")
    content = client.get("/api/assessment/content", headers=h).json()
    out = client.post("/api/assessment/labs/LAB-C2-01/exec", headers=h,
                      json={"history": [], "command": "ss -tlnp"}).json()["output"]
    assert "3389" in out
    from app.seed.questions_data import CASES, LAB_C1, LAB_C4, TESTS

    public = {c["code"]: c for c in content["cases"]}

    def best_path(case):
        ids = {s["id"]: f"b{i + 1}" for i, s in enumerate(case["stages"])}
        assert public[case["code"]]["start"] == ids[case["start"]]
        stages = {s["id"]: s for s in case["stages"]}
        sid, path = case["start"], []
        while sid:
            opt = max(stages[sid]["options"], key=lambda o: o["points"])
            path.append({"stage": ids[sid], "option": opt["id"]})
            sid = opt["next"]
        return path

    body = {
        "duration_seconds": 2100,
        "tests": {t["code"]: t["correct"] for t in TESTS},
        "labs": {
            "LAB-C1-01": {"levels": LAB_C1["answer"]["levels"], "storage": LAB_C1["answer"]["storage"], "legal": 0},
            "LAB-C2-01": {"history": C2_PERFECT},
            "LAB-C3-02": {"history": C3_PERFECT},
            "LAB-C4-01": {"answers": LAB_C4["answer"]["q"], "sandbox_run": True, "actions": ["x1", "x2", "x3", "x4"]},
        },
        "cases": {c["code"]: best_path(c) for c in CASES},
    }
    assert len(content["cases"]) == len(body["cases"])
    r = client.post("/api/assessment/submit", headers=h, json=body).json()
    assert r["i_axk"] == pytest.approx(100.0)
    assert r["level"].startswith("Ekspert")
    p = client.get(f"/api/officers/{r['officer_id']}/passport", headers=h).json()
    assert p["session"]["id"] == r["session_id"] and p["session"]["stage"] == "attestatsiya"
    pdf = client.get(f"/api/reports/session/{r['session_id']}/pdf", headers=h)
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"
    v = client.get(f"/api/verify/{p['session']['verify_code']}").json()
    assert v["valid"] and v["i_axk"] == pytest.approx(100.0)


def test_empty_submission_scores_zero(client):
    h = _auth(client, "e1")
    r = client.post("/api/assessment/submit", headers=h, json={}).json()
    assert r["i_axk"] == 0.0 and r["level"].startswith("Kritik")
