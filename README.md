# RNAEP - Platforma za prodaju ulaznica

## Pregled

RNAEP je mikroservisna veb aplikacija za prodaju ulaznica za događaje (koncerti, sportski događaji, pozorišne predstave). Sistem je dizajniran prema principima mikroservisne arhitekture, sa nezavisnim servisima koji komuniciraju kako sinhrono (REST API preko API Gateway-a), tako i asinhrono (Apache Kafka).

---

## Arhitektura

Sistem se sastoji od sledećih mikroservisa:

- **User Service** - registracija, autentifikacija i upravljanje korisnicima i ulogama
- **Event Service** - upravljanje događajima, lokacijama (venues) i kategorijama
- **Ticket Service** - rezervacija sedišta, upravljanje kartama i narudžbinama
- **Payment Service** - obrada plaćanja, refundacija i transakcija
- **Notification Service** - slanje email obaveštenja korisnicima
- **API Gateway** - centralizovana ulazna tačka koja rutira zahteve, autentifikuje korisnike i prosleđuje ih odgovarajućim servisima
- **Frontend** - React/TypeScript korisnički interfejs

Svaki servis poseduje sopstvenu bazu podataka (Database per Service patern).

---

## Tehnologije

- **Backend**: Python 3.12/3.13, FastAPI, SQLAlchemy
- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **Baze podataka**: MySQL (User, Event, Ticket, Payment), MongoDB (Notification)
- **Asinhrona komunikacija**: Apache Kafka
- **Monitoring**: Prometheus, Grafana
- **Kontejnerizacija**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Email servis**: Postmark

---

## Komunikacija između servisa

### Sinhrona komunikacija

Front-end komunicira sa svim mikroservisima isključivo preko API Gateway-a, koji rutira zahteve, autentifikuje korisnike putem JWT tokena i prosleđuje identitet korisnika (X-User-Id, X-User-Role) dalje ka odgovarajućim servisima.

### Asinhrona komunikacija (Apache Kafka)

Payment Service, Ticket Service i Notification Service komuniciraju asinhrono putem Kafka topica:

- `payment.completed` - Payment Service emituje nakon uspešnog plaćanja; Ticket Service i Notification Service ga konzumiraju
- `payment.failed` - Payment Service emituje nakon neuspešnog plaćanja; Ticket Service i Notification Service ga konzumiraju
- `payment.refunded` - Payment Service emituje nakon uspešne refundacije; Notification Service ga konzumira
- `notification.sent` - Notification Service emituje nakon uspešno poslatog email obaveštenja

### Saga patern

Ticket Service implementira kompenzacione akcije u skladu sa Saga paternom. Nakon prijema `payment.completed` poruke, rezervacija se potvrđuje i karta se prodaje. Nakon prijema `payment.failed` poruke, rezervacija se otkazuje i sedište se automatski oslobađa za nove kupce.

Pored toga, Ticket Service poseduje pozadinski proces (background worker) koji periodično provera i automatski otkazuje rezervacije koje nisu plaćene u predviđenom vremenskom okviru od 10 minuta, oslobađajući sedišta za druge korisnike.

---

## Bezbednost

Sistem implementira sledeće bezbednosne mehanizme:

- **SQL Injection zaštita** - korišćenjem SQLAlchemy ORM-a, koji automatski generiše parametrizovane upite
- **IDOR zaštita** - svaki servis provera da korisnik može pristupiti samo sopstvenim resursima (plaćanja, rezervacije, obaveštenja), osim ako ima administratorsku ulogu
- **CORS** - svi servisi dozvoljavaju zahteve isključivo sa frontend domena
- **XSS zaštita** - tekstualni podaci koji se prosleđuju u email obaveštenja se enkodiraju (html.escape)
- **JWT autentifikacija** - User Service izdaje potpisane tokene; API Gateway dekoduje token i prosleđuje identitet korisnika ostalim servisima putem header-a
- **Heširanje lozinki** - korisničke lozinke se čuvaju u heširanom obliku

---

## Monitoring

Svi mikroservisi izlažu `/metrics` endpoint koji koristi Prometheus za prikupljanje telemetrijskih podataka (broj HTTP zahteva, trajanje obrade, status kodovi odgovora). Prikupljeni podaci se vizuelno prikazuju kroz Grafana dashboard.

---

## Pokretanje sistema

### Preduslovi

- Docker i Docker Compose
- Najmanje 15-20 GB slobodnog prostora na disku

### Pokretanje

Kreirati `.env` fajl u root direktorijumu sa Postmark kredencijalima:

```text
POSTMARK_API_KEY=<vas_postmark_api_kljuc>
POSTMARK_FROM_EMAIL=<vasa_verifikovana_email_adresa>
```

Pokrenuti kompletan sistem:

```bash
docker compose up --build
```

### Pristupne adrese

| Servis               | Adresa                |
| -------------------- | --------------------- |
| Frontend             | http://localhost:3000 |
| API Gateway          | http://localhost:8000 |
| User Service         | http://localhost:8005 |
| Event Service        | http://localhost:8003 |
| Ticket Service       | http://localhost:8004 |
| Payment Service      | http://localhost:8001 |
| Notification Service | http://localhost:8002 |
| Prometheus           | http://localhost:9090 |
| Grafana              | http://localhost:3001 |

### Popunjavanje početnih podataka (seed)

Nakon prvog pokretanja, potrebno je pokrenuti seed skripte za User, Event i Ticket servise:

```bash
docker compose exec user-service-py python -m app.seed
docker compose exec event-service python -m app.seed
docker compose exec ticket-service python -m app.seed
```

Payment Service automatski popunjava osnovne metode plaćanja prilikom pokretanja.

---

## Struktura repozitorijuma

```text
.
├── user-service-py/         # User Service
├── event_service/           # Event Service
├── ticket-service/          # Ticket Service
├── payment-service/         # Payment Service
├── notification-service/    # Notification Service
├── api-gateway/             # API Gateway
├── frontend/                 # React frontend
├── shared/                   # Zajednička logika (Prometheus metrike)
├── docker-compose.yml
└── prometheus.yml
```

---

## CI/CD

Svaki mikroservis poseduje sopstveni GitHub Actions workflow koji automatski pokreće testove prilikom svakog push-a i pull request-a na glavne grane. Nakon uspešnog merge-a na main granu, automatski se izgrađuje i objavljuje Docker image servisa.
