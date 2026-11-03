import json
from pathlib import Path

import pytest

from app.services.scoring_engine import (
    LEVEL_BASIC, LEVEL_CONDITIONAL, LEVEL_CRITICAL, LEVEL_EXPERT, LEVEL_QUALIFIED, THESIS_AHP_MATRIX, classify,
    compute_ahp_weights, domain_score, evaluate,
)
from app.services.stats import paired_t_test


def _ksa(table):
    k = {b: v[0] for b, v in table.items()}
    s = {b: v[1] for b, v in table.items()}
    a = {b: v[2] for b, v in table.items()}
    return k, s, a


E1 = {"C1": (88, 82, 83), "C2": (80, 85, 77), "C3": (78, 75, 75), "C4": (85, 80, 82)}
E2 = {"C1": (80, 70, 67), "C2": (70, 60, 53), "C3": (60, 40, 33), "C4": (80, 75, 70)}
E3 = {"C1": (60, 50, 47), "C2": (52, 45, 41), "C3": (48, 40, 35), "C4": (65, 55, 55)}


def test_ahp_thesis_matrix_weights_and_consistency():
    res = compute_ahp_weights(THESIS_AHP_MATRIX)
    assert res.weights == pytest.approx([0.20, 0.35, 0.25, 0.20], abs=1e-9)
    assert res.cr < 0.10
    assert res.consistent
    assert res.lambda_max == pytest.approx(4.0, abs=1e-6)


def test_ahp_rounded_matrix_from_table():
    rounded = [[1, 0.571, 0.8, 1], [1.75, 1, 1.4, 1.75], [1.25, 0.714, 1, 1.25], [1, 0.571, 0.8, 1]]
    res = compute_ahp_weights(rounded)
    assert res.weights == pytest.approx([0.20, 0.35, 0.25, 0.20], abs=1e-3)
    assert res.cr < 0.10


def test_ahp_inconsistent_matrix_detected():
    bad = [[1, 9, 1 / 9, 1], [1 / 9, 1, 9, 1], [9, 1 / 9, 1, 9], [1, 1, 1 / 9, 1]]
    res = compute_ahp_weights(bad)
    assert res.cr >= 0.10
    assert not res.consistent


def test_e1_qualified():
    ev = evaluate(*_ksa(E1))
    assert ev.c == {"C1": 84.0, "C2": 81.0, "C3": 76.0, "C4": 82.0}
    assert ev.i_axk == pytest.approx(80.55)
    assert ev.phi == 1
    assert ev.level == LEVEL_QUALIFIED
    assert ev.gaps == {"C1": 0.0, "C2": 0.0, "C3": 4.0, "C4": 0.0}
    assert ev.gap_blocks == []


def test_e2_conditional_because_c3_below_threshold():
    ev = evaluate(*_ksa(E2))
    assert ev.c == {"C1": 72.0, "C2": 61.0, "C3": 44.0, "C4": 75.0}
    assert ev.i_axk == pytest.approx(61.75)
    assert ev.phi == 0
    assert ev.failed_blocks == ["C3"]
    assert ev.level == LEVEL_CONDITIONAL
    assert ev.gaps == {"C1": 8.0, "C2": 19.0, "C3": 36.0, "C4": 5.0}
    assert ev.gap_blocks == ["C2", "C3"]


def test_e3_critical():
    ev = evaluate(*_ksa(E3))
    assert ev.c == {"C1": 52.0, "C2": 46.0, "C3": 41.0, "C4": 58.0}
    assert ev.i_axk == pytest.approx(48.35)
    assert ev.phi == 0
    assert ev.level == LEVEL_CRITICAL
    assert ev.gaps == {"C1": 28.0, "C2": 34.0, "C3": 39.0, "C4": 22.0}


@pytest.mark.parametrize("i, phi, level", [
    (54.99, 1, LEVEL_CRITICAL), (55.0, 0, LEVEL_CONDITIONAL), (55.0, 1, LEVEL_BASIC), (70.99, 1, LEVEL_BASIC),
    (71.0, 1, LEVEL_QUALIFIED), (85.99, 1, LEVEL_QUALIFIED), (86.0, 1, LEVEL_EXPERT), (85.0, 0, LEVEL_CONDITIONAL),
])
def test_classification_boundaries(i, phi, level):
    assert classify(i, phi) == level


def test_mii_norm_increases_gaps():
    ev = evaluate(*_ksa(E1), norm=85.0)
    assert ev.gaps == {"C1": 1.0, "C2": 4.0, "C3": 9.0, "C4": 3.0}


def test_domain_score_validates_range():
    with pytest.raises(ValueError):
        domain_score(101, 50, 50)


def test_experiment_dataset_matches_table_3_3():
    data = json.loads((Path(__file__).parents[1] / "app/seed/experiment_officers.json").read_text(encoding="utf-8"))
    officers = data["officers"]
    assert len(officers) == 45
    res = {}
    for stage in ("before", "after"):
        evs = [evaluate(*({b: o["sessions"][stage]["ksa"][b][n] for b in ("C1", "C2", "C3", "C4")}
                          for n in range(3))) for o in officers]
        res[stage] = evs
    mean = lambda xs: sum(xs) / len(xs)  # noqa: E731
    for stage, targets in (("before", (61.4, 53.8, 48.2, 64.5, 56.1)), ("after", (81.2, 78.6, 74.8, 83.4, 79.1))):
        evs = res[stage]
        got = [mean([e.c[b] for e in evs]) for b in ("C1", "C2", "C3", "C4")] + [mean([e.i_axk for e in evs])]
        assert [round(x, 1) for x in got] == list(targets)
    t = paired_t_test([e.i_axk for e in res["before"]], [e.i_axk for e in res["after"]])
    assert round(t["t"], 2) == 14.82
    assert t["p"] < 0.001
    good = (LEVEL_QUALIFIED, LEVEL_EXPERT)
    assert round(sum(e.level in good for e in res["before"]) / 45 * 100, 1) == 20.0
    assert round(sum(e.level in good for e in res["after"]) / 45 * 100, 1) == 68.9
    named = {o["username"]: o for o in officers}
    assert evaluate(*_ksa({b: named["e2"]["sessions"]["before"]["ksa"][b] for b in E2})).i_axk == pytest.approx(61.75)


def test_paired_t_test_p_value():
    res = paired_t_test([1, 2, 3, 4, 5, 6], [2, 2.5, 4.1, 4.4, 6.3, 6.2])
    # scipy.stats.ttest_rel bilan solishtirilgan qiymatlar
    assert res["t"] == pytest.approx(4.160251, abs=1e-6)
    assert res["p"] == pytest.approx(0.0088219, abs=1e-6)
