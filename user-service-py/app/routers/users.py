"""
Rute za upravljanje korisnicima (samo admin).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import User

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_all_users(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = crud.list_users(db, skip=skip, limit=limit)
    return [_user_to_out(u) for u in users]


@router.get("/search", response_model=list[schemas.UserOut])
def search(
    q: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = crud.search_users(db, q)
    return [_user_to_out(u) for u in users]


@router.get("/statistics/count")
def statistics(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return {"total_users": crud.count_users(db)}


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_one(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # IDOR zaštita: običan korisnik sme da vidi samo SVOJ profil; admin sme sve
    if current_user.id != user_id and not current_user.has_role("admin"):
        raise HTTPException(
            status_code=403,
            detail="Nemate dozvolu da pristupite ovom korisniku.",
        )

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    return _user_to_out(user)


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_one(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    user = crud.update_user(db, user, payload.name, payload.email, payload.password)
    return _user_to_out(user)


@router.delete("/{user_id}", response_model=schemas.MessageResponse)
def delete_one(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    crud.delete_user(db, user)
    return schemas.MessageResponse(message="Korisnik je obrisan.")


@router.post("/{user_id}/assign-role", response_model=schemas.UserOut)
def assign_role(
    user_id: int,
    payload: schemas.RoleAssign,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    user = crud.assign_role(db, user, payload.role)
    return _user_to_out(user)


@router.delete("/{user_id}/remove-role", response_model=schemas.UserOut)
def remove_role(
    user_id: int,
    payload: schemas.RoleAssign,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    user = crud.remove_role(db, user, payload.role)
    return _user_to_out(user)


def _user_to_out(user: User) -> schemas.UserOut:
    return schemas.UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        roles=user.role_names(),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
