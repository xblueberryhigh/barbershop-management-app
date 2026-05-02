from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routes.customers import router as customers_router
from app.routes.bookings import router as bookings_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router

app = FastAPI()

app.include_router(customers_router)
app.include_router(bookings_router)
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "Barbershop management api running"}

# Start the frontend only after those API rules are stable.
# Medium: auth token decoding uses a bare except: in security.py. It won’t break the MVP immediately, but it hides real bugs and makes auth failures harder to debug.
# Medium: there is still no cancel/update booking flow, only create/list. If your MVP includes real appointment management, that’s a backend gap, not just a frontend task.

