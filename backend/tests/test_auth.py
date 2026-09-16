from tests.conftest import auth_headers


def test_register_creates_user(client, department):
    resp = client.post(
        "/auth/register",
        json={
            "name": "Aditi Sharma",
            "email": "aditi@example.com",
            "phone": "9000000000",
            "password": "Passw0rd!",
            "department_id": department.id,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "aditi@example.com"
    assert body["role"] == "user"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_rejected(client, department):
    payload = {
        "name": "Aditi Sharma",
        "email": "aditi@example.com",
        "phone": "9000000000",
        "password": "Passw0rd!",
        "department_id": department.id,
    }
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_register_rejects_weak_password(client, department):
    resp = client.post(
        "/auth/register",
        json={
            "name": "Weak Password",
            "email": "weak@example.com",
            "phone": "9000000000",
            "password": "123",
            "department_id": department.id,
        },
    )
    assert resp.status_code == 422


def test_register_invalid_department_rejected(client):
    resp = client.post(
        "/auth/register",
        json={
            "name": "Aditi Sharma",
            "email": "aditi@example.com",
            "phone": "9000000000",
            "password": "Passw0rd!",
            "department_id": 999,
        },
    )
    assert resp.status_code == 400


def test_login_wrong_password_rejected(client, department):
    client.post(
        "/auth/register",
        json={
            "name": "Aditi Sharma",
            "email": "aditi@example.com",
            "phone": "9000000000",
            "password": "Passw0rd!",
            "department_id": department.id,
        },
    )
    resp = client.post("/auth/login", json={"email": "aditi@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, user_token):
    resp = client.get("/auth/me", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@example.com"


def test_admin_only_route_rejects_regular_user(client, user_token):
    resp = client.post(
        "/departments",
        json={"name": "New Dept"},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 403


def test_admin_only_route_allows_admin(client, admin_token):
    resp = client.post(
        "/departments",
        json={"name": "New Dept"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201
