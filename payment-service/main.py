from security import get_current_user_id, get_current_user_role
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, Payment, PaymentMethod, Refund, Transaction
from pydantic import BaseModel, ConfigDict
from datetime import datetime, UTC
from typing import Optional
from kafka_producer import send_payment_completed, send_payment_failed, send_payment_refunded

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kreira tabele u bazi podataka ako ne postoje
    # Izvršava se prije yield (pri pokretanju servisa)
    Base.metadata.create_all(bind=engine)
    yield
    # Ovde bi išlo gasenje resursa, ako bi nam trebalo (nakon yield)

app = FastAPI(title="Payment Service", lifespan=lifespan)

# Pydantic šeme za validaciju ulaznih podataka
class PaymentCreate(BaseModel):
    reservation_id: int
    user_id: int
    payment_method_id: int
    amount: float
    user_email: str
    event_name: str
    event_date: str
    venue_name: str
    venue_address: str

class RefundCreate(BaseModel):
    payment_id: int
    amount: float
    user_email: str

# Pydantic šeme za serijalizaciju izlaznih podataka
# Bez ovih modela, FastAPI ne zna automatski kako da pretvori
# SQLAlchemy objekat u JSON odgovor
class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    user_id: int
    payment_method_id: int
    amount: float
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None

class RefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: int
    amount: float
    status: str
    refunded_at: Optional[datetime] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: int
    amount: float
    status: str
    processed_at: Optional[datetime] = None


# Payment endpointi
@app.get("/")
def root():
    return {"message": "Payment Service is running"}

@app.get("/payments", response_model=list[PaymentResponse])
def get_all_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()

@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role)
    ):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    # IDOR zaštita - korisnik može vidjeti samo svoje plaćanje, osim ako je admin
    if current_user_role != "admin" and payment.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return payment

@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    payment = Payment(
        reservation_id=payment_data.reservation_id,
        user_id=payment_data.user_id,
        payment_method_id=payment_data.payment_method_id,
        amount=payment_data.amount,
        status="pending"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    try:
        # Kreiranje transakcije
        transaction = Transaction(
            payment_id=payment.id,
            amount=payment_data.amount,
            status="pending",
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # Simulacija uspješnog plaćanja
        payment.status = "paid"
        payment.paid_at = datetime.now(UTC)
        transaction.status = "success"
        transaction.processed_at = datetime.now(UTC)
        db.commit()

        # Šalji payment.completed event na Kafka
        send_payment_completed(
            payment, 
            payment_data.user_email,
            payment_data.event_name,
            payment_data.event_date,
            payment_data.venue_name,
            payment_data.venue_address
        )

    except Exception as e:
        # Ako plaćanje nije uspjelo
        payment.status = "not_paid"
        transaction.status = "failed"
        transaction.processed_at = datetime.now(UTC)
        db.commit()

        # Šalji payment.failed event na Kafka
        send_payment_failed(payment, payment_data.user_email, str(e))

        raise HTTPException(status_code=500, detail=str(e))

    return payment

# Refund endpointi
@app.get("/refunds", response_model=list[RefundResponse])
def get_all_refunds(db: Session = Depends(get_db)):
    return db.query(Refund).all()

@app.post("/refunds", response_model=RefundResponse)
def create_refund(refund_data: RefundCreate, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == refund_data.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != "paid":
        raise HTTPException(status_code=400, detail="Payment is not paid")

    refund = Refund(
        payment_id=refund_data.payment_id,
        amount=refund_data.amount,
        status="pending"
    )
    db.add(refund)

    try:
        # Simulacija obrade refunda
        refund.status = "success"
        refund.refunded_at = datetime.now(UTC)
        payment.status = "refunded"
        db.commit()
        db.refresh(refund)

        # Šalji payment.refunded event na Kafka
        send_payment_refunded(refund, payment.user_id, refund_data.user_email)

    except Exception as e:
        # Ako refundacija nije uspjela
        refund.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    return refund

# Transaction endpointi
@app.get("/transactions", response_model=list[TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction