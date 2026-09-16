from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.booking import BookingAdminOut


class CreateOrderRequest(BaseModel):
    booking_id: int


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str
    booking_id: int


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    razorpay_order_id: str
    razorpay_payment_id: str | None
    amount: float
    status: str
    paid_at: datetime | None


class PaymentAdminOut(PaymentOut):
    booking: BookingAdminOut
