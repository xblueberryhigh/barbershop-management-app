from contextlib import asynccontextmanager

from fastapi import FastAPI
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


# Expand the booking model to include at least a barber/staff assignment.
# Start the frontend only after those API rules are stable.

