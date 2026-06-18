from kafka import KafkaConsumer
import json
from datetime import datetime

from app.database import SessionLocal
from app.models import Reservation, Order, Ticket, Seat


consumer = KafkaConsumer(
    "payment.completed",
    "payment.failed",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="ticket-service-group"
)


def handle_payment_completed(data):
    db = SessionLocal()

    try:
        reservation_id = data.get("reservation_id")
        payment_id = data.get("payment_id")

        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

        if not reservation:
            return

        order = db.query(Order).filter(Order.reservation_id == reservation.id).first()
        ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()
        seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()

        reservation.status = "confirmed"

        if order:
            order.status = "paid"
            order.payment_id = payment_id
            order.paid_at = datetime.utcnow()

        ticket.status = "sold"
        seat.status = "sold"

        db.commit()

    finally:
        db.close()


def handle_payment_failed(data):
    db = SessionLocal()

    try:
        reservation_id = data.get("reservation_id")

        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

        if not reservation:
            return

        order = db.query(Order).filter(Order.reservation_id == reservation.id).first()
        ticket = db.query(Ticket).filter(Ticket.id == reservation.ticket_id).first()
        seat = db.query(Seat).filter(Seat.id == ticket.seat_id).first()

        reservation.status = "cancelled"

        if order:
            order.status = "cancelled"

        ticket.status = "available"
        seat.status = "available"

        db.commit()

    finally:
        db.close()


def consume_payment_events():
    print("Ticket Service Kafka consumer started...")

    for message in consumer:
        topic = message.topic
        data = message.value

        if topic == "payment.completed":
            handle_payment_completed(data)

        elif topic == "payment.failed":
            handle_payment_failed(data)