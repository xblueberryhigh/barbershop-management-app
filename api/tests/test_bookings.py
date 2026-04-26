from datetime import datetime, timedelta

from app.enums import BookingStatus


def next_business_day_at(hour: int, minute: int = 0) -> datetime:
    candidate = datetime.now() + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate.replace(hour=hour, minute=minute, second=0, microsecond=0)


def next_weekday(target_weekday: int, hour: int, minute: int = 0) -> datetime:
    now = datetime.now()
    days_ahead = (target_weekday - now.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    candidate = now + timedelta(days=days_ahead)
    return candidate.replace(hour=hour, minute=minute, second=0, microsecond=0)


def previous_business_day_at(hour: int, minute: int = 0) -> datetime:
    candidate = datetime.now() - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate.replace(hour=hour, minute=minute, second=0, microsecond=0)


def booking_payload(customer_id: int, start_time: datetime, end_time: datetime) -> dict:
    return {
        "customer_id": customer_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": BookingStatus.CONFIRMED.value,
    }


def test_get_bookings_requires_authentication(client):
    response = client.get("/bookings")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_booking_returns_booking_with_customer(client, user_headers, customer_factory):
    customer = customer_factory(first_name="Jane", last_name="Doe")
    start_time = next_business_day_at(10, 0)
    end_time = next_business_day_at(11, 0)

    response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time, end_time),
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["id"] > 0
    assert response_data["customer"] == {
        "id": customer.id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone_number": customer.phone_number,
    }
    assert response_data["status"] == BookingStatus.CONFIRMED.value
    assert response_data["start_time"] == start_time.isoformat()
    assert response_data["end_time"] == end_time.isoformat()


def test_create_booking_rejects_unknown_customer(client, user_headers):
    start_time = next_business_day_at(10, 0)
    end_time = next_business_day_at(11, 0)

    response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(999, start_time, end_time),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}


def test_create_booking_rejects_overlapping_booking(client, user_headers, customer_factory):
    customer = customer_factory()
    start_time = next_business_day_at(10, 0)
    end_time = next_business_day_at(11, 0)

    first_response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time, end_time),
    )
    second_response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time + timedelta(minutes=30), end_time + timedelta(minutes=30)),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json() == {"detail": "Booking conflicts with an existing booking"}


def test_create_booking_rejects_past_time(client, user_headers, customer_factory):
    customer = customer_factory()
    start_time = previous_business_day_at(10, 0)
    end_time = start_time + timedelta(hours=1)

    response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time, end_time),
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Bookings cannot be created in the past"}


def test_create_booking_rejects_weekend(client, user_headers, customer_factory):
    customer = customer_factory()
    start_time = next_weekday(5, 10, 0)
    end_time = next_weekday(5, 11, 0)

    response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time, end_time),
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Bookings are only allowed on working days"}


def test_create_booking_rejects_lunch_break_overlap(client, user_headers, customer_factory):
    customer = customer_factory()
    start_time = next_business_day_at(11, 30)
    end_time = next_business_day_at(12, 30)

    response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time, end_time),
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Booking cannot end during the lunch break"}


def test_create_booking_rejects_cross_day_booking(client, user_headers, customer_factory):
    customer = customer_factory()
    start_time = next_business_day_at(22, 30)
    end_time = start_time + timedelta(hours=2)

    response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time, end_time),
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Booking must start and end on the same day"}


def test_get_bookings_returns_nested_customer_data(client, user_headers, customer_factory):
    customer = customer_factory(first_name="Ada", last_name="Lovelace")
    start_time = next_business_day_at(9, 0)
    end_time = next_business_day_at(10, 0)

    create_response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_payload(customer.id, start_time, end_time),
    )
    list_response = client.get("/bookings", headers=user_headers)

    assert create_response.status_code == 200
    assert list_response.status_code == 200
    created_booking = create_response.json()
    assert list_response.json() == [
        {
            "id": created_booking["id"],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": BookingStatus.CONFIRMED.value,
            "customer": {
                "id": customer.id,
                "first_name": "Ada",
                "last_name": "Lovelace",
                "phone_number": customer.phone_number,
            },
        }
    ]
