from app.enums import UserRole


def test_login_returns_access_token_for_valid_credentials(client, regular_user):
    response = client.post(
        "/auth/login-user",
        json={"email": regular_user.email, "password": "UserPass123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_invalid_password(client, regular_user):
    response = client.post(
        "/auth/login-user",
        json={"email": regular_user.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_me_requires_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_me_returns_authenticated_user(client, regular_user, user_headers):
    response = client.get("/auth/me", headers=user_headers)

    assert response.status_code == 200
    assert response.json() == {
        "id": regular_user.id,
        "first_name": regular_user.first_name,
        "last_name": regular_user.last_name,
        "email": regular_user.email,
        "role": UserRole.USER.value,
    }


def test_admin_can_create_user(client, admin_headers):
    response = client.post(
        "/auth/create-user",
        headers=admin_headers,
        json={
            "first_name": "New",
            "last_name": "Staff",
            "email": "new.staff@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] > 0
    assert response_data["first_name"] == "New"
    assert response_data["last_name"] == "Staff"
    assert response_data["email"] == "new.staff@example.com"
    assert response_data["role"] == UserRole.USER.value


def test_non_admin_cannot_create_user(client, user_headers):
    response = client.post(
        "/auth/create-user",
        headers=user_headers,
        json={
            "first_name": "New",
            "last_name": "Staff",
            "email": "new.staff@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Only admins can create users"}


def test_create_user_rejects_duplicate_email(client, admin_headers, regular_user):
    response = client.post(
        "/auth/create-user",
        headers=admin_headers,
        json={
            "first_name": "Copy",
            "last_name": "User",
            "email": regular_user.email,
            "password": "Password123",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}
