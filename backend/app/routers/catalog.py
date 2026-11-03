from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CompetencyBlock, KsaIndicator
from app.seed.catalog_data import TRAINING_CATALOG
from app.services.scoring_engine import BLOCKS, THESIS_AHP_MATRIX, compute_ahp_weights

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/catalog")
def catalog(db: Session = Depends(get_db)):
    blocks = db.scalars(select(CompetencyBlock).order_by(CompetencyBlock.code)).all()
    inds = db.scalars(select(KsaIndicator).order_by(KsaIndicator.sub_code)).all()
    return [{
        "code": b.code, "name": b.name, "ahp_weight": b.ahp_weight, "alpha_k": b.alpha_k, "beta_s": b.beta_s,
        "gamma_a": b.gamma_a, "min_threshold": b.min_threshold,
        "subs": [{
            "sub_code": i.sub_code, "sub_name": i.sub_name,
            "k": {"code": i.k_code, "desc": i.k_desc}, "s": {"code": i.s_code, "desc": i.s_desc},
            "a": {"code": i.a_code, "desc": i.a_desc},
            "nist": i.nist_ref, "ecsf": i.ecsf_ref, "law": i.law_ref,
            "course": {"title": TRAINING_CATALOG[i.sub_code][0], "hours": TRAINING_CATALOG[i.sub_code][1]},
        } for i in inds if i.block_code == b.code],
    } for b in blocks]


class AhpIn(BaseModel):
    matrix: list[list[float]]

    @field_validator("matrix")
    @classmethod
    def check(cls, m: list[list[float]]) -> list[list[float]]:
        n = len(m)
        if not 2 <= n <= 10 or any(len(r) != n for r in m):
            raise ValueError("Matritsa n×n (2 ≤ n ≤ 10) bo‘lishi kerak")
        for r in m:
            for v in r:
                if not 1 / 9 - 1e-6 <= v <= 9 + 1e-6:
                    raise ValueError("Saaty shkalasi: qiymatlar 1/9 … 9 oralig‘ida bo‘lishi kerak")
        return m


def _ahp_out(res) -> dict:
    return {"labels": list(BLOCKS) if len(res.weights) == 4 else [f"C{i + 1}" for i in range(len(res.weights))],
            "matrix": res.matrix, "geometric_means": res.geometric_means, "weights": res.weights,
            "lambda_max": res.lambda_max, "ci": res.ci, "cr": res.cr, "ri": res.ri, "consistent": res.consistent}


@router.get("/ahp/default")
def ahp_default():
    return _ahp_out(compute_ahp_weights(THESIS_AHP_MATRIX))


@router.post("/ahp/compute")
def ahp_compute(body: AhpIn):
    try:
        return _ahp_out(compute_ahp_weights(body.matrix))
    except ValueError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
