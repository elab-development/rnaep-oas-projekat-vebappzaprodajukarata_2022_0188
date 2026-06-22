from shared.logger import setup_metrics
import os
import httpx
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from security import decode_token, get_user_role

load_dotenv()

# Adrese mikroservisa - unutar Dockera koriste se imena kontejnera,
# lokalno se mogu koristiti localhost adrese sa različitim portovima
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service:8000")
TICKET_SERVICE_URL = os.getenv("TICKET_SERVICE_URL", "http://ticket-service:8000")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

setup_metrics(app, "api-gateway")

async def proxy_request(request: Request, target_url: str, extra_headers: dict = None):
    # Prosleđujemo zahtjev ka odgovarajućem mikroservisu i vraćamo njegov odgovor
    # extra_headers koristimo da dodamo X-User-Id/X-User-Role prije prosleđivanja
    headers = dict(request.headers)
    headers.pop("host", None)  # Uklanjamo host header da ne zbuni ciljani servis
    if extra_headers:
        headers.update(extra_headers)

    body = await request.body()

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=30.0
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )


@app.get("/")
def root():
    return {"message": "API Gateway is running"}


# ---------------- USER SERVICE ----------------
# User Service sam dekodira JWT (Authorization header), pa zahtjev
# prosleđujemo direktno, bez ikakvih izmjena

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth(path: str, request: Request):
    target_url = f"{USER_SERVICE_URL}/api/auth/{path}"
    return await proxy_request(request, target_url)


@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_users(path: str, request: Request):
    target_url = f"{USER_SERVICE_URL}/api/users/{path}"
    return await proxy_request(request, target_url)


# ---------------- EVENT SERVICE ----------------
# Event Service očekuje X-User-Role header, pa ga dodajemo prije prosleđivanja

@app.api_route("/api/events/{path:path}", methods=["GET"])
async def proxy_events_get(path: str, request: Request):
    target_url = f"{EVENT_SERVICE_URL}/events/{path}"
    return await proxy_request(request, target_url)


@app.api_route("/api/events/{path:path}", methods=["POST", "PUT", "DELETE", "PATCH"])
async def proxy_events_admin(path: str, request: Request, user_role: str = Depends(get_user_role)):
    target_url = f"{EVENT_SERVICE_URL}/events/{path}"
    return await proxy_request(request, target_url, extra_headers={"X-User-Role": user_role})


@app.api_route("/api/venues/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_venues(path: str, request: Request, user_role: str = Depends(get_user_role)):
    target_url = f"{EVENT_SERVICE_URL}/venues/{path}"
    return await proxy_request(request, target_url, extra_headers={"X-User-Role": user_role})


@app.api_route("/api/categories/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_categories(path: str, request: Request, user_role: str = Depends(get_user_role)):
    target_url = f"{EVENT_SERVICE_URL}/categories/{path}"
    return await proxy_request(request, target_url, extra_headers={"X-User-Role": user_role})


# ---------------- TICKET SERVICE ----------------
# Ticket Service očekuje X-User-Id header, pa ga dodajemo prije prosleđivanja

# ---------------- TICKET SERVICE ----------------

@app.api_route("/api/tickets/my/{path:path}", methods=["GET"])
async def proxy_my_tickets_get(
    path: str,
    request: Request,
    user_id: int = Depends(decode_token),
):
    target_url = f"{TICKET_SERVICE_URL}/tickets/my/{path}"
    return await proxy_request(
        request,
        target_url,
        extra_headers={"X-User-Id": str(user_id)},
    )


@app.api_route("/api/tickets/{path:path}", methods=["GET"])
async def proxy_tickets_get(path: str, request: Request):
    target_url = f"{TICKET_SERVICE_URL}/tickets/{path}"
    return await proxy_request(request, target_url)


@app.api_route("/api/tickets/{path:path}", methods=["POST", "PUT", "DELETE", "PATCH"])
async def proxy_tickets_protected(
    path: str,
    request: Request,
    user_id: int = Depends(decode_token),
):
    target_url = f"{TICKET_SERVICE_URL}/tickets/{path}"
    return await proxy_request(
        request,
        target_url,
        extra_headers={"X-User-Id": str(user_id)},
    )


# ---------------- PAYMENT SERVICE ----------------
# Payment Service očekuje i X-User-Id i X-User-Role header

@app.api_route("/api/payments/{path:path}", methods=["GET", "POST"])
async def proxy_payments(
    path: str,
    request: Request,
    user_id: int = Depends(decode_token),
    user_role: str = Depends(get_user_role)
):
    target_url = f"{PAYMENT_SERVICE_URL}/payments/{path}"
    return await proxy_request(
        request, target_url,
        extra_headers={"X-User-Id": str(user_id), "X-User-Role": user_role}
    )


@app.api_route("/api/refunds/{path:path}", methods=["GET", "POST"])
async def proxy_refunds(
    path: str,
    request: Request,
    user_id: int = Depends(decode_token),
    user_role: str = Depends(get_user_role)
):
    target_url = f"{PAYMENT_SERVICE_URL}/refunds/{path}"
    return await proxy_request(
        request, target_url,
        extra_headers={"X-User-Id": str(user_id), "X-User-Role": user_role}
    )


@app.api_route("/api/transactions/{path:path}", methods=["GET"])
async def proxy_transactions(
    path: str,
    request: Request,
    user_id: int = Depends(decode_token),
    user_role: str = Depends(get_user_role)
):
    target_url = f"{PAYMENT_SERVICE_URL}/transactions/{path}"
    return await proxy_request(
        request, target_url,
        extra_headers={"X-User-Id": str(user_id), "X-User-Role": user_role}
    )


# ---------------- NOTIFICATION SERVICE ----------------
# Notification Service očekuje i X-User-Id i X-User-Role header

@app.api_route("/api/notifications", methods=["GET"])
async def proxy_notifications(
    request: Request,
    user_id: int = Depends(decode_token),
    user_role: str = Depends(get_user_role)
):
    target_url = f"{NOTIFICATION_SERVICE_URL}/notifications"
    return await proxy_request(
        request, target_url,
        extra_headers={"X-User-Id": str(user_id), "X-User-Role": user_role}
    )