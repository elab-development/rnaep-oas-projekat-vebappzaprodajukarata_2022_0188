"""
Glavna FastAPI aplikacija - User Microservice.
Pokreni sa:  uvicorn app.main:app --reload --port 8001
"""
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, users

from shared.logger import setup_metrics

app = FastAPI(
    title="User Microservice",
    description="Mikroservis za korisnike - registracija, autentifikacija, uloge.",
    version="1.0.0",
)

# CORS - dozvoli pristup sa frontend-a
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_metrics(app, "user-service-py")

# Rute
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/api/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "service": "user-microservice",
        "timestamp": datetime.utcnow(),
    }
