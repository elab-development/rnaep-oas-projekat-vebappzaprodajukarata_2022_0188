"""
CRUD operacije - funkcije za rad sa bazom (Create, Read, Update, Delete).
"""
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User, Role, PasswordReset
from app.security import hash_password


# ---------- Korisnik ----------

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def search_users(db: Session, term: str) -> list[User]:
    like = f"%{term}%"
    return db.query(User).filter(
        (User.name.like(like)) | (User.email.like(like))
    ).all()


def count_users(db: Session) -> int:
    return db.query(User).count()


def create_user(db: Session, name: str, email: str, password: str,
                role_name: str = "user") -> User:
    user = User(name=name, email=email, password=hash_password(password))

    # Dodeli ulogu
    role = db.query(Role).filter(Role.name == role_name).first()
    if role:
        user.roles.append(role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, name: str | None = None,
                email: str | None = None, password: str | None = None) -> User:
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    if password is not None:
        user.password = hash_password(password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


# ---------- Uloge ----------

def assign_role(db: Session, user: User, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).first()
    if role and not user.has_role(role_name):
        user.roles.append(role)
        db.commit()
        db.refresh(user)
    return user


def remove_role(db: Session, user: User, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).first()
    if role and user.has_role(role_name):
        user.roles.remove(role)
        db.commit()
        db.refresh(user)
    return user


# ---------- Password reset ----------

def create_password_reset(db: Session, user: User) -> PasswordReset:
    # Obriši stare tokene ovog korisnika
    db.query(PasswordReset).filter(PasswordReset.user_id == user.id).delete()

    reset = PasswordReset(
        user_id=user.id,
        reset_token=secrets.token_urlsafe(40),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    db.add(reset)
    db.commit()
    db.refresh(reset)
    return reset


def get_password_reset(db: Session, token: str) -> PasswordReset | None:
    return db.query(PasswordReset).filter(PasswordReset.reset_token == token).first()


def reset_user_password(db: Session, reset: PasswordReset, new_password: str) -> User:
    user = reset.user
    user.password = hash_password(new_password)
    reset.used_at = datetime.utcnow()
    # Obriši ostale tokene radi sigurnosti
    db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id,
        PasswordReset.id != reset.id,
    ).delete()
    db.commit()
    db.refresh(user)
    return user
