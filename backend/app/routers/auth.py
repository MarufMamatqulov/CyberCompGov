from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import IctOfficer
from app.security import create_token, current_user, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

DEMO_ACCOUNTS = {
    "admin": "Komissiya Raisi (Admin)",
    "e1": "e1 — Aliyev J. (Malakali)",
    "e2": "e2 — Karimov S. (Shartli bazaviy, Φ=0)",
    "e3": "e3 — Rustamov B. (Kritik)",
}


class LoginIn(BaseModel):
    username: str
    password: str


class EimzoIn(BaseModel):
    pinfl: str
    pin: str


def user_out(u: IctOfficer) -> dict:
    return {"id": u.id, "username": u.username, "full_name": u.full_name, "role": u.role, "position": u.position,
            "agency": u.agency.name, "category": u.agency.category}


def _token_response(u: IctOfficer) -> dict:
    return {"access_token": create_token(u), "token_type": "bearer", "user": user_out(u)}


def _require_demo() -> None:
    if not get_settings().demo_mode:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Demo rejimi o‘chirilgan")


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(IctOfficer).where(IctOfficer.username == body.username.strip()))
    if u is None or not verify_password(body.password, u.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Login yoki parol noto‘g‘ri")
    return _token_response(u)


@router.get("/demo-accounts")
def demo_accounts():
    _require_demo()
    return [{"key": k, "label": v} for k, v in DEMO_ACCOUNTS.items()]


@router.post("/demo/{key}")
def demo_login(key: str, db: Session = Depends(get_db)):
    _require_demo()
    if key not in DEMO_ACCOUNTS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Demo hisob topilmadi")
    u = db.scalar(select(IctOfficer).where(IctOfficer.username == key))
    if u is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Demo hisob topilmadi")
    return _token_response(u)


@router.get("/eimzo/certificates")
def eimzo_certificates(db: Session = Depends(get_db)):
    """E-IMZO simulyatsiyasi: kompyuterda “o‘rnatilgan” demo ERI kalitlari."""
    _require_demo()
    users = db.scalars(select(IctOfficer).where(IctOfficer.username.in_(list(DEMO_ACCOUNTS)))).all()
    order = list(DEMO_ACCOUNTS)
    users.sort(key=lambda u: order.index(u.username))
    return [{"pinfl": u.pinfl, "full_name": u.full_name, "organization": u.agency.name,
             "serial": f"7A{u.id:06d}F", "valid_to": "2027-12-31"} for u in users]


@router.post("/eimzo")
def eimzo_login(body: EimzoIn, db: Session = Depends(get_db)):
    _require_demo()
    if body.pin != get_settings().eimzo_demo_pin:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "ERI kaliti paroli noto‘g‘ri")
    u = db.scalar(select(IctOfficer).where(IctOfficer.pinfl == body.pinfl))
    if u is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sertifikat egasi tizimda ro‘yxatdan o‘tmagan")
    return _token_response(u)


@router.get("/me")
def me(user: IctOfficer = Depends(current_user)):
    return user_out(user)


@router.get("/config")
def public_config():
    return {"demo_mode": get_settings().demo_mode}
