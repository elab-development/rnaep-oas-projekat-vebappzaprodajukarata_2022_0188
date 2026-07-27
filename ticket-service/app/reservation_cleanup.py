import time
from datetime import datetime

from app.database import SessionLocal
from app.models import Reservation, Order, Ticket, Seat


def expire_old_reservations():
    db = SessionLocal()

    try:
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

    finally:
        db.close()


def start_reservation_cleanup_worker():
    while True:
        expire_old_reservations()
        time.sleep(60)