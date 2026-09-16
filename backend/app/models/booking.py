import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


class BookingStatus(str, enum.Enum):
    pending = "PENDING"
    confirmed = "CONFIRMED"
    cancelled = "CANCELLED"


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint("user_id", "slot_id", name="uq_booking_user_slot"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    webinar_id = Column(Integer, ForeignKey("webinars.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False)
    status = Column(Enum(BookingStatus, name="booking_status"), default=BookingStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    webinar = relationship("Webinar")
    slot = relationship("Slot")
