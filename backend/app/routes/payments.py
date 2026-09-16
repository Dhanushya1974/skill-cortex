from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from razorpay.errors import SignatureVerificationError
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.notification import NotificationType
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.schemas.payment import (
    CreateOrderRequest,
    CreateOrderResponse,
    PaymentAdminOut,
    PaymentOut,
    VerifyPaymentRequest,
)
from app.services.notification_service import notify
from app.utils.deps import get_current_user, require_admin
from app.utils.razorpay_client import client as razorpay_client

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
def create_order(
    payload: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.webinar))
        .filter(Booking.id == payload.booking_id)
        .first()
    )
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Booking is not awaiting payment")

    amount_paise = int(round(booking.webinar.price * 100))

    try:
        order = razorpay_client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"booking_{booking.id}",
                "payment_capture": 1,
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Razorpay order creation failed: {exc}")

    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if payment:
        payment.razorpay_order_id = order["id"]
        payment.amount = booking.webinar.price
        payment.status = PaymentStatus.pending
        payment.razorpay_payment_id = None
        payment.paid_at = None
    else:
        payment = Payment(
            booking_id=booking.id,
            razorpay_order_id=order["id"],
            amount=booking.webinar.price,
            status=PaymentStatus.pending,
        )
        db.add(payment)
    db.commit()

    return CreateOrderResponse(
        order_id=order["id"],
        amount=amount_paise,
        currency="INR",
        key_id=settings.RAZORPAY_KEY_ID,
        booking_id=booking.id,
    )


@router.post("/verify", response_model=PaymentOut)
def verify_payment(
    payload: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .options(
            joinedload(Payment.booking).joinedload(Booking.user),
            joinedload(Payment.booking).joinedload(Booking.webinar),
            joinedload(Payment.booking).joinedload(Booking.slot),
        )
        .filter(Payment.razorpay_order_id == payload.razorpay_order_id)
        .first()
    )
    if not payment or payment.booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment not found")

    try:
        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_order_id": payload.razorpay_order_id,
                "razorpay_payment_id": payload.razorpay_payment_id,
                "razorpay_signature": payload.razorpay_signature,
            }
        )
    except SignatureVerificationError:
        payment.status = PaymentStatus.failed
        db.commit()
        raise HTTPException(status_code=400, detail="Payment verification failed")

    payment.razorpay_payment_id = payload.razorpay_payment_id
    payment.status = PaymentStatus.paid
    payment.paid_at = datetime.now(timezone.utc)
    payment.booking.status = BookingStatus.confirmed
    db.commit()
    db.refresh(payment)

    booking = payment.booking
    notify(
        db,
        user=booking.user,
        type_=NotificationType.booking_confirmation,
        booking_id=booking.id,
        subject="Booking Confirmed - Skill Cortex",
        message=(
            f"Hi {booking.user.name}, your booking for '{booking.webinar.title}' on "
            f"{booking.slot.date} at {booking.slot.start_time} is confirmed. "
            f"Amount paid: Rs.{payment.amount}. Payment reference: {payment.razorpay_payment_id}."
        ),
    )

    admins = db.query(User).filter(User.role == UserRole.admin).all()
    for admin in admins:
        notify(
            db,
            user=admin,
            type_=NotificationType.payment_notification,
            booking_id=booking.id,
            subject="New Payment Received - Skill Cortex",
            message=(
                f"{booking.user.name} ({booking.user.email}) paid Rs.{payment.amount} for "
                f"'{booking.webinar.title}' — payment status PAID."
            ),
        )

    return payment


@router.get("", response_model=list[PaymentAdminOut])
def list_payments(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return (
        db.query(Payment)
        .options(
            joinedload(Payment.booking).joinedload(Booking.user),
            joinedload(Payment.booking).joinedload(Booking.webinar),
            joinedload(Payment.booking).joinedload(Booking.slot),
        )
        .order_by(Payment.created_at.desc())
        .all()
    )
