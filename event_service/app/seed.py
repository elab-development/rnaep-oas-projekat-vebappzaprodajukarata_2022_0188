from datetime import datetime, timedelta

from app.database import Base, engine, SessionLocal
from app.models import Venue, Category, Event


def seed():
    Base.metadata.create_all(bind=engine)
    print("✓ Tabele kreirane")

    db = SessionLocal()
    try:
        # Lokacije
        venues_data = [
            ("Štark Arena", "Bulevar Arsenija Čarnojevića 58", "Beograd", 18000),
            ("Sava Centar", "Milentija Popovića 9", "Beograd", 3700),
            ("SPENS", "Sutjeska 2", "Novi Sad", 7000),
        ]
        venues = {}
        for name, address, city, capacity in venues_data:
            venue = db.query(Venue).filter(Venue.name == name).first()
            if not venue:
                venue = Venue(name=name, address=address, city=city, capacity=capacity)
                db.add(venue)
                db.commit()
                db.refresh(venue)
            venues[name] = venue
        print("✓ Lokacije kreirane")

        # Kategorije
        categories_data = [
            ("Koncert", "Muzički događaji i koncerti"),
            ("Sport", "Sportski događaji i utakmice"),
            ("Pozorište", "Pozorišne predstave"),
        ]
        categories = {}
        for name, description in categories_data:
            category = db.query(Category).filter(Category.name == name).first()
            if not category:
                category = Category(name=name, description=description)
                db.add(category)
                db.commit()
                db.refresh(category)
            categories[name] = category
        print("✓ Kategorije kreirane")

        # Dogadjaji
        events_data = [
            ("Metallica Concert", "Veliki koncert", "Štark Arena", "Koncert", 30),
            ("Partizan - Crvena Zvezda", "Večiti derbi", "Štark Arena", "Sport", 15),
            ("Hamlet", "Klasična pozorišna predstava", "Sava Centar", "Pozorište", 7),
        ]
        for title, description, venue_name, category_name, days_from_now in events_data:
            if not db.query(Event).filter(Event.title == title).first():
                start = datetime.utcnow() + timedelta(days=days_from_now)
                event = Event(
                    title=title,
                    description=description,
                    start_time=start,
                    end_time=start + timedelta(hours=3),
                    venue_id=venues[venue_name].id,
                    category_id=categories[category_name].id,
                    status="scheduled",
                )
                db.add(event)
                db.commit()
        print("✓ Dogadjaji kreirani")
    finally:
        db.close()


if __name__ == "__main__":
    seed()