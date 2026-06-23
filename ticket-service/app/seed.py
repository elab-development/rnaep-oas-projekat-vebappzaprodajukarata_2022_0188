from app.database import Base, engine, SessionLocal
from app.models import Seat, Ticket


def seed():
    Base.metadata.create_all(bind=engine)
    print("✓ Tabele kreirane")

    db = SessionLocal()
    try:
        # event_id 1, 2, 3 odgovaraju događajima kreiranim u Event Service seed-u
        seats_and_tickets = [
            # (event_id, row_label, seat_number, price)
            (1, "A", 1, 5000.0),
            (1, "A", 2, 5000.0),
            (1, "A", 3, 5000.0),
            (1, "B", 1, 3500.0),
            (1, "B", 2, 3500.0),
            (2, "A", 1, 2000.0),
            (2, "A", 2, 2000.0),
            (2, "B", 1, 1500.0),
            (3, "A", 1, 1200.0),
            (3, "A", 2, 1200.0),
        ]

        for event_id, row_label, seat_number, price in seats_and_tickets:
            existing_seat = (
                db.query(Seat)
                .filter(
                    Seat.event_id == event_id,
                    Seat.row_label == row_label,
                    Seat.seat_number == seat_number,
                )
                .first()
            )
            if not existing_seat:
                seat = Seat(
                    event_id=event_id,
                    row_label=row_label,
                    seat_number=seat_number,
                    status="available",
                )
                db.add(seat)
                db.commit()
                db.refresh(seat)

                ticket = Ticket(
                    event_id=event_id,
                    seat_id=seat.id,
                    price=price,
                    status="available",
                )
                db.add(ticket)
                db.commit()

        print("✓ Sedista i karte kreirane")
    finally:
        db.close()


if __name__ == "__main__":
    seed()