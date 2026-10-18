"""Fitness class endpoints: create and list upcoming classes."""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import FitnessClass, User
from app.schemas.schemas import ClassCreate, ClassOut
from app.utils.tz import ist_naive_to_utc_iso, now_ist_naive, to_ist_naive

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.post("", response_model=ClassOut, status_code=status.HTTP_201_CREATED)
def create_class(
    payload: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new fitness class. Requires authentication."""
    # Normalise incoming time (may be UTC "Z" or offset-aware) to IST for storage
    ist_time = to_ist_naive(payload.dateTime)

    new_class = FitnessClass(
        name=payload.name,
        date_time=ist_time,
        instructor=payload.instructor,
        available_slots=payload.availableSlots,
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    logger.info(
        "Class created by %s: %s at %s",
        current_user.email,
        new_class.name,
        new_class.date_time,
    )

    # Stored in IST, returned as UTC "Z" per the assignment example
    return {
        "id": new_class.id,
        "name": new_class.name,
        "dateTime": ist_naive_to_utc_iso(new_class.date_time),
        "instructor": new_class.instructor,
        "availableSlots": new_class.available_slots,
    }


@router.get("", response_model=list[ClassOut])
def list_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch all upcoming fitness classes (start time in the future). Requires authentication."""
    # date_time is stored as naive IST, so compare against the current time in IST
    now_ist = now_ist_naive()

    classes = (
        db.query(FitnessClass)
        .filter(FitnessClass.date_time >= now_ist)
        .order_by(FitnessClass.date_time.asc())
        .all()
    )

    return [
        {
            "id": c.id,
            "name": c.name,
            "dateTime": ist_naive_to_utc_iso(c.date_time),
            "instructor": c.instructor,
            "availableSlots": c.available_slots,
        }
        for c in classes
    ]
