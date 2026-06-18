from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Ticket, Seat, Reservation, Order
from app.schemas import ReservationCreate

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/")
def get_all_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()


@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.post("/reserve")
def reserve_ticket(reservation_data: ReservationCreate, db: Session = Depends(get_db)):
    try:
        ticket = (
            db.query(Ticket)
            .filter(Ticket.id == reservation_data.ticket_id)
            .with_for_update()
            .first()
        )

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        if ticket.status != "available":
            raise HTTPException(status_code=400, detail="Ticket is not available")

        seat = (
            db.query(Seat)
            .filter(Seat.id == ticket.seat_id)
            .with_for_update()
            .first()
        )

        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found")

        if seat.status != "available":
            raise HTTPException(status_code=400, detail="Seat is not available")

        ticket.status = "reserved"
        seat.status = "reserved"

        reservation = Reservation(
            ticket_id=ticket.id,
            user_id=reservation_data.user_id,
            status="active"
        )

        db.add(reservation)
        db.flush()

        order = Order(
            reservation_id=reservation.id,
            user_id=reservation_data.user_id,
            total_amount=ticket.price,
            status="pending_payment"
        )

        db.add(order)
        db.commit()
        db.refresh(reservation)
        db.refresh(order)

        return {
            "message": "Ticket reserved successfully",
            "reservation_id": reservation.id,
            "order_id": order.id,
            "ticket_id": ticket.id,
            "seat_id": seat.id,
            "amount": ticket.price,
            "expires_at": reservation.expires_at,
            "status": reservation.status
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/reservations")
def get_user_reservations(user_id: int, db: Session = Depends(get_db)):
    return db.query(Reservation).filter(Reservation.user_id == user_id).all()


@router.post("/reservations/expire")
def expire_old_reservations(db: Session = Depends(get_db)):
    now = datetime.utcnow()

    expired_reservations = (
        db.query(Reservation)
        .filter(
            Reservation.status == "active",
            Reservation.expires_at < now
        )
        .all()
    )

    for reservation in expired_reservations:
        ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()
        order = db.query(Order).filter(Order.reservation_id == reservation.id).first()

        if ticket:
            seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()
            ticket.status = "available"

            if seat:
                seat.status = "available"

        reservation.status = "expired"

        if order:
            order.status = "cancelled"

    db.commit()

    return {
        "message": "Expired reservations released",
        "expired_count": len(expired_reservations)
    }