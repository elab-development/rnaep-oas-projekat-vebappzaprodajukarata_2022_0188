from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from .database import Base


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    row_label = Column(String(10), nullable=False)
    seat_number = Column(Integer, nullable=False)
    status = Column(String(20), default="available")  # available, reserved, sold

    ticket = relationship("Ticket", back_populates="seat", uselist=False)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(20), default="available")  # available, reserved, sold

    seat = relationship("Seat", back_populates="ticket")
    reservations = relationship("Reservation", back_populates="ticket")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    status = Column(String(20), default="active")  # active, confirmed, expired, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))

    ticket = relationship("Ticket", back_populates="reservations")
    order = relationship("Order", back_populates="reservation", uselist=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_id = Column(Integer, nullable=True)
    status = Column(String(30), default="pending_payment")  # pending_payment, paid, cancelled, refunded
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    reservation = relationship("Reservation", back_populates="order")