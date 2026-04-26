def test_get_customers_requires_authentication(client):
    response = client.get("/customers")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_customer_persists_trimmed_values(client, user_headers):
    response = client.post(
        "/customers",
        headers=user_headers,
        json={
            "first_name": "  Jane  ",
            "last_name": "  Doe ",
            "phone_number": " 1234567890 ",
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] > 0
    assert response_data["first_name"] == "Jane"
    assert response_data["last_name"] == "Doe"
    assert response_data["phone_number"] == "1234567890"


def test_get_customers_returns_created_customers(client, user_headers, customer_factory):
    first_customer = customer_factory(first_name="Jane", last_name="Doe")
    second_customer = customer_factory(first_name="John", last_name="Smith")

    response = client.get("/customers", headers=user_headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": first_customer.id,
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_number": first_customer.phone_number,
        },
        {
            "id": second_customer.id,
            "first_name": "John",
            "last_name": "Smith",
            "phone_number": second_customer.phone_number,
        },
    ]
