"""
Konekcija sa bazom podataka (SQLAlchemy).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Engine - veza sa MySQL bazom
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Session factory - kreira sesije za rad sa bazom
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Bazna klasa za sve modele
Base = declarative_base()


def get_db():
    """
    Dependency - daje sesiju baze za jedan zahtev, pa je zatvara.
    Koristi se u rutama preko Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
