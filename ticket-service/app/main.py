from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routes import tickets
from app.kafka_consumer import consume_payment_events
from app.reservation_cleanup import start_reservation_cleanup_worker
import threading
from app.exceptions import (
    TicketNotFoundException,
    SeatNotAvailableException,
    ticket_not_found_handler,
    seat_not_available_handler,
    validation_exception_handler
)

from fastapi.exceptions import RequestValidationError



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ticket Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)


@app.get("/")
def root():
    return {"message": "Ticket Service is running"}


@app.on_event("startup")
def startup_event():
    consumer_thread = threading.Thread(
        target=consume_payment_events,
        daemon=True
    )
    consumer_thread.start()
    cleanup_thread = threading.Thread(
    target=start_reservation_cleanup_worker,
    daemon=True
    )
    cleanup_thread.start()

app.add_exception_handler(
    TicketNotFoundException,
    ticket_not_found_handler
)

app.add_exception_handler(
    SeatNotAvailableException,
    seat_not_available_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)