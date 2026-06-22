from app.db.database import SessionLocal, engine
from app.db.models import Base, Clinic


def seed_data():
    """Seed the database with sample clinic data for Tamil Nadu."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Clinic).count() > 0:
            print("Database already seeded with clinics.")
            return

        clinics = [
            Clinic(
                name="Erode Primary Health Centre",
                address="12 Main Road, Erode",
                city="Erode",
                lat=11.3410,
                lng=77.7172,
                phone="+919876543210",
                available=True,
            ),
            Clinic(
                name="Bhavani Govt Hospital",
                address="Govt Hosp Road, Bhavani",
                city="Bhavani",
                lat=11.4449,
                lng=77.6972,
                phone="+919876543211",
                available=True,
            ),
            Clinic(
                name="Salem City Health Clinic",
                address="5 Junction Road, Salem",
                city="Salem",
                lat=11.6643,
                lng=78.1460,
                phone="+919876543212",
                available=True,
            ),
            Clinic(
                name="Coimbatore Community PHC",
                address="104 Trichy Road, Coimbatore",
                city="Coimbatore",
                lat=11.0168,
                lng=76.9558,
                phone="+919876543213",
                available=True,
            ),
            Clinic(
                name="Chennai Triage Clinic",
                address="22 Anna Salai, Chennai",
                city="Chennai",
                lat=13.0827,
                lng=80.2707,
                phone="+919876543214",
                available=True,
            ),
        ]
        db.add_all(clinics)
        db.commit()
        print("Clinics seeded successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
