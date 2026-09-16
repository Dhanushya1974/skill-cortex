import logging
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app.config import settings
from app.models.notification import Notification, NotificationChannel, NotificationStatus, NotificationType
from app.models.user import User

logger = logging.getLogger("notifications")


def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured; skipping email to %s: %s", to_email, subject)
        return False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


def _send_sms(phone: str | None, message: str) -> bool:
    # No SMS provider is configured yet (architecture doc: "SMS provider to be
    # selected during implementation"). This logs instead of delivering, so the
    # notification pipeline and status tracking work end-to-end already — swap
    # this for a real provider (Twilio, MSG91, etc.) without touching callers.
    logger.info("[SMS stub, not delivered] to=%s message=%s", phone, message)
    return False


def notify(
    db: Session,
    *,
    user: User,
    type_: NotificationType,
    message: str,
    subject: str = "Skill Cortex Notification",
    booking_id: int | None = None,
    channel: NotificationChannel = NotificationChannel.email,
    reminder_offset_days: int | None = None,
) -> Notification:
    if channel == NotificationChannel.email:
        sent = send_email(user.email, subject, message)
    else:
        sent = _send_sms(user.phone, message)

    notification = Notification(
        user_id=user.id,
        booking_id=booking_id,
        type=type_,
        channel=channel,
        message=message,
        status=NotificationStatus.sent if sent else NotificationStatus.failed,
        sent_at=datetime.now(timezone.utc) if sent else None,
        reminder_offset_days=reminder_offset_days,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
