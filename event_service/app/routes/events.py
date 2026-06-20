from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.security import require_admin
from app.database import get_db
from app.models import Event, Venue, Category
from app.schemas import EventCreate
from app.exceptions import EventNotFoundException

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/")
def create_event(event_data: EventCreate,admin_role: str = Depends(require_admin), db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == event_data.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    category = db.query(Category).filter(Category.id == event_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    event = Event(
        title=event_data.title,
        description=event_data.description,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        venue_id=event_data.venue_id,
        category_id=event_data.category_id,
        status="scheduled"
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get("/")
def get_all_events(db: Session = Depends(get_db)):
    return db.query(Event).all()


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise EventNotFoundException()

    return event


@router.put("/{event_id}")
def update_event(
    event_id: int,
    event_data: EventCreate,
    admin_role: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise EventNotFoundException()

    event.title = event_data.title
    event.description = event_data.description
    event.start_time = event_data.start_time
    event.end_time = event_data.end_time
    event.venue_id = event_data.venue_id
    event.category_id = event_data.category_id
    event.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(event)

    return event


@router.delete("/{event_id}")
def delete_event(event_id: int,admin_role: str = Depends(require_admin), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise EventNotFoundException()

    db.delete(event)
    db.commit()

    return {"message": "Event deleted successfully"}


@router.patch("/{event_id}/cancel")
def cancel_event(event_id: int,admin_role: str = Depends(require_admin), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise EventNotFoundException()

    event.status = "cancelled"
    event.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(event)

    return event