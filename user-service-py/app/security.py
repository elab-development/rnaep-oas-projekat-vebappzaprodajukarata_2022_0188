"""
Sigurnost - heširanje lozinki (bcrypt) i JWT tokeni.
"""
from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# Kontekst za heširanje lozinki (bcrypt - isto kao Laravel)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hešira lozinku."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Proverava da li lozinka odgovara hešu."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Kreira JWT token za korisnika."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Dekodira JWT token i vraća ID korisnika (ili None ako je nevažeći)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except (JWTError, ValueError):
        return None
