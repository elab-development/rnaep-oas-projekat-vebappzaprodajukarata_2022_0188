"""
Seed skripta - kreira tabele i ubacuje početne podatke (uloge + test korisnici).
Pokreni sa:  python -m app.seed
"""
from app.database import Base, engine, SessionLocal
from app.models import Role, User
from app.security import hash_password


def seed():
    # Kreiraj sve tabele
    Base.metadata.create_all(bind=engine)
    print("✓ Tabele kreirane")

    db = SessionLocal()
    try:
        # Uloge
        role_names = {
            "guest": "Neregistrovani korisnik",
            "user": "Registrovani korisnik",
            "admin": "Administrator",
        }
        roles = {}
        for name, desc in role_names.items():
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name, description=desc)
                db.add(role)
                db.commit()
                db.refresh(role)
            roles[name] = role
        print("✓ Uloge kreirane")

        # Test korisnici
        test_users = [
            ("Admin", "admin@example.com", "Admin123!", "admin"),
            ("Obični Korisnik", "user@example.com", "User123!", "user"),
            ("Aleksandra", "aleksandra@example.com", "Aleksandra123!", "user"),
            ("Janja", "janja@example.com", "Janja123!", "user"),
            ("Milica", "milica@example.com", "Milica123!", "user"),
        ]
        for name, email, pwd, role_name in test_users:
            if not db.query(User).filter(User.email == email).first():
                user = User(name=name, email=email, password=hash_password(pwd))
                user.roles.append(roles[role_name])
                db.add(user)
                db.commit()
        print("✓ Test korisnici kreirani")
        print("\nMožeš se prijaviti sa: admin@example.com / Admin123!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
