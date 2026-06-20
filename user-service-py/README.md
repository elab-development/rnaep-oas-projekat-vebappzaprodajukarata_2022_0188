# User Microservice (FastAPI)

Mikroservis za korisnike — registracija, autentifikacija (JWT), upravljanje profilom, password reset i upravljanje korisnicima sa ulogama (role-based access). Deo mikroservisne aplikacije za prodaju karata.

## Tehnologije

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **MySQL** — baza (Database per service)
- **JWT** (python-jose) — autentifikacija
- **bcrypt** (passlib) — heširanje lozinki
- **pytest** — testovi

## Preduslovi

- Python 3.11+
- MySQL (npr. preko Laragon-a)

## Pokretanje (lokalno)

```bash
# 1. Uđi u folder
cd user-service

# 2. Napravi virtuelno okruženje
python -m venv venv

# Aktiviraj ga:
#   Windows (Git Bash):  source venv/Scripts/activate
#   Windows (CMD):       venv\Scripts\activate
#   Mac/Linux:           source venv/bin/activate

# 3. Instaliraj zavisnosti
pip install -r requirements.txt

# 4. Napravi .env
cp .env.example .env      # Windows: copy .env.example .env
# Uredi .env: DB_USERNAME=root, DB_PASSWORD= (prazno za Laragon)

# 5. Napravi bazu u MySQL-u (npr. kroz Laragon Database / HeidiSQL):
#    CREATE DATABASE users_db;

# 6. Kreiraj tabele i test korisnike
python -m app.seed

# 7. Pokreni server
uvicorn app.main:app --reload --port 8001
```

Server radi na `http://localhost:8001`.
Interaktivna dokumentacija (Swagger): `http://localhost:8001/docs`

## Testovi

```bash
pytest
```

Testovi koriste SQLite u memoriji — ne treba MySQL za pokretanje testova.

## Test korisnici (kreiraju se sa `python -m app.seed`)

| Email | Lozinka | Uloga |
|-------|---------|-------|
| admin@example.com | Admin123! | admin |
| user@example.com | User123! | user |
| aleksandra@example.com | Aleksandra123! | user |
| janja@example.com | Janja123! | user |
| milica@example.com | Milica123! | user |

## API rute

### Javne
- `POST /api/auth/register` — registracija
- `POST /api/auth/login` — login (vraća JWT token)
- `POST /api/auth/forgot-password` — zahtev za reset lozinke
- `POST /api/auth/reset-password` — reset lozinke
- `POST /api/auth/validate-reset-token` — provera reset tokena
- `GET /api/health` — health check

### Zaštićene (Authorization: Bearer TOKEN)
- `GET /api/auth/me` — moj profil
- `PUT /api/auth/profile` — izmena profila
- `POST /api/auth/logout` — odjava

### Admin
- `GET /api/users` — lista korisnika
- `GET /api/users/search?q=...` — pretraga
- `GET /api/users/{id}` — jedan korisnik
- `PUT /api/users/{id}` — izmena
- `DELETE /api/users/{id}` — brisanje
- `POST /api/users/{id}/assign-role` — dodela uloge
- `DELETE /api/users/{id}/remove-role` — uklanjanje uloge
- `GET /api/users/statistics/count` — broj korisnika

## Docker

```bash
docker-compose up -d
docker-compose exec user-service python -m app.seed
```

Server: `http://localhost:8001`
