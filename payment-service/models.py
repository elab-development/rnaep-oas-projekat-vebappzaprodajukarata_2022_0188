from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from datetime import datetime, UTC

Base = declarative_base()

def utc_now():
    return datetime.now(UTC)

class PaymentMethod(Base):
    __tablename__ = 'payment_method'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    payment = relationship("Payment", back_populates="payment_method")

class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, nullable=False)
    payment_method_id = Column(Integer, ForeignKey('payment_method.id'))
    amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, paid, not_paid, refunded
    created_at = Column(DateTime, default=utc_now)
    paid_at = Column(DateTime, nullable=True)

    payment_method = relationship("PaymentMethod", back_populates="payment")
    transaction = relationship("Transaction", back_populates="payment")
    refund = relationship("Refund", back_populates="payment", uselist=False)

class Refund(Base):
    __tablename__ = 'refund'

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey('payment.id'))
    amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False) # pending, success, failed
    refunded_at = Column(DateTime, nullable=True)

    payment = relationship("Payment", back_populates="refund")

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey('payment.id'))
    amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # pending, success, failed
    processed_at = Column(DateTime, nullable=True)

    payment = relationship("Payment", back_populates="transaction")