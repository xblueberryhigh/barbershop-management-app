from contextlib import asynccontextmanager

from fastapi import FastAPI
from app import models
from app.database import Base, engine
from app.routes.customers import router as customers_router
from app.routes.bookings import router as bookings_router
from app.routes.auth import router as auth_router

app = FastAPI()

app.include_router(customers_router)
app.include_router(bookings_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Barbershop management api running"}


# Add booking conflict rules in booking_service.py.
# Expand the booking model to include at least a barber/staff assignment.
# Add tests for login, protected routes, and booking conflicts.
# Start the frontend only after those API rules are stable.

