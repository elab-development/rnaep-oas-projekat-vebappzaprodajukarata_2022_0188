# Event Service

## Overview

Event Service is responsible for managing events, venues, and categories in the ticketing platform. It provides CRUD operations for creating, updating, retrieving, and deleting events and related entities.

The service is implemented using FastAPI and follows the database-per-service microservice architecture pattern.

---

## Technologies

- Python 3.12
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Pytest
- GitHub Actions
- SQLite (used for testing)

---

## Database

Database :

```text
event_db
```

The service uses its own database in accordance with the Database per Service pattern.

---

## Entities

### Event

- id
- title
- description
- start_time
- end_time
- status
- venue_id
- category_id
- created_at
- updated_at

### Venue

- id
- name
- address
- city
- capacity
- latitude
- longitude

### Category

- id
- name
- description

---

## Relationships

```text
Venue 1 ---- N Event
Category 1 ---- N Event
```

---

## Running the service

Activate virtual environment:

```bash
.\venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the service:

```bash
uvicorn app.main:app --reload
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Events

- POST /events/
- GET /events/
- GET /events/{event_id}
- PUT /events/{event_id}
- DELETE /events/{event_id}
- PATCH /events/{event_id}/cancel

### Venues

- POST /venues/
- GET /venues/
- GET /venues/{venue_id}
- PUT /venues/{venue_id}
- DELETE /venues/{venue_id}

### Categories

- POST /categories/
- GET /categories/
- GET /categories/{category_id}
- PUT /categories/{category_id}
- DELETE /categories/{category_id}

---

## Security

The service implements:

- CORS configuration
- SQL Injection protection through SQLAlchemy ORM
- IDOR protection through role-based authorization
- Custom exception handlers
- Validation using Pydantic schemas

Administrative operations require:

```text
X-User-Role: admin
```

---

## Testing

Tests are implemented using Pytest.

Testing uses SQLite database:

```text
test_event_service.db
```

Run tests:

```bash
pytest
```

---

### Continuous Integration

GitHub Actions are used to automatically execute tests on every push and pull request.

---

## Health Check

```text
GET /health
```

Response:

```json
{
  "status": "UP",
  "service": "event-service"
}
```
