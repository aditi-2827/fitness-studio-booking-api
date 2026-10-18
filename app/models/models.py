"""ORM models for the fitness studio booking system."""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    """Timezone-aware UTC timestamp, used as a column default."""
    return datetime.now(timezone.utc)


class User(Base):
    """A registered user of the platform."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class FitnessClass(Base):
    """A fitness class offered by the studio."""

    __tablename__ = "fitness_classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Stored as naive IST (Asia/Kolkata). The API layer handles conversions.
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    instructor: Mapped[str] = mapped_column(String(100), nullable=False)
    available_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="fitness_class")


class Booking(Base):
    """A booking made by a user for a specific class."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("fitness_classes.id"), nullable=False, index=True
    )
    client_name: Mapped[str] = mapped_column(String(100), nullable=False)
    client_email: Mapped[str] = mapped_column(String(255), nullable=False)
    booked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="bookings")
    fitness_class: Mapped["FitnessClass"] = relationship(back_populates="bookings")

    # One user can book a given class only once
    __table_args__ = (
        UniqueConstraint("user_id", "class_id", name="uq_user_class"),
    )
