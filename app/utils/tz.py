"""Timezone helpers.

The studio operates out of India, so every class time is normalised to
IST (Asia/Kolkata, UTC+05:30) before it hits the database. Incoming
times that carry a UTC offset are converted; naive times are assumed
to already be in IST. The stored value is a naive IST datetime, and
responses format it back as UTC with a "Z" suffix.
"""

from datetime import datetime

from pytz import timezone

IST = timezone("Asia/Kolkata")


def now_ist_naive() -> datetime:
    """Current time as a naive IST datetime (for comparing against stored times)."""
    return datetime.now(IST).replace(tzinfo=None)


def to_ist_naive(dt: datetime) -> datetime:
    """Normalise any datetime to a naive IST datetime for storage.

    - aware datetimes (e.g. with a "Z" suffix) are converted to IST
    - naive datetimes are assumed to already be in IST and left as-is
    """
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(IST).replace(tzinfo=None)


def ist_naive_to_utc_iso(dt: datetime) -> str:
    """Convert a stored naive-IST datetime to a UTC ISO string ending in "Z".

    API responses use this format (e.g. "2025-06-18T08:00:00Z") while
    the database keeps everything in IST.
    """
    utc_dt = IST.localize(dt).astimezone(timezone("UTC"))
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
