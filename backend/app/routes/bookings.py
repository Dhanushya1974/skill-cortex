from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.booking import Booking
from app.models.slot import Slot
from app.models.user import User
from app.schemas.booking import BookingAdminOut, BookingCreate, BookingOut
from app.utils.deps import get_current_user, require_admin

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slot = db.get(Slot, payload.slot_id)
    if not slot or slot.webinar_id != payload.webinar_id or not slot.is_active:
        raise HTTPException(status_code=400, detail="Invalid or unavailable slot")

    result = db.execute(
        update(Slot)
        .where(Slot.id == slot.id, Slot.available_seats > 0)
        .values(available_seats=Slot.available_seats - 1)
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=400, detail="Slot is fully booked")

    booking = Booking(user_id=current_user.id, webinar_id=payload.webinar_id, slot_id=payload.slot_id)
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="You have already booked this slot")

    db.refresh(booking)
    return (
        db.query(Booking)
        .options(joinedload(Booking.webinar), joinedload(Booking.slot))
        .filter(Booking.id == booking.id)
        .first()
    )


@router.get("/me", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Booking)
        .options(joinedload(Booking.webinar), joinedload(Booking.slot))
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.get("", response_model=list[BookingAdminOut])
def list_bookings(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return (
        db.query(Booking)
        .options(joinedload(Booking.webinar), joinedload(Booking.slot), joinedload(Booking.user))
        .order_by(Booking.created_at.desc())
        .all()
    )
