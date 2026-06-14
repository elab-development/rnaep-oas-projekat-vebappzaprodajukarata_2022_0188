"""
Pydantic šeme - definišu oblik podataka koji ulaze i izlaze iz API-ja.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Korisnik ----------

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserRegister(UserBase):
    password: str = Field(min_length=8)
    password_confirmation: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    roles: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ---------- Token ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    user: UserOut
    token: str
    token_type: str = "bearer"
    expires_in: int


# ---------- Password reset ----------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8)
    password_confirmation: str


class ValidateTokenRequest(BaseModel):
    token: str


# ---------- Uloge ----------

class RoleAssign(BaseModel):
    role: str  # 'admin', 'user', 'guest'


# ---------- Opšti odgovori ----------

class MessageResponse(BaseModel):
    message: str
