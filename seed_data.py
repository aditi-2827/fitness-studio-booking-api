"""Seed the database with a sample user and a few fitness classes.

Run with:
    python seed_data.py
"""

from datetime import datetime, timedelta

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.models import FitnessClass, User
from app.utils.tz import now_ist_naive

SAMPLE_USER_EMAIL = "demo@fitnessstudio.com"
SAMPLE_USER_PASSWORD = "demo1234"

CLASSES = [
    ("Yoga Flow", 1, "John Doe", 20),
    ("Zumba Blast", 2, "Jane Smith", 25),
    ("HIIT Session", 3, "Ravi Kumar", 15),
    ("Pilates Core", 4, "Ananya Sharma", 12),
    ("Spin & Burn", 5, "Mike Chen", 18),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Demo user
        existing = db.query(User).filter(User.email == SAMPLE_USER_EMAIL).first()
        if not existing:
            user = User(
                name="Demo User",
                email=SAMPLE_USER_EMAIL,
                hashed_password=hash_password(SAMPLE_USER_PASSWORD),
            )
            db.add(user)
            db.commit()
            print(f"Created demo user: {SAMPLE_USER_EMAIL} / {SAMPLE_USER_PASSWORD}")
        else:
            print("Demo user already exists, skipping.")

        # Sample classes spread across upcoming days (times in IST)
        if db.query(FitnessClass).count() == 0:
            base = now_ist_naive()
            for i, (name, day_offset, instructor, slots) in enumerate(CLASSES):
                class_dt = base + timedelta(days=day_offset, hours=9 + i)
                fitness_class = FitnessClass(
                    name=name,
                    date_time=class_dt,
                    instructor=instructor,
                    available_slots=slots,
                )
                db.add(fitness_class)
            db.commit()
            print(f"Seeded {len(CLASSES)} sample classes.")
        else:
            print("Classes already exist, skipping.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
