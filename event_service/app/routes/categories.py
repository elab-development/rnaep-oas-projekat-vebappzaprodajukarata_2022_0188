from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import require_admin
from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate
from app.exceptions import CategoryNotFoundException

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(category_data: CategoryCreate,admin_role: str = Depends(require_admin), db: Session = Depends(get_db)):
    category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get("/")
def get_all_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise CategoryNotFoundException()

    return category


@router.put("/{category_id}")
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    admin_role: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise CategoryNotFoundException()

    category.name = category_data.name
    category.description = category_data.description

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_category(category_id: int,admin_role: str = Depends(require_admin), db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise CategoryNotFoundException()

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}