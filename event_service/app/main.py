from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routes.events import router as events_router
from app.routes.venues import router as venues_router
from app.routes.categories import router as categories_router
from fastapi.exceptions import RequestValidationError

from app.exceptions import (
    EventNotFoundException,
    VenueNotFoundException,
    CategoryNotFoundException,
    event_not_found_handler,
    venue_not_found_handler,
    category_not_found_handler,
    validation_exception_handler
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Service")

app.add_exception_handler(EventNotFoundException, event_not_found_handler)
app.add_exception_handler(VenueNotFoundException, venue_not_found_handler)
app.add_exception_handler(CategoryNotFoundException, category_not_found_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

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

app.include_router(events_router)
app.include_router(venues_router)
app.include_router(categories_router)


@app.get("/")
def root():
    return {"message": "Event Service is running"}


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "event-service"
    }