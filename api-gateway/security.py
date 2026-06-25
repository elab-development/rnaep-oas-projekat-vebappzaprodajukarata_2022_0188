import os
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, Header
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")


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


def get_user_role(authorization: str | None = Header(default=None)) -> str:
    # Pozivamo User Service /api/auth/me rutu da dobijemo ulogu korisnika
    # Prosleđujemo isti Authorization header koji je front poslao Gateway-u
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    response = httpx.get(
        f"{USER_SERVICE_URL}/api/auth/me",
        headers={"Authorization": authorization}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Could not verify user")

    user_data = response.json()
    roles = user_data.get("roles", [])

    # Vraća "admin" ako korisnik ima tu ulogu,  inače "user"
    return "admin" if "admin" in roles else "user"
