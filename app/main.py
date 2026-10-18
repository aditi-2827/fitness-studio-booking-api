"""FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import auth, bookings, classes

# Basic logging config so we can see what's happening when the app runs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (fine for SQLite dev; use Alembic in production)
    Base.metadata.create_all(bind=engine)
    logging.getLogger(__name__).info("Database tables ready")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Simple booking API for a fictional fitness studio. "
        "Sign up, log in, then create/browse classes and book slots."
    ),
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(bookings.router)


@app.get("/", tags=["Health"])
def health_check():
    """Basic health check so you know the API is up."""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
