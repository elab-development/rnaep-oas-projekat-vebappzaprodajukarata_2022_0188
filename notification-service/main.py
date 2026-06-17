from fastapi import FastAPI
from database import email_logs
from kafka_consumer import process_messages
import threading

app = FastAPI(title="Notification Service")

@app.on_event("startup")
def startup_event():
    # Pokrećemo consumer u posebnoj niti kako bi radio u pozadini
    # dok FastAPI servis normalno prima zahtjeve
    thread = threading.Thread(target=process_messages, daemon=True) # pravimo nit
    thread.start() # pokrećemo nit

@app.get("/")
def root():
    return {"message": "Notification Service is running"}

@app.get("/notifications")
def get_all_notifications():
    # Dohvatamo sve email logove iz MongoDB
    notifications = list(email_logs.find({}, {'_id': 0}))
    return notifications