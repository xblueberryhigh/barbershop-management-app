import os
from itertools import count

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"

from app.database import Base, get_db
from app.enums import BookingStatus, UserRole
from app.main import app
from app.models import Customer, User
from app.security import hash_password


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@event.listens_for(test_engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    del connection_record
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def reset_database():
    with test_engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user_factory(db_session):
    sequence = count(1)

    def create_user(
        *,
        role: UserRole = UserRole.USER,
        password: str = "Password123",
        first_name: str = "Test",
        last_name: str = "User",
        email: str | None = None,
    ) -> User:
        user_number = next(sequence)
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email or f"user{user_number}@example.com",
            hashed_password=hash_password(password),
            role=role,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create_user


@pytest.fixture
def customer_factory(db_session):
    sequence = count(1)

    def create_customer(
        *,
        first_name: str = "Test",
        last_name: str = "Customer",
        phone_number: str | None = None,
    ) -> Customer:
        customer_number = next(sequence)
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number or f"555000{customer_number:04d}",
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    return create_customer


@pytest.fixture
def login_headers(client):
    def get_headers(email: str, password: str) -> dict[str, str]:
        response = client.post(
            "/auth/login-user",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return get_headers


@pytest.fixture
def admin_user(user_factory):
    return user_factory(role=UserRole.ADMIN, password="AdminPass123", email="admin@example.com")


@pytest.fixture
def regular_user(user_factory):
    return user_factory(password="UserPass123", email="user@example.com")


@pytest.fixture
def admin_headers(admin_user, login_headers):
    return login_headers(admin_user.email, "AdminPass123")


@pytest.fixture
def user_headers(regular_user, login_headers):
    return login_headers(regular_user.email, "UserPass123")
