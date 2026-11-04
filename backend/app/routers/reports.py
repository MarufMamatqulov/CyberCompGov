from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import EvalSession, IctOfficer
from app.security import current_user, ensure_can_view
from app.services.pdf_report import build_passport_pdf

router = APIRouter(prefix="/api", tags=["reports"])


def verify_url(code: str) -> str:
    return f"{get_settings().public_base_url.rstrip('/')}/verify/{code}"


@router.get("/reports/session/{session_id}/pdf")
def session_pdf(session_id: int, db: Session = Depends(get_db), user: IctOfficer = Depends(current_user)):
    sess = db.get(EvalSession, session_id)
    if sess is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sessiya topilmadi")
    ensure_can_view(user, sess.officer_id, db)
    pdf = build_passport_pdf(sess, verify_url(sess.verify_code))
    filename = f"attestatsiya_pasporti_{sess.officer.username}_{sess.id}.pdf"
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/verify/{code}")
def verify(code: str, db: Session = Depends(get_db)):
    """QR-kod orqali hujjat haqiqiyligini ochiq tekshirish (shaxsiy ma’lumotlar qisqartirilgan)."""
    sess = db.scalar(select(EvalSession).where(EvalSession.verify_code == code.upper()))
    if sess is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hujjat topilmadi yoki haqiqiy emas")
    parts = sess.officer.full_name.split()
    masked = " ".join([parts[0]] + [p[0] + "." for p in parts[1:]]) if parts else ""
    return {"valid": True, "code": sess.verify_code, "officer": masked, "agency": sess.officer.agency.name,
            "date": sess.created_at.isoformat(), "i_axk": sess.i_axk, "phi": sess.phi_flag,
            "level": sess.level_name}
