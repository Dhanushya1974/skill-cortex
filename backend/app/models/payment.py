import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class PaymentStatus(str, enum.Enum):
    pending = "PENDING"
    paid = "PAID"
    failed = "FAILED"
    refunded = "REFUNDED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    razorpay_order_id = Column(String(100), nullable=False)
    razorpay_payment_id = Column(String(100))
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.pending, nullable=False)
    paid_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking")
