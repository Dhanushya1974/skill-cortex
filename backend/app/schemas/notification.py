from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserOut


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int | None
    type: str
    channel: str
    message: str
    status: str
    sent_at: datetime | None
    created_at: datetime


class NotificationAdminOut(NotificationOut):
    user: UserOut
