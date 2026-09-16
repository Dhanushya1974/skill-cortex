import hashlib
import hmac

from app.config import settings
from tests.conftest import auth_headers


def _confirmed_booking_setup(client, admin_token, user_token, department):
    webinar_resp = client.post(
        "/webinars",
        json={
            "title": "ML",
            "description": "d",
            "department_id": department.id,
            "price": 500,
            "duration_minutes": 60,
        },
        headers=auth_headers(admin_token),
    )
    webinar_id = webinar_resp.json()["id"]

    slot_resp = client.post(
        f"/webinars/{webinar_id}/slots",
        json={"date": "2026-12-01", "start_time": "10:00:00", "end_time": "11:00:00", "capacity": 5},
        headers=auth_headers(admin_token),
    )
    slot_id = slot_resp.json()["id"]

    booking_resp = client.post(
        "/bookings",
        json={"webinar_id": webinar_id, "slot_id": slot_id},
        headers=auth_headers(user_token),
    )
    return booking_resp.json()["id"]


def _register_and_login(client, department_id, email):
    client.post(
        "/auth/register",
        json={
            "name": "Other",
            "email": email,
            "phone": "9000000020",
            "password": "Passw0rd!",
            "department_id": department_id,
        },
    )
    return client.post("/auth/login", json={"email": email, "password": "Passw0rd!"}).json()["access_token"]


def _sign(order_id, payment_id):
    msg = f"{order_id}|{payment_id}"
    return hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()


def test_create_order_rejects_other_users_booking(client, admin_token, user_token, department):
    booking_id = _confirmed_booking_setup(client, admin_token, user_token, department)
    other_token = _register_and_login(client, department.id, "other@example.com")

    resp = client.post("/payments/create-order", json={"booking_id": booking_id}, headers=auth_headers(other_token))
    assert resp.status_code == 404


def test_create_order_calls_razorpay_and_returns_order(client, admin_token, user_token, department, monkeypatch):
    booking_id = _confirmed_booking_setup(client, admin_token, user_token, department)
    monkeypatch.setattr(
        "app.routes.payments.razorpay_client.order.create",
        lambda data: {"id": "order_fake123"},
    )

    resp = client.post("/payments/create-order", json={"booking_id": booking_id}, headers=auth_headers(user_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["order_id"] == "order_fake123"
    assert body["amount"] == 50000  # price 500 * 100 paise


def test_verify_payment_rejects_forged_signature(client, admin_token, user_token, department, monkeypatch):
    booking_id = _confirmed_booking_setup(client, admin_token, user_token, department)
    monkeypatch.setattr("app.routes.payments.razorpay_client.order.create", lambda data: {"id": "order_forge1"})
    client.post("/payments/create-order", json={"booking_id": booking_id}, headers=auth_headers(user_token))

    resp = client.post(
        "/payments/verify",
        json={
            "razorpay_order_id": "order_forge1",
            "razorpay_payment_id": "pay_forge1",
            "razorpay_signature": "deadbeef0000",
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 400

    mine = client.get("/bookings/me", headers=auth_headers(user_token)).json()
    assert mine[0]["status"] == "PENDING"


def test_verify_payment_confirms_booking_on_valid_signature(client, admin_token, user_token, department, monkeypatch):
    booking_id = _confirmed_booking_setup(client, admin_token, user_token, department)
    monkeypatch.setattr("app.routes.payments.razorpay_client.order.create", lambda data: {"id": "order_valid1"})
    client.post("/payments/create-order", json={"booking_id": booking_id}, headers=auth_headers(user_token))

    signature = _sign("order_valid1", "pay_valid1")
    resp = client.post(
        "/payments/verify",
        json={
            "razorpay_order_id": "order_valid1",
            "razorpay_payment_id": "pay_valid1",
            "razorpay_signature": signature,
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "PAID"

    mine = client.get("/bookings/me", headers=auth_headers(user_token)).json()
    assert mine[0]["status"] == "CONFIRMED"


def test_verify_payment_rejects_cross_user_access(client, admin_token, user_token, department, monkeypatch):
    booking_id = _confirmed_booking_setup(client, admin_token, user_token, department)
    monkeypatch.setattr("app.routes.payments.razorpay_client.order.create", lambda data: {"id": "order_cross1"})
    client.post("/payments/create-order", json={"booking_id": booking_id}, headers=auth_headers(user_token))
    cross_token = _register_and_login(client, department.id, "cross@example.com")

    signature = _sign("order_cross1", "pay_cross1")
    resp = client.post(
        "/payments/verify",
        json={
            "razorpay_order_id": "order_cross1",
            "razorpay_payment_id": "pay_cross1",
            "razorpay_signature": signature,
        },
        headers=auth_headers(cross_token),
    )
    assert resp.status_code == 404
