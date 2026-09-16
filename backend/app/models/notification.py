import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class NotificationType(str, enum.Enum):
    registration = "REGISTRATION"
    booking_confirmation = "BOOKING_CONFIRMATION"
    payment_notification = "PAYMENT_NOTIFICATION"
    reminder = "REMINDER"
    cancellation = "CANCELLATION"


class NotificationChannel(str, enum.Enum):
    email = "EMAIL"
    sms = "SMS"


class NotificationStatus(str, enum.Enum):
    pending = "PENDING"
    sent = "SENT"
    failed = "FAILED"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    type = Column(Enum(NotificationType, name="notification_type"), nullable=False)
    channel = Column(Enum(NotificationChannel, name="notification_channel"), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus, name="notification_status"), default=NotificationStatus.pending, nullable=False)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reminder_offset_days = Column(Integer, nullable=True)

    user = relationship("User")
    booking = relationship("Booking")
