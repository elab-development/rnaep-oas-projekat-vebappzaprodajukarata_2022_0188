# Ticket Service

## Description

Ticket Service is a microservice developed using Python and FastAPI. Its purpose is to manage ticket reservations, seat availability and customer orders. The service prevents race conditions by using pessimistic locking and automatically releases unpaid reservations after 10 minutes.

## Technologies

* Python 3.12
* FastAPI
* SQLAlchemy
* MySQL
* Kafka
* Pytest

## Database Entities

### Seat

Represents a seat for an event.

Possible statuses:

* available
* reserved
* sold

### Ticket

Represents a ticket associated with a seat.

Possible statuses:

* available
* reserved
* sold

### Reservation

Represents a temporary ticket reservation.

Possible statuses:

* active
* confirmed
* expired
* cancelled

### Order

Represents an order created for a reservation.

Possible statuses:

* pending_payment
* paid
* cancelled

## Reservation Process

1. User selects a ticket.
2. Ticket Service checks seat availability.
3. Pessimistic locking prevents multiple users from reserving the same seat.
4. Reservation and Order objects are created.
5. Payment Service processes the payment.
6. Depending on the payment result, the reservation is confirmed or cancelled.

## Saga Pattern

Ticket Service uses the Saga pattern to maintain consistency between microservices.

### Successful Payment

Payment Service publishes the event:

`payment.completed`

Ticket Service:

* changes Reservation status to `confirmed`
* changes Order status to `paid`
* changes Ticket status to `sold`
* changes Seat status to `sold`

### Failed Payment

Payment Service publishes the event:

`payment.failed`

Ticket Service performs a compensation transaction:

* changes Reservation status to `cancelled`
* changes Order status to `cancelled`
* changes Ticket status to `available`
* changes Seat status to `available`

This approach guarantees data consistency without distributed transactions.

## Pessimistic Locking

Ticket Service uses SQLAlchemy's:

```python
.with_for_update()
```

to ensure that two users cannot reserve the same seat simultaneously.

## Reservation Expiration

Reservations are valid for 10 minutes.

A background worker periodically checks expired reservations and automatically:

* sets Reservation status to `expired`
* sets Order status to `cancelled`
* releases the ticket
* releases the seat

## Running the Service

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```
