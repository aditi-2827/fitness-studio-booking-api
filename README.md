# Fitness Studio Booking API

A simple REST API for a fictional fitness studio, built with **Python** and **FastAPI**.

Users can sign up, log in, browse upcoming classes, book a slot, and view their own bookings.
Class times are stored in **IST** (Asia/Kolkata) as required.

---

## Features

- JWT-based authentication (signup + login)
- Create and list upcoming fitness classes (auth required)
- Book a slot in a class with overbooking protection (auth required)
- View your own bookings (auth required)
- Class times stored in IST, returned as UTC (`Z`)
- Automatic interactive API docs (Swagger UI / ReDoc)

---

## Tech Stack

| Layer     | Choice                                      |
|-----------|---------------------------------------------|
| Framework | FastAPI                                     |
| Language  | Python 3.10+                                |
| Database  | SQLite (dev) — swap `DATABASE_URL` for Postgres/MySQL |
| ORM       | SQLAlchemy 2.0                              |
| Auth      | JWT (python-jose) + bcrypt password hashing |
| Tests     | pytest + FastAPI TestClient                 |

---

## Project Structure

```
fitness_booking_api/
├── app/
│   ├── main.py               # FastAPI app + router registration
│   ├── core/
│   │   ├── config.py         # Settings from env vars
│   │   ├── database.py       # Engine, session, Base
│   │   ├── security.py       # Password hashing + JWT helpers
│   │   └── deps.py           # Auth dependency (get_current_user)
│   ├── models/
│   │   └── models.py         # SQLAlchemy models (User, FitnessClass, Booking)
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response schemas
│   ├── routers/
│   │   ├── auth.py           # /signup, /login
│   │   ├── classes.py        # POST /classes, GET /classes
│   │   └── bookings.py       # POST /book, GET /bookings
│   └── utils/
│       └── tz.py             # IST timezone helpers
├── tests/                    # Unit tests
├── seed_data.py              # Sample user + classes
├── requirements.txt
└── README.md
```

---

## Setup & Run Locally

### 1. Clone and enter the directory

```bash
git clone <your-repo-url>
cd fitness_booking_api
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure environment

```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

Edit `.env` and set a strong `SECRET_KEY` for production.

### 5. Seed sample data (optional)

```bash
python seed_data.py
```

This creates a demo user (`demo@fitnessstudio.com` / `demo1234`) and 5 sample classes.

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

The API is now running at **http://127.0.0.1:8000**

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Tables are auto-created on startup (fine for SQLite dev). For production, use Alembic migrations.

---

## API Endpoints

| Method | Endpoint    | Auth | Description                        |
|--------|-------------|------|------------------------------------|
| POST   | /signup     | No   | Register a new user                |
| POST   | /login      | No   | Log in, returns JWT                |
| POST   | /classes    | Yes  | Create a fitness class             |
| GET    | /classes    | Yes  | List all upcoming classes          |
| POST   | /book       | Yes  | Book a slot in a class             |
| GET    | /bookings   | Yes  | View your own bookings             |
| GET    | /           | No   | Health check                       |

---

## API Usage (cURL)

### Sign up

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}'
```

### Log in

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the token for the next calls:

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Create a class (auth required)

```bash
curl -X POST http://127.0.0.1:8000/classes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Yoga Flow",
    "dateTime": "2025-06-15T10:00:00Z",
    "instructor": "John Doe",
    "availableSlots": 20
  }'
```

The `dateTime` above is stored internally in **IST**, but returned in UTC (`Z`) format:

```json
{
  "id": 1,
  "name": "Yoga Flow",
  "dateTime": "2025-06-15T10:00:00Z",
  "instructor": "John Doe",
  "availableSlots": 20
}
```

### List upcoming classes (auth required)

```bash
curl -X GET http://127.0.0.1:8000/classes \
  -H "Authorization: Bearer $TOKEN"
```

### Book a class (auth required)

```bash
curl -X POST http://127.0.0.1:8000/book \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "Alice",
    "client_email": "alice@example.com"
  }'
```

### View your bookings (auth required)

```bash
curl -X GET http://127.0.0.1:8000/bookings \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Handling

| Status | Meaning                                           |
|--------|---------------------------------------------------|
| 201    | Created (signup, create class, booking)           |
| 200    | OK (login, list endpoints)                        |
| 401    | Missing / invalid / expired token, or bad login   |
| 404    | Class not found                                   |
| 409    | Duplicate email, duplicate booking, or class full |
| 422    | Validation error (missing/invalid fields)         |

Example error response:

```json
{ "detail": "Class is fully booked" }
```

---

## Timezone Handling

- The studio operates in **IST (Asia/Kolkata, UTC+05:30)**.
- On input, any timezone-aware `dateTime` (e.g. `...Z` for UTC) is converted to IST before storage.
- Naive times (no offset) are assumed to already be in IST.
- On output, `dateTime` is converted back to UTC and returned with a `Z` suffix (e.g. `2025-06-15T10:00:00Z`).

---

## Running Tests

```bash
pytest -v
```

Tests use an in-memory SQLite database and cover auth, class CRUD, booking, overbooking, and duplicate-booking cases.

---

## Notes / Assumptions

- A user can book a given class **only once** (enforced with a DB unique constraint).
- Booking decrements `availableSlots` atomically inside a transaction with a row-level lock (`with_for_update`) to prevent overbooking under concurrency.
- `GET /classes` only returns classes with a start time in the future.
- JWT expires after 30 minutes by default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## Future Improvements

- Alembic migrations instead of auto `create_all`
- Token refresh endpoint
- Admin role for class management
- Pagination on list endpoints
- Cancel booking endpoint
