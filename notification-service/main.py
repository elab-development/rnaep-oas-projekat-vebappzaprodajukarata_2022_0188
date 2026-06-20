from fastapi.middleware.cors import CORSMiddleware
from security import get_current_user_id, get_current_user_role
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/")
def root():
    return {"message": "Notification Service is running"}

@app.get("/notifications")
def get_all_notifications(
     current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role)
):
    # Dohvatamo sve email logove iz MongoDB
    # IDOR zaštita - korisnik vidi samo svoje notifikacije, osim ako je admin
    if current_user_role == "admin":
        notifications = list(email_logs.find({}, {'_id': 0}))
    else:
        notifications = list(email_logs.find({'user_id': current_user_id}, {'_id': 0}))
    return notifications