from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.security import get_current_user_id
from app.database import get_db
from app.models import Ticket, Seat, Reservation, Order
from app.schemas import ReservationCreate, SeatCreate
from app.exceptions import SeatNotAvailableException, TicketNotFoundException

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/")
def get_all_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()


@router.get("/event/{event_id}")
def get_tickets_by_event(event_id: int, db: Session = Depends(get_db)):
    return db.query(Ticket).filter(Ticket.event_id == event_id).all()


@router.get("/event/{event_id}/seats")
def get_event_seats(event_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Seat)
        .filter(Seat.event_id == event_id)
        .order_by(Seat.row_label, Seat.seat_number)
        .all()
    )


@router.post("/seats")
def create_seat_with_ticket(
    seat_data: SeatCreate,
    db: Session = Depends(get_db),
):
    existing_seat = (
        db.query(Seat)
        .filter(
            Seat.event_id == seat_data.event_id,
            Seat.row_label == seat_data.row_label,
            Seat.seat_number == seat_data.seat_number,
        )
        .first()
    )

    if existing_seat:
        raise HTTPException(status_code=400, detail="Seat already exists for this event")

    seat = Seat(
        event_id=seat_data.event_id,
        row_label=seat_data.row_label,
        seat_number=seat_data.seat_number,
        status="available",
    )

    db.add(seat)
    db.flush()

    ticket = Ticket(
        event_id=seat_data.event_id,
        seat_id=seat.id,
        price=seat_data.price,
        status="available",
    )

    db.add(ticket)
    db.commit()
    db.refresh(seat)
    db.refresh(ticket)

    return {
        "message": "Seat and ticket created successfully",
        "seat": seat,
        "ticket": ticket,
    }


@router.get("/my/reservations")
def get_my_reservations(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return db.query(Reservation).filter(Reservation.user_id == current_user_id).all()


@router.get("/my/orders")
def get_my_orders(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return db.query(Order).filter(Order.user_id == current_user_id).all()


@router.get("/user/{user_id}/reservations")
def get_user_reservations(user_id: int, db: Session = Depends(get_db)):
    return db.query(Reservation).filter(Reservation.user_id == user_id).all()


@router.get("/reservations/{reservation_id}")
def get_reservation(
    reservation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id == reservation_id,
            Reservation.user_id == current_user_id,
        )
        .first()
    )

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return reservation


@router.get("/reservations/{reservation_id}/order")
def get_order_by_reservation(
    reservation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .join(Reservation)
        .filter(
            Reservation.id == reservation_id,
            Reservation.user_id == current_user_id,
        )
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user_id,
        )
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.get("/my/tickets")
def get_my_tickets(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    reservations = (
        db.query(Reservation)
        .filter(Reservation.user_id == current_user_id)
        .all()
    )

    result = []

    for reservation in reservations:
        ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()
        order = db.query(Order).filter(Order.reservation_id == reservation.id).first()

        if not ticket:
            continue

        seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()

        result.append({
            "reservation_id": reservation.id,
            "order_id": order.id if order else None,
            "ticket_id": ticket.id,
            "event_id": ticket.event_id,
            "seat_id": seat.id if seat else None,
            "row_label": seat.row_label if seat else None,
            "seat_number": seat.seat_number if seat else None,
            "price": ticket.price,
            "ticket_status": ticket.status,
            "reservation_status": reservation.status,
            "order_status": order.status if order else None,
            "expires_at": reservation.expires_at,
            "created_at": reservation.created_at,
            "paid_at": order.paid_at if order else None,
        })

    return result


@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise TicketNotFoundException()

    return ticket


@router.post("/reserve")
def reserve_ticket(
    reservation_data: ReservationCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        ticket = (
            db.query(Ticket)
            .filter(Ticket.id == reservation_data.ticket_id)
            .with_for_update()
            .first()
        )

        if not ticket:
            raise TicketNotFoundException()

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
            raise SeatNotAvailableException()

        ticket.status = "reserved"
        seat.status = "reserved"

        reservation = Reservation(
            ticket_id=ticket.id,
            user_id=current_user_id,
            status="active",
        )

        db.add(reservation)
        db.flush()

        order = Order(
            reservation_id=reservation.id,
            user_id=current_user_id,
            total_amount=ticket.price,
            status="pending_payment",
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
            "reservation_status": reservation.status,
            "order_status": order.status,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reservations/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id == reservation_id,
            Reservation.user_id == current_user_id,
        )
        .first()
    )

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if reservation.status != "active":
        raise HTTPException(status_code=400, detail="Reservation cannot be cancelled")

    ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()
    order = db.query(Order).filter(Order.reservation_id == reservation.id).first()

    if ticket:
        ticket.status = "available"

        seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()
        if seat:
            seat.status = "available"

    reservation.status = "cancelled"

    if order:
        order.status = "cancelled"

    db.commit()

    return {
        "message": "Reservation cancelled successfully",
        "reservation_id": reservation.id,
        "status": reservation.status,
    }


@router.post("/reservations/expire")
def expire_old_reservations(db: Session = Depends(get_db)):
    now = datetime.utcnow()

    expired_reservations = (
        db.query(Reservation)
        .filter(
            Reservation.status == "active",
            Reservation.expires_at < now,
        )
        .all()
    )

    for reservation in expired_reservations:
        ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()
        order = db.query(Order).filter(Order.reservation_id == reservation.id).first()

        if ticket:
            ticket.status = "available"

            seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()
            if seat:
                seat.status = "available"

        reservation.status = "expired"

        if order:
            order.status = "cancelled"

    db.commit()

    return {
        "message": "Expired reservations released",
        "expired_count": len(expired_reservations),
    }

@router.post("/orders/{order_id}/confirm-payment")
def confirm_payment(
    order_id: int,
    payment_id: int,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")

    reservation = db.query(Reservation).filter(
        Reservation.id == order.reservation_id
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()

    if not ticket:
        raise TicketNotFoundException()

    reservation.status = "confirmed"
    order.status = "paid"
    order.payment_id = payment_id
    order.paid_at = datetime.utcnow()
    ticket.status = "sold"

    seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()
    if seat:
        seat.status = "sold"

    db.commit()

    return {
        "message": "Payment confirmed successfully",
        "order_id": order.id,
        "reservation_id": reservation.id,
        "ticket_id": ticket.id,
        "status": order.status,
    }

@router.post("/orders/{order_id}/fail-payment")
def fail_payment(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    reservation = db.query(Reservation).filter(
        Reservation.id == order.reservation_id
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()

    if not ticket:
        raise TicketNotFoundException()

    order.status = "failed"
    reservation.status = "cancelled"
    ticket.status = "available"

    seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()
    if seat:
        seat.status = "available"

    db.commit()

    return {
        "message": "Payment failed, ticket released",
        "order_id": order.id,
        "reservation_id": reservation.id,
        "ticket_id": ticket.id,
    }

