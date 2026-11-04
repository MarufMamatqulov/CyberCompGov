from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import IctOfficer

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(officer: IctOfficer) -> str:
    s = get_settings()
    payload = {
        "sub": str(officer.id),
        "role": officer.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=s.jwt_expire_minutes),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> IctOfficer:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Avtorizatsiya talab etiladi",
                                 headers={"WWW-Authenticate": "Bearer"})
    if not token:
        raise unauthorized
    s = get_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise unauthorized
    user = db.get(IctOfficer, user_id)
    if user is None:
        raise unauthorized
    return user


def require_admin(user: IctOfficer = Depends(current_user)) -> IctOfficer:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat attestatsiya komissiyasi uchun")
    return user


def require_admin_or_expert(user: IctOfficer = Depends(current_user)) -> IctOfficer:
    if user.role not in ("admin", "expert"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat komissiya va ekspertlar uchun")
    return user


def require_leadership(user: IctOfficer = Depends(current_user)) -> IctOfficer:
    if user.role not in ("admin", "expert", "supervisor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat komissiya a’zolari va tashkilot rahbarlari uchun")
    return user


def ensure_can_view(user: IctOfficer, officer_id: int, db: Session | None = None) -> None:
    if user.role in ("admin", "expert"):
        return
    if user.id == officer_id:
        return
    if user.role == "supervisor":
        if db is not None:
            target = db.get(IctOfficer, officer_id)
            if target is not None and target.agency_id == user.agency_id:
                return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Boshqa xodim pasportini ko‘rish huquqi yo‘q")
