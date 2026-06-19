from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import email_logs
from kafka_consumer import process_messages
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pokrecemo consumer u posebnoj niti kako bi radio u pozadini
    # dok FastAPI servis normalno prima zahteve
    thread = threading.Thread(target=process_messages, daemon=True)
    thread.start()
    yield

app = FastAPI(title="Notification Service")

@app.get("/")
def root():
    return {"message": "Notification Service is running"}

@app.get("/notifications")
def get_all_notifications():
    # Dohvatamo sve email logove iz MongoDB
    notifications = list(email_logs.find({}, {'_id': 0}))
    return notifications