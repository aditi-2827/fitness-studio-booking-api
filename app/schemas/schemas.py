"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---------- User / Auth ----------

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Fitness Class ----------

class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    # Accepts ISO-8601 strings like "2025-06-15T10:00:00Z"
    dateTime: datetime
    instructor: str = Field(..., min_length=1, max_length=100)
    availableSlots: int = Field(..., ge=1, description="Must be at least 1")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Yoga Flow",
                "dateTime": "2025-06-15T10:00:00Z",
                "instructor": "John Doe",
                "availableSlots": 20,
            }
        }
    }


class ClassOut(BaseModel):
    id: int
    name: str
    # Stored as IST in the DB, serialized as UTC with a "Z" suffix
    dateTime: datetime
    instructor: str
    availableSlots: int

    model_config = {"from_attributes": True}


# ---------- Booking ----------

class BookingCreate(BaseModel):
    class_id: int
    client_name: str = Field(..., min_length=1, max_length=100)
    client_email: EmailStr

    model_config = {
        "json_schema_extra": {
            "example": {
                "class_id": 1,
                "client_name": "Alice",
                "client_email": "alice@example.com",
            }
        }
    }


class BookingOut(BaseModel):
    id: int
    class_id: int
    client_name: str
    client_email: str
    booked_at: datetime
    # Basic class info so the response is useful on its own
    class_name: str
    class_date_time: datetime
    instructor: str

    model_config = {"from_attributes": True}
