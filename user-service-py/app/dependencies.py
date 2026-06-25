"""
Dependencies - provera autentifikacije i autorizacije.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

# Šema za Bearer token u Authorization header-u
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Vraća trenutno prijavljenog korisnika na osnovu JWT tokena.
    Baca 401 ako token nedostaje ili je nevažeći.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niste prijavljeni.",
        )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nevažeći ili istekao token.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Korisnik ne postoji.",
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dozvoljava pristup samo administratorima.
    Baca 403 ako korisnik nije admin.
    """
    if not current_user.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pristup dozvoljen samo administratorima.",
        )
    return current_user
