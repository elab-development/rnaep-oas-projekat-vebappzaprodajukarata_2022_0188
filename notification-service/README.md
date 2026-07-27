# Notification Service

## Pregled

Notification Service je zadužen za slanje email obaveštenja korisnicima platforme za prodaju ulaznica. Servis asinhrono prima događaje o plaćanjima putem Apache Kafka platforme i na osnovu njih šalje odgovarajuća email obaveštenja (potvrda kupovine, obaveštenje o neuspešnom plaćanju, potvrda refundacije).

Servis je implementiran korišćenjem FastAPI okvira i prati Database per Service mikroservisni arhitektonski patern.

---

## Tehnologije

- Python 3.13
- FastAPI
- MongoDB (pymongo)
- Apache Kafka (kafka-python)
- Postmark (postmarker biblioteka za slanje email-ova)
- Pytest
- GitHub Actions

---

## Baza podataka

Naziv baze:

```text
notification_db
```

Servis koristi MongoDB nerelacionu bazu podataka u skladu sa Database per Service paternom. Sav sadržaj obaveštenja se čuva u kolekciji `email_logs`.

---

## Struktura dokumenta (email_logs)

- notification_id
- order_id
- user_id
- user_email
- type (ticket, error, refund)
- email_body (struktura zavisi od tipa obaveštenja)
- status
- sent_at
- created_at

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

- GET /notifications

---

## Komunikacija sa drugim servisima

Notification Service komunicira sa Payment Service-om asinhrono, putem Apache Kafka platforme.

Kafka topici koje servis konzumira:

- `payment.completed` - šalje email sa detaljima kupljene ulaznice
- `payment.failed` - šalje email obaveštenje o neuspešnom plaćanju
- `payment.refunded` - šalje email obaveštenje o izvršenoj refundaciji

Nakon obrade, servis proizvodi poruku na `notification.sent` topic radi evidencije da je obaveštenje uspešno poslato.

---

## Bezbednost

Servis implementira:

- CORS konfiguraciju
- IDOR zaštitu - korisnik može pristupiti samo svojim obaveštenjima, osim ako ima administratorsku ulogu

Identitet korisnika se utvrđuje putem header-a koje prosleđuje API Gateway:

```text
X-User-Id: <id korisnika>
X-User-Role: <uloga korisnika>
```

---

## Testiranje

Testovi su implementirani korišćenjem Pytest biblioteke.

Pokretanje testova:

```bash
pytest
```

---

## Kontinuirana integracija

GitHub Actions se koristi za automatsko pokretanje testova prilikom svakog push-a i pull request-a na glavne grane.

---

### Monitoring

Servis izlaže `/metrics` endpoint koji koristi Prometheus za prikupljanje telemetrijskih podataka (broj HTTP zahteva, trajanje obrade, status kodovi) .
