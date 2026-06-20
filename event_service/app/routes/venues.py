from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import require_admin
from app.database import get_db
from app.models import Venue
from app.schemas import VenueCreate
from app.exceptions import VenueNotFoundException

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.post("/")
def create_venue(venue_data: VenueCreate,admin_role: str = Depends(require_admin), db: Session = Depends(get_db)):
    venue = Venue(
        name=venue_data.name,
        address=venue_data.address,
        city=venue_data.city,
        capacity=venue_data.capacity
    )

    db.add(venue)
    db.commit()
    db.refresh(venue)

    return venue


@router.get("/")
def get_all_venues(db: Session = Depends(get_db)):
    return db.query(Venue).all()


@router.get("/{venue_id}")
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()

    if not venue:
        raise VenueNotFoundException()

    return venue


@router.put("/{venue_id}")
def update_venue(
    venue_id: int,
    venue_data: VenueCreate,
    admin_role: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()

    if not venue:
        raise VenueNotFoundException()

    venue.name = venue_data.name
    venue.address = venue_data.address
    venue.city = venue_data.city
    venue.capacity = venue_data.capacity

    db.commit()
    db.refresh(venue)

    return venue


@router.delete("/{venue_id}")
def delete_venue(venue_id: int,admin_role: str = Depends(require_admin), db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()

    if not venue:
        raise VenueNotFoundException()

    db.delete(venue)
    db.commit()

    return {"message": "Venue deleted successfully"}