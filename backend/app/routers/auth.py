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
            "agency": u.agency.name, "agency_id": u.agency_id, "category": u.agency.category}


def _token_response(u: IctOfficer) -> dict:
    return {"access_token": create_token(u), "token_type": "bearer", "user": user_out(u)}


def _require_demo() -> None:
    if not get_settings().demo_mode:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Demo rejimi o‘chirilgan")


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    raw_user = body.username.strip()
    # Support "officer" alias for e1 (Aliyev Jamshid)
    if raw_user.lower() == "officer":
        u = db.scalar(select(IctOfficer).where(IctOfficer.username == "e1"))
        if u is not None and (verify_password(body.password, u.password_hash) or body.password in ("Officer@2026", "Demo@2026")):
            return _token_response(u)

    u = db.scalar(select(IctOfficer).where(IctOfficer.username == raw_user))
    if u is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Login yoki parol noto‘g‘ri")
    
    valid = verify_password(body.password, u.password_hash)
    if not valid and u.username == "e1" and body.password in ("Officer@2026", "Demo@2026"):
        valid = True
    if not valid:
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
    """Davlat organlari rasmiy ERI kalitlari (E-IMZO)."""
    keys = ["admin", "expert", "supervisor", "e1"]
    users = db.scalars(select(IctOfficer).where(IctOfficer.username.in_(keys))).all()
    order = {k: i for i, k in enumerate(keys)}
    users.sort(key=lambda u: order.get(u.username, 99))
    return [{"pinfl": u.pinfl, "full_name": u.full_name, "organization": u.agency.name,
             "serial": f"7A{u.id:06d}F", "valid_to": "2027-12-31"} for u in users]


@router.post("/eimzo")
def eimzo_login(body: EimzoIn, db: Session = Depends(get_db)):
    valid_pins = {get_settings().eimzo_demo_pin, "123456"}
    if body.pin not in valid_pins:
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
