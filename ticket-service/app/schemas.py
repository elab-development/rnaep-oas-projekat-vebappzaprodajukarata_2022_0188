from pydantic import BaseModel
from datetime import datetime


class SeatCreate(BaseModel):
    event_id: int
    row_label: str
    seat_number: int
    price: float


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


class ReservationResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class ReservationWithOrderResponse(BaseModel):
    message: str
    reservation_id: int
    order_id: int
    ticket_id: int
    seat_id: int
    amount: float
    expires_at: datetime
    reservation_status: str
    order_status: str


class OrderResponse(BaseModel):
    id: int
    reservation_id: int
    user_id: int
    total_amount: float
    payment_id: int | None = None
    status: str
    created_at: datetime
    paid_at: datetime | None = None

    class Config:
        from_attributes = True


class SeatWithTicketResponse(BaseModel):
    message: str
    seat: SeatResponse
    ticket: TicketResponse