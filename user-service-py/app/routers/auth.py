"""
Rute za autentifikaciju: registracija, login, profil, password reset.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.security import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    # Provera da se lozinke poklapaju
    if payload.password != payload.password_confirmation:
        raise HTTPException(status_code=422, detail="Lozinke se ne podudaraju.")

    # Provera da email nije već zauzet
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=422, detail="Email adresa je već registrovana.")

    user = crud.create_user(db, payload.name, payload.email, payload.password)
    return _user_to_out(user)


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Pogrešan email ili lozinka.")

    token = create_access_token(user.id)
    return schemas.LoginResponse(
        user=_user_to_out(user),
        token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=schemas.MessageResponse)
def logout(current_user: User = Depends(get_current_user)):
    # JWT je stateless - logout se radi tako što klijent obriše token.
    return schemas.MessageResponse(message="Uspešna odjava.")


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _user_to_out(current_user)


@router.put("/profile", response_model=schemas.UserOut)
def update_profile(
    payload: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ako menja email, proveri da nije zauzet od drugog korisnika
    if payload.email and payload.email != current_user.email:
        existing = crud.get_user_by_email(db, payload.email)
        if existing:
            raise HTTPException(status_code=422, detail="Email adresa je već registrovana.")

    user = crud.update_user(db, current_user, payload.name, payload.email, payload.password)
    return _user_to_out(user)


@router.post("/forgot-password")
def forgot_password(payload: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=422, detail="Korisnik sa ovom email adresom ne postoji.")

    reset = crud.create_password_reset(db, user)
    # TODO: poslati email sa linkom. Za testiranje vraćamo token direktno.
    return {
        "message": "Reset link je poslat na vašu email adresu.",
        "token": reset.reset_token,  # OBRIŠI U PRODUKCIJI
    }


@router.post("/validate-reset-token")
def validate_reset_token(payload: schemas.ValidateTokenRequest, db: Session = Depends(get_db)):
    reset = crud.get_password_reset(db, payload.token)
    if not reset:
        raise HTTPException(status_code=422, detail="Nevažeći reset token.")
    if not reset.is_valid():
        raise HTTPException(
            status_code=422,
            detail="Reset token je istekao ili je već korišćen. Zatražite novi.",
        )
    return {"message": "Token je validan.", "expires_at": reset.expires_at}


@router.post("/reset-password", response_model=schemas.UserOut)
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    if payload.password != payload.password_confirmation:
        raise HTTPException(status_code=422, detail="Lozinke se ne podudaraju.")

    reset = crud.get_password_reset(db, payload.token)
    if not reset:
        raise HTTPException(status_code=422, detail="Nevažeći reset token.")
    if not reset.is_valid():
        raise HTTPException(
            status_code=422,
            detail="Reset token je istekao ili je već korišćen. Zatražite novi.",
        )

    user = crud.reset_user_password(db, reset, payload.password)
    return _user_to_out(user)


def _user_to_out(user: User) -> schemas.UserOut:
    """Pretvara User model u izlaznu šemu (sa imenima uloga)."""
    return schemas.UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        roles=user.role_names(),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
