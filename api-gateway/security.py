import os
import httpx
import pybreaker
from jose import jwt, JWTError
from fastapi import HTTPException, Header
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

# Circuit Breaker za User Service
# Otvara se nakon 5 grešaka, pokušava ponovo nakon 30 sekundi
user_service_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30
)


def decode_token(authorization: str | None = Header(default=None)):
    # Provjera da je header prisutan i da je u formatu "Bearer <token>"
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        # Dekodiramo JWT koristeći isti SECRET_KEY kao User Service
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@user_service_breaker
def _call_user_service(authorization: str):
    """Poziv ka User Service-u zaštićen Circuit Breaker-om."""
    response = httpx.get(
        f"{USER_SERVICE_URL}/api/auth/me",
        headers={"Authorization": authorization},
        timeout=5.0
    )
    return response

def get_user_role(authorization: str | None = Header(default=None)) -> str:
    # Pozivamo User Service /api/auth/me rutu da dobijemo ulogu korisnika
    # Prosleđujemo isti Authorization header koji je front poslao Gateway-u
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        response = _call_user_service(authorization)

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Could not verify user")

        user_data = response.json()
        roles = user_data.get("roles", [])

        # Vraća "admin" ako korisnik ima tu ulogu,  inače "user"
        return "admin" if "admin" in roles else "user"

    except pybreaker.CircuitBreakerError:
        # Circuit Breaker je otvoren - User Service nije dostupan
        raise HTTPException(
            status_code=503,
            detail="User Service trenutno nije dostupan. Pokušajte ponovo kasnije."
        )