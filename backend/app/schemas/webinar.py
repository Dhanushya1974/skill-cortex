from pydantic import BaseModel, ConfigDict

from app.schemas.slot import SlotOut


class WebinarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    department_id: int
    price: float
    duration_minutes: int
    is_active: bool


class WebinarDetailOut(WebinarOut):
    slots: list[SlotOut] = []


class WebinarCreate(BaseModel):
    title: str
    description: str | None = None
    department_id: int
    price: float
    duration_minutes: int


class WebinarUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None
