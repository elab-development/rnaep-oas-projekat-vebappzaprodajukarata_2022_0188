from pydantic import BaseModel
from datetime import datetime


class SeatCreate(BaseModel):
    event_id: int
    row_label: str
    seat_number: int


class SeatResponse(BaseModel):
    id: int
    event_id: int
    row_label: str
    seat_number: int
    status: str

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    event_id: int
    seat_id: int
    price: float


class TicketResponse(BaseModel):
    id: int
    event_id: int
    seat_id: int
    price: float
    status: str

    class Config:
        from_attributes = True


class ReservationCreate(BaseModel):
    ticket_id: int
    user_id: int


class ReservationResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    status: str
    expires_at: datetime
    order_id: int
    amount: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    reservation_id: int
    user_id: int
    total_amount: float
    payment_id: int | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True