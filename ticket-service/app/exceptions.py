from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class TicketNotFoundException(Exception):
    pass


class SeatNotAvailableException(Exception):
    pass


async def ticket_not_found_handler(
        request: Request,
        exc: TicketNotFoundException
):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ticket not found"}
    )


async def seat_not_available_handler(
        request: Request,
        exc: SeatNotAvailableException
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Seat is not available"}
    )


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )