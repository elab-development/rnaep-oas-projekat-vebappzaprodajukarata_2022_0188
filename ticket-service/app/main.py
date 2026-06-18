from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routes import tickets
from app.kafka_consumer import consume_payment_events

import threading

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ticket Service")

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