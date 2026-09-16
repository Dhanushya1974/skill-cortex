from datetime import date, time, timedelta

from app.models.booking import Booking, BookingStatus
from app.models.notification import Notification, NotificationType
from app.models.slot import Slot
from app.models.user import User, UserRole
from app.models.webinar import Webinar
from app.scheduler import reminder_scheduler
from app.utils.security import hash_password
from tests.conftest import TestingSessionLocal


def _confirmed_booking(db_session, department, days_offset, email_suffix):
    webinar = Webinar(
        title="Reminder Test",
        description="d",
        department_id=department.id,
        price=100,
        duration_minutes=30,
        is_active=True,
    )
    db_session.add(webinar)
    db_session.commit()
    db_session.refresh(webinar)

    slot = Slot(
        webinar_id=webinar.id,
        date=date.today() + timedelta(days=days_offset),
        start_time=time(14, 0),
        end_time=time(15, 0),
        capacity=10,
        available_seats=9,
        is_active=True,
    )
    db_session.add(slot)
    db_session.commit()
    db_session.refresh(slot)

    user = User(
        name="Reminder User",
        email=f"reminder{email_suffix}@example.com",
        phone="9000000030",
        password_hash=hash_password("Passw0rd!"),
        department_id=department.id,
        role=UserRole.user,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    booking = Booking(user_id=user.id, webinar_id=webinar.id, slot_id=slot.id, status=BookingStatus.confirmed)
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking


def test_reminder_sent_only_for_due_offsets(db_session, department, monkeypatch):
    monkeypatch.setattr(reminder_scheduler, "SessionLocal", TestingSessionLocal)

    due_3 = _confirmed_booking(db_session, department, 3, "3")
    due_1 = _confirmed_booking(db_session, department, 1, "1")
    due_0 = _confirmed_booking(db_session, department, 0, "0")
    not_due = _confirmed_booking(db_session, department, 5, "5")

    sent = reminder_scheduler.run_reminder_check()
    assert sent == 3

    reminded_ids = {
        n.booking_id
        for n in db_session.query(Notification).filter(Notification.type == NotificationType.reminder).all()
    }
    assert reminded_ids == {due_3.id, due_1.id, due_0.id}
    assert not_due.id not in reminded_ids


def test_reminder_not_duplicated_on_repeated_runs(db_session, department, monkeypatch):
    monkeypatch.setattr(reminder_scheduler, "SessionLocal", TestingSessionLocal)
    _confirmed_booking(db_session, department, 1, "dup")

    first = reminder_scheduler.run_reminder_check()
    second = reminder_scheduler.run_reminder_check()
    third = reminder_scheduler.run_reminder_check()

    assert first == 1
    assert second == 0
    assert third == 0


def test_reminder_not_sent_for_pending_booking(db_session, department, monkeypatch):
    monkeypatch.setattr(reminder_scheduler, "SessionLocal", TestingSessionLocal)
    booking = _confirmed_booking(db_session, department, 0, "pending")
    booking.status = BookingStatus.pending
    db_session.commit()

    sent = reminder_scheduler.run_reminder_check()
    assert sent == 0
