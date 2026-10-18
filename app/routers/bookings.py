"""Booking endpoints: book a class and view own bookings."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Booking, FitnessClass, User
from app.schemas.schemas import BookingCreate, BookingOut
from app.utils.tz import ist_naive_to_utc_iso

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Bookings"])


def _booking_to_dict(booking: Booking) -> dict:
    """Flatten a Booking ORM object into the response shape, including class details
    (class time converted back to UTC "Z" format)."""
    return {
        "id": booking.id,
        "class_id": booking.class_id,
        "client_name": booking.client_name,
        "client_email": booking.client_email,
        "booked_at": booking.booked_at,
        "class_name": booking.fitness_class.name,
        "class_date_time": ist_naive_to_utc_iso(booking.fitness_class.date_time),
        "instructor": booking.fitness_class.instructor,
    }


@router.post("/book", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def book_class(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Book a slot in a fitness class. Requires authentication.

    Prevents overbooking by only decrementing slots when at least one
    is still available, inside a transaction.
    """
    fitness_class = (
        db.query(FitnessClass)
        .filter(FitnessClass.id == payload.class_id)
        .with_for_update()  # row-level lock to avoid race conditions
        .first()
    )
    if fitness_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )

    if fitness_class.available_slots <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Class is fully booked",
        )

    booking = Booking(
        user_id=current_user.id,
        class_id=payload.class_id,
        client_name=payload.client_name,
        client_email=payload.client_email,
    )
    fitness_class.available_slots -= 1

    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        # Unique constraint (user_id, class_id) fired — user already booked this class
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already booked this class",
        )

    db.refresh(booking)
    logger.info(
        "Booking created: user=%s class=%s",
        current_user.email,
        payload.class_id,
    )
    return _booking_to_dict(booking)


@router.get("/bookings", response_model=list[BookingOut])
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """View all bookings made by the authenticated user. Requires authentication."""
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.booked_at.desc())
        .all()
    )
    return [_booking_to_dict(b) for b in bookings]
