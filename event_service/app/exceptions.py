from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class EventNotFoundException(Exception):
    pass


class VenueNotFoundException(Exception):
    pass


class CategoryNotFoundException(Exception):
    pass


async def event_not_found_handler(request: Request, exc: EventNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Event not found"}
    )


async def venue_not_found_handler(request: Request, exc: VenueNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Venue not found"}
    )


async def category_not_found_handler(request: Request, exc: CategoryNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Category not found"}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )