from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.slot import SlotOut
from app.schemas.user import UserOut
from app.schemas.webinar import WebinarOut


class BookingCreate(BaseModel):
    webinar_id: int
    slot_id: int


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    webinar: WebinarOut
    slot: SlotOut


class BookingAdminOut(BookingOut):
    user: UserOut
