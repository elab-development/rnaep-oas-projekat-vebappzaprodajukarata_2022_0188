"""
SQLAlchemy modeli - tabele u bazi podataka.
"""
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


# Pivot (asocijativna) tabela za vezu User <-> Role (mnogo prema mnogo)
role_user = Table(
    "role_user",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # heširana lozinka
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Veze
    roles = relationship("Role", secondary=role_user, back_populates="users")
    password_resets = relationship(
        "PasswordReset", back_populates="user", cascade="all, delete-orphan"
    )

    def has_role(self, role_name: str) -> bool:
        """Proverava da li korisnik ima zadatu ulogu."""
        return any(role.name == role_name for role in self.roles)

    def role_names(self) -> list[str]:
        """Vraća imena svih uloga korisnika."""
        return [role.name for role in self.roles]


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)  # 'guest', 'user', 'admin'
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", secondary=role_user, back_populates="roles")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reset_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="password_resets")

    def is_valid(self) -> bool:
        """Token je validan ako nije korišćen i nije istekao."""
        return self.used_at is None and self.expires_at > datetime.utcnow()
