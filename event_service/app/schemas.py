# from pydantic import BaseModel
# from datetime import datetime
# from typing import Optional


# # ---------------- VENUE ----------------

# class VenueCreate(BaseModel):
#     name: str
#     address: str
#     city: str
#     capacity: int


# class VenueResponse(BaseModel):
#     id: int
#     name: str
#     address: str
#     city: str
#     capacity: int
#     latitude: float | None = None
#     longitude: float | None = None

#     class Config:
#         from_attributes = True


# # ---------------- CATEGORY ----------------

# class CategoryCreate(BaseModel):
#     name: str
#     description: str | None = None


# class CategoryResponse(BaseModel):
#     id: int
#     name: str
#     description: str | None = None

#     class Config:
#         from_attributes = True


# # ---------------- EVENT ----------------

# class EventCreate(BaseModel):
#     title: str
#     description: str | None = None
#     start_time: datetime
#     end_time: datetime
#     venue_id: int
#     category_id: int


# class EventResponse(BaseModel):
#     id: int
#     title: str
#     description: str | None = None
#     start_time: datetime
#     end_time: datetime
#     status: str
#     venue_id: int
#     category_id: int
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

from pydantic import BaseModel
from datetime import datetime


# ---------------- VENUE ----------------

class VenueCreate(BaseModel):
    name: str
    address: str
    city: str
    capacity: int


class VenueResponse(BaseModel):
    id: int
    name: str
    address: str
    city: str
    capacity: int
    latitude: float | None = None
    longitude: float | None = None

    class Config:
        from_attributes = True


# ---------------- CATEGORY ----------------

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


# ---------------- EVENT ----------------

class EventCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    venue_id: int
    category_id: int


class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    status: str
    venue_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    venue: VenueResponse
    category: CategoryResponse

    class Config:
        from_attributes = True