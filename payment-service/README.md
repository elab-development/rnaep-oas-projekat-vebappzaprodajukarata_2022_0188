# Payment Service

## Pregled

Payment Service je zadužen za obradu plaćanja, refundacija i transakcija na platformi za prodaju ulaznica. Pruža CRUD operacije za kreiranje i pregled plaćanja, kao i obradu refundacija povezanih sa izvršenim plaćanjima.

Servis je implementiran korišćenjem FastAPI okvira i prati Database per Service mikroservisni arhitektonski patern.

---

## Tehnologije

- Python 3.13
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Apache Kafka (kafka-python)
- Pytest
- GitHub Actions
- SQLite (koristi se za testiranje)

---

## Baza podataka

Naziv baze:

```text
payment_db
```

Servis koristi sopstvenu bazu podataka u skladu sa Database per Service paternom.

---

## Entiteti

### Payment

- id
- reservation_id
- user_id
- payment_method_id
- amount
- status (pending, paid, not_paid, refunded)
- created_at
- paid_at

### PaymentMethod

- id
- name

### Transaction

- id
- payment_id
- amount
- status (pending, success, failed)
- processed_at

### Refund

- id
- payment_id
- amount
- status (pending, success, failed)
- refunded_at

---

## Relacije

```text
PaymentMethod 1 ---- N Payment
Payment 1 ---- N Transaction
Payment 1 ---- N Refund
```

---

## Pokretanje servisa

Aktivacija virtuelnog okruženja:

```bash
.\venv\Scripts\activate
```

Instalacija zavisnosti:

```bash
pip install -r requirements.txt
```

Pokretanje servisa:

```bash
uvicorn main:app --reload
```

Swagger dokumentacija:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpointi

### Payments

- POST /payments
- GET /payments
- GET /payments/{payment_id}

### Refunds

- POST /refunds
- GET /refunds

### Transactions

- GET /transactions
- GET /transactions/{transaction_id}

---

## Komunikacija sa drugim servisima

Payment Service komunicira sa Ticket Service-om i Notification Service-om asinhrono, putem Apache Kafka platforme.

Kafka topici koje servis proizvodi:

- `payment.completed` - emituje se nakon uspešnog plaćanja
- `payment.failed` - emituje se nakon neuspešnog plaćanja
- `payment.refunded` - emituje se nakon uspešne refundacije

Ticket Service konzumira `payment.completed` i `payment.failed` topice radi potvrde ili otkazivanja rezervacije (Saga patern, kompenzacione akcije). Notification Service konzumira sva tri topica radi slanja email obaveštenja korisnicima.

---

## Bezbednost

Servis implementira:

- CORS konfiguraciju
- Zaštitu od SQL Injection napada kroz SQLAlchemy ORM
- IDOR zaštitu - korisnik može pristupiti samo svojim plaćanjima, refundacijama i transakcijama, osim ako ima administratorsku ulogu
- XSS zaštitu - tekstualna polja koja se prosleđuju u email obaveštenja se enkodiraju (html.escape)
- Validaciju ulaznih podataka pomoću Pydantic šema

Identitet korisnika se utvrđuje putem header-a koje prosleđuje API Gateway:

```text
X-User-Id: <id korisnika>
X-User-Role: <uloga korisnika>
```

---

## Testiranje

Testovi su implementirani korišćenjem Pytest biblioteke. Kafka funkcionalnosti su mock-ovane tokom testiranja kako testovi ne bi zahtevali pravu Kafka konekciju.

Pokretanje testova:

```bash
PYTHONPATH=.:.. pytest -v
```

---

## Kontinuirana integracija

GitHub Actions se koristi za automatsko pokretanje testova prilikom svakog push-a i pull request-a na glavne grane.

---

## Monitoring

Servis izlaže `/metrics` endpoint koji koristi Prometheus za prikupljanje telemetrijskih podataka (broj HTTP zahteva, trajanje obrade, status kodovi) .
