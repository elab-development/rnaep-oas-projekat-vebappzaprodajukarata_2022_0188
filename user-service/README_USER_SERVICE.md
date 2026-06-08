# 🔐 User Microservice

Mikroservis odgovoran za **registraciju, autentifikaciju i upravljanje korisnicima** u aplikaciji za prodaju karata.

## 📋 Što Ovaj Servis Radi?

User Microservice omogućava:
- ✅ Registracija novih korisnika
- ✅ Login i autentifikacija (sa Sanctum tokenom)
- ✅ Upravljanje profilima korisnika
- ✅ Dodeljivanje uloga (admin, user, guest)
- ✅ Pretraga korisnika (samo admin)
- ✅ Brisanje korisnika (samo admin)
- ✅ Dobijanje statistike (samo admin)

---

## 🚀 Brzi Start

### Preduslov
- Docker i Docker Compose instaliran
- PHP 8.2+ (ako radiš bez Docker-a)
- MySQL 8.0 (ako radiš bez Docker-a)

### 1. Kloniranje Repozitorijuma

```bash
git clone https://github.com/your-org/ticket-app.git
cd ticket-app/user-service
```

### 2. Pokrećanje sa Docker-om (PREPORUKA)

```bash
# Kreiraj .env fajl iz šablona
cp .env.example .env

# Pokreni sve servise
docker-compose up -d

# Primeni migracije i seed
docker-compose exec user-service php artisan migrate:fresh --seed

# Proveri status
docker-compose ps
```

**Servis je dostupan na:** http://localhost:8001

**PhpMyAdmin je dostupan na:** http://localhost:8081

### 3. Pokrećanje bez Docker-a (Lokalno)

```bash
# Instalacija zavisnosti
composer install

# Kreiraj .env fajl
cp .env.example .env

# Generiši app key
php artisan key:generate

# Kreiraj bazu podataka
# (ručno preko MySQL klijenta ili Artisan komande)

# Primeni migracije
php artisan migrate:fresh --seed

# Pokreni development server
php artisan serve

# Server sluša na http://localhost:8000
```

---

## 📡 API Endpoints

### 🔓 Javni Endpoints (bez tokena)

#### 1. Registracija
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "Aleksandra Vrzić",
  "email": "aleksandra@example.com",
  "password": "SecurePassword123!",
  "password_confirmation": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "message": "Korisnik uspešno registrovan",
  "data": {
    "id": 1,
    "name": "Aleksandra Vrzić",
    "email": "aleksandra@example.com",
    "roles": ["user"],
    "created_at": "2024-04-15T10:30:00Z",
    "updated_at": "2024-04-15T10:30:00Z"
  }
}
```

---

#### 2. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "aleksandra@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Uspešna prijava",
  "data": {
    "user": {
      "id": 1,
      "name": "Aleksandra Vrzić",
      "email": "aleksandra@example.com",
      "roles": ["user"]
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 28800
  }
}
```

---

### 🔒 Zaštićeni Endpoints (sa tokenom)

#### 3. Moj Profil
```http
GET /api/auth/me
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Profil prijavljivog korisnika",
  "data": {
    "id": 1,
    "name": "Aleksandra Vrzić",
    "email": "aleksandra@example.com",
    "roles": ["user"],
    "created_at": "2024-04-15T10:30:00Z",
    "updated_at": "2024-04-15T10:30:00Z"
  }
}
```

---

#### 4. Ažuriranje Profila
```http
PUT /api/auth/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Novo Ime",
  "email": "nevemail@example.com"
}
```

---

#### 5. Logout
```http
POST /api/auth/logout
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Uspešna odjava"
}
```

---

#### 6. Osvežavanje Tokena
```http
POST /api/auth/refresh
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Token uspešno osvežen",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 28800
  }
}
```

---

### 👨‍💼 Admin Endpoints

> ⚠️ Zahtevaju `admin` rolu!

#### 7. Lista Svih Korisnika
```http
GET /api/users?page=1&per_page=15
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "message": "Lista korisnika",
  "data": [
    {
      "id": 1,
      "name": "Aleksandra",
      "email": "aleksandra@example.com",
      "roles": ["user"]
    }
  ],
  "pagination": {
    "total": 50,
    "per_page": 15,
    "current_page": 1,
    "total_pages": 4
  }
}
```

---

#### 8. Pretraga Korisnika
```http
GET /api/users/search?q=aleksandra&per_page=15
Authorization: Bearer {admin_token}
```

---

#### 9. Pregled Korisnika po ID-u
```http
GET /api/users/{id}
Authorization: Bearer {token}
```

---

#### 10. Ažuriranje Korisnika (Admin)
```http
PUT /api/users/{id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Novo Ime",
  "email": "nevemail@example.com"
}
```

---

#### 11. Brisanje Korisnika (Admin)
```http
DELETE /api/users/{id}
Authorization: Bearer {admin_token}
```

---

#### 12. Dodeljivanje Uloge
```http
POST /api/users/{id}/assign-role
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "role": "admin"
}
```

**Moguće uloge:** `guest`, `user`, `admin`

---

#### 13. Uklanjanje Uloge
```http
DELETE /api/users/{id}/remove-role
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "role": "admin"
}
```

---

#### 14. Statistika Korisnika
```http
GET /api/users/statistics/count
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "message": "Statistika korisnika",
  "data": {
    "total_users": 50,
    "admins": 2,
    "regular_users": 48,
    "recent_users": [...]
  }
}
```

---

## 🧪 Testiranje

### Pokretanje Testova
```bash
# Svi testovi
php artisan test

# Samo testovi za autentifikaciju
php artisan test --filter=AuthenticationTest

# Sa verbose outputom
php artisan test --verbose
```

### Testiranje sa Postman-om
1. Preuzmi Postman
2. Kreiraj novu kolekciju
3. Dodaj zahteve iz sekcije "API Endpoints" iznad
4. Testiraj!

---

## 🏗️ Struktura Direktorijuma

```
user-service/
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── AuthController.php          # Login, registracija, profil
│   │   │   └── UserController.php          # CRUD, admin funkcije
│   │   ├── Middleware/
│   │   │   └── AdminMiddleware.php         # Provera admin role
│   │   └── Requests/                       # Form validacijske klase
│   ├── Models/
│   │   ├── User.php                        # Korisničkog modela
│   │   └── Role.php                        # Uloga model
│   ├── Services/
│   │   └── AuthenticationService.php       # Poslovnog logika autentifikacije
│   └── Repositories/
│       └── UserRepository.php              # Pristup bazi podataka
├── database/
│   ├── migrations/
│   │   └── *_create_users_table.php        # Migracije baze
│   └── seeders/
│       └── DatabaseSeeder.php              # Test podaci
├── routes/
│   └── api.php                             # API rute
├── tests/
│   └── Feature/
│       └── AuthenticationTest.php          # Testovi
├── .env.example                            # Šablon za .env
├── Dockerfile                              # Docker konfiguracija
├── docker-compose.yml                      # Docker Compose
├── composer.json                           # PHP zavisnosti
└── README.md                               # Ova datoteka
```

---

## 🔧 Konfiguracija

### Važne Promenljive .env

```env
# Baza podataka
DB_HOST=user-db              # Ime kontejnera u Docker-u
DB_DATABASE=users_db
DB_USERNAME=root
DB_PASSWORD=root_password

# Sanctum Token
SANCTUM_STATEFUL_DOMAINS=localhost,localhost:3000

# Logging
LOG_LEVEL=debug              # local, debug, info, notice, warning, error, critical, alert, emergency
```

---

## 📦 Zavisnosti

### Backend
- **Laravel 11** - PHP framework
- **Laravel Sanctum** - API autentifikacija i tokeni
- **Composer** - PHP package manager

### Baza Podataka
- **MySQL 8.0** - Relaciona baza podataka

### DevOps
- **Docker** - Kontejnerizacija
- **Docker Compose** - Orkestacija servisa

---

## 🐛 Uobičajeni Problemi

### Problem: "SQLSTATE[HY000]: General error: 1030 Got error"

**Rešenje:**
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec user-service php artisan migrate:fresh --seed
```

---

### Problem: "Port 3306 već zauzet"

**Rešenje:**
```bash
# Promeni port u docker-compose.yml
# Zameni: "3306:3306"
# Sa: "3307:3306"

# Ili zaustavi druge MySQL servise
sudo service mysql stop
```

---

### Problem: "Permission denied" greške

**Rešenje:**
```bash
docker-compose exec user-service chmod -R 775 storage bootstrap/cache
```

---

## 📚 Dodatni Resursi

- [Laravel Dokumentacija](https://laravel.com/docs)
- [Laravel Sanctum](https://laravel.com/docs/sanctum)
- [Docker Dokumentacija](https://docs.docker.com)

---

## 👥 Tim

Razvijeno od strane:
- Aleksandra Vrzić (2022/0188)
- Janja Vukelić (2022/0159)
- Milica Drljača (2022/0234)

**Mentor:** Miloš Jolović

---

## 📝 Verzija

**v1.0.0** - Osnovna autentifikacija i upravljanje korisnicima

---

## 📄 Licenca

MIT License

---

## 🤝 Doprinos

1. Kreiraj feature granu: `git checkout -b feature/nova-funkcionalnost`
2. Commituj promene: `git commit -m "feat: opis"`
3. Push na GitHub: `git push origin feature/nova-funkcionalnost`
4. Otvori Pull Request

---

**Zadnje ažuriranje:** 15. april 2024
