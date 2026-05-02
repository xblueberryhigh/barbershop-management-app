from app.enums import UserRole


def test_get_users_requires_authentication(client):
    response = client.get("/users")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_non_admin_cannot_get_full_users(client, user_headers):
    response = client.get("/users", headers=user_headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "Only admins can get users"}


def test_admin_can_get_full_users(client, admin_headers, user_factory):
    staff_user = user_factory(
        first_name="Sam",
        last_name="Scissor",
        email="sam.scissor@example.com",
    )

    response = client.get("/users", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "first_name": "Test",
            "last_name": "User",
            "email": "admin@example.com",
            "role": UserRole.ADMIN.value,
        },
        {
            "id": staff_user.id,
            "first_name": "Sam",
            "last_name": "Scissor",
            "email": "sam.scissor@example.com",
            "role": UserRole.BARBER.value,
        },
    ]


def test_get_assignable_users_requires_authentication(client):
    response = client.get("/users/assignable-users")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_authenticated_user_can_get_assignable_users(client, user_headers):
    response = client.get("/users/assignable-users", headers=user_headers)

    assert response.status_code == 200


def test_get_assignable_users_returns_limited_non_admin_results(client, admin_headers, user_factory):
    alpha = user_factory(
        first_name="Alex",
        last_name="Fade",
        email="alex.fade@example.com",
    )
    bravo = user_factory(
        first_name="Chris",
        last_name="Clipper",
        email="chris.clipper@example.com",
    )

    response = client.get("/users/assignable-users", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": alpha.id,
            "first_name": "Alex",
            "last_name": "Fade",
            "role": UserRole.BARBER.value,
        },
        {
            "id": bravo.id,
            "first_name": "Chris",
            "last_name": "Clipper",
            "role": UserRole.BARBER.value,
        },
    ]
