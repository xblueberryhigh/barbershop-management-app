from contextlib import asynccontextmanager

from fastapi import FastAPI
from app import models
from app.database import Base, engine
from app.routes.customers import router as customers_router
from app.routes.bookings import router as bookings_router
from app.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Importing models above registers all tables on Base.metadata.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(customers_router)
app.include_router(bookings_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Barbershop management api running"}


# Alembic
# register/login/me
# role-based protection
# booking rules

