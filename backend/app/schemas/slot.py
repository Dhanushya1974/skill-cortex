from datetime import date, time

from pydantic import BaseModel, ConfigDict


class SlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    webinar_id: int
    date: date
    start_time: time
    end_time: time
    capacity: int
    available_seats: int
    is_active: bool


class SlotCreate(BaseModel):
    date: date
    start_time: time
    end_time: time
    capacity: int


class SlotUpdate(BaseModel):
    capacity: int | None = None
    is_active: bool | None = None
