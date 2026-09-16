import logging
from datetime import date, time

from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.notification import Notification, NotificationType
from app.services.notification_service import notify

logger = logging.getLogger("reminders")

# Days-before-slot milestones a reminder should fire at. Configurable per FR-12.
REMINDER_OFFSETS_DAYS = [3, 1, 0]


def _reminder_message(webinar_title: str, days_before: int, start_time: time) -> str:
    if days_before == 3:
        return f"Your {webinar_title} webinar is in 3 days."
    if days_before == 1:
        return f"Your {webinar_title} webinar is tomorrow at {start_time}."
    return f"Reminder: Your {webinar_title} webinar starts today at {start_time}."


def _already_sent(db: Session, booking_id: int, days_before: int) -> bool:
    return (
        db.query(Notification)
        .filter(
            Notification.booking_id == booking_id,
            Notification.type == NotificationType.reminder,
            Notification.reminder_offset_days == days_before,
        )
        .first()
        is not None
    )


def run_reminder_check() -> int:
    """Send due reminders for confirmed, paid bookings. Returns count sent.

    BR-08: only confirmed bookings get reminders. BR-09: each (booking, offset)
    milestone is sent at most once, tracked via Notification.reminder_offset_days.
    """
    db = SessionLocal()
    sent_count = 0
    try:
        today = date.today()
        bookings = (
            db.query(Booking)
            .options(joinedload(Booking.webinar), joinedload(Booking.slot), joinedload(Booking.user))
            .filter(Booking.status == BookingStatus.confirmed)
            .all()
        )
        for booking in bookings:
            days_until = (booking.slot.date - today).days
            if days_until not in REMINDER_OFFSETS_DAYS:
                continue
            if _already_sent(db, booking.id, days_until):
                continue

            message = _reminder_message(booking.webinar.title, days_until, booking.slot.start_time)
            notify(
                db,
                user=booking.user,
                type_=NotificationType.reminder,
                booking_id=booking.id,
                subject="Webinar Reminder - Skill Cortex",
                message=message,
                reminder_offset_days=days_until,
            )
            sent_count += 1
            logger.info("Sent %sd-before reminder for booking %s", days_until, booking.id)
    finally:
        db.close()
    return sent_count
