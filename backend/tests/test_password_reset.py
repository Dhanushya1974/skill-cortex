import re

from tests.conftest import auth_headers


def _register(client, department, email="reset@example.com", password="Passw0rd!"):
    client.post(
        "/auth/register",
        json={
            "name": "Reset User",
            "email": email,
            "phone": "9000000040",
            "password": password,
            "department_id": department.id,
        },
    )


def _extract_token(caplog):
    for record in caplog.records:
        match = re.search(r"token=([^\s&]+)", record.message)
        if match:
            return match.group(1)
    raise AssertionError("reset link was not logged")


def test_forgot_password_does_not_leak_whether_email_exists(client, department):
    _register(client, department)
    resp_known = client.post("/auth/forgot-password", json={"email": "reset@example.com"})
    resp_unknown = client.post("/auth/forgot-password", json={"email": "nosuchuser@example.com"})
    assert resp_known.status_code == 200
    assert resp_unknown.status_code == 200
    assert resp_known.json() == resp_unknown.json()


def test_reset_password_with_valid_token_updates_password(client, department, caplog):
    _register(client, department)
    with caplog.at_level("INFO"):
        client.post("/auth/forgot-password", json={"email": "reset@example.com"})
    token = _extract_token(caplog)

    resp = client.post("/auth/reset-password", json={"token": token, "new_password": "NewPass123!"})
    assert resp.status_code == 200

    old_login = client.post("/auth/login", json={"email": "reset@example.com", "password": "Passw0rd!"})
    assert old_login.status_code == 401

    new_login = client.post("/auth/login", json={"email": "reset@example.com", "password": "NewPass123!"})
    assert new_login.status_code == 200


def test_reset_token_cannot_be_replayed(client, department, caplog):
    _register(client, department)
    with caplog.at_level("INFO"):
        client.post("/auth/forgot-password", json={"email": "reset@example.com"})
    token = _extract_token(caplog)

    first = client.post("/auth/reset-password", json={"token": token, "new_password": "NewPass123!"})
    assert first.status_code == 200

    second = client.post("/auth/reset-password", json={"token": token, "new_password": "AnotherPass1!"})
    assert second.status_code == 400


def test_reset_password_rejects_garbage_token(client):
    resp = client.post("/auth/reset-password", json={"token": "not-a-real-token", "new_password": "NewPass123!"})
    assert resp.status_code == 400


def test_access_token_cannot_be_used_as_reset_token(client, user_token):
    resp = client.post("/auth/reset-password", json={"token": user_token, "new_password": "NewPass123!"})
    assert resp.status_code == 400
