from tests.conftest import auth_headers


def _create_webinar_and_slot(client, admin_token, department_id, capacity=1):
    webinar_resp = client.post(
        "/webinars",
        json={
            "title": "Python Programming",
            "description": "Intro",
            "department_id": department_id,
            "price": 999,
            "duration_minutes": 60,
        },
        headers=auth_headers(admin_token),
    )
    assert webinar_resp.status_code == 201
    webinar_id = webinar_resp.json()["id"]

    slot_resp = client.post(
        f"/webinars/{webinar_id}/slots",
        json={
            "date": "2026-12-01",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "capacity": capacity,
        },
        headers=auth_headers(admin_token),
    )
    assert slot_resp.status_code == 201
    slot_id = slot_resp.json()["id"]
    return webinar_id, slot_id


def _register_and_login(client, department_id, email):
    client.post(
        "/auth/register",
        json={
            "name": "Booker",
            "email": email,
            "phone": "9000000010",
            "password": "Passw0rd!",
            "department_id": department_id,
        },
    )
    resp = client.post("/auth/login", json={"email": email, "password": "Passw0rd!"})
    return resp.json()["access_token"]


def test_booking_requires_auth(client, admin_token, department):
    _, slot_id = _create_webinar_and_slot(client, admin_token, department.id)
    resp = client.post("/bookings", json={"webinar_id": 1, "slot_id": slot_id})
    assert resp.status_code == 401


def test_booking_decrements_available_seats(client, admin_token, user_token, department):
    webinar_id, slot_id = _create_webinar_and_slot(client, admin_token, department.id, capacity=5)
    resp = client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "PENDING"
    assert resp.json()["slot"]["available_seats"] == 4


def test_booking_rejects_duplicate_by_same_user(client, admin_token, user_token, department):
    webinar_id, slot_id = _create_webinar_and_slot(client, admin_token, department.id, capacity=5)
    client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(user_token),
    )
    resp = client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 400


def test_booking_rejects_when_slot_full(client, admin_token, user_token, department):
    webinar_id, slot_id = _create_webinar_and_slot(client, admin_token, department.id, capacity=1)
    other_token = _register_and_login(client, department.id, "other@example.com")

    first = client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(user_token),
    )
    assert first.status_code == 201

    second = client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(other_token),
    )
    assert second.status_code == 400
    assert "full" in second.json()["detail"].lower()


def test_booking_rejects_inactive_slot(client, admin_token, user_token, department):
    webinar_id, slot_id = _create_webinar_and_slot(client, admin_token, department.id, capacity=5)
    client.patch(
        f"/slots/{slot_id}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )
    resp = client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 400


def test_my_bookings_only_returns_own_bookings(client, admin_token, user_token, department):
    webinar_id, slot_id = _create_webinar_and_slot(client, admin_token, department.id, capacity=5)
    other_token = _register_and_login(client, department.id, "other2@example.com")

    client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(user_token),
    )

    mine = client.get("/bookings/me", headers=auth_headers(user_token))
    assert len(mine.json()) == 1

    others = client.get("/bookings/me", headers=auth_headers(other_token))
    assert len(others.json()) == 0
