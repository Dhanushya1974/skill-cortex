from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.slot import Slot
from app.models.webinar import Webinar
from app.schemas.slot import SlotCreate, SlotOut, SlotUpdate
from app.utils.deps import require_admin

router = APIRouter(tags=["slots"])


@router.post("/webinars/{webinar_id}/slots", response_model=SlotOut, status_code=status.HTTP_201_CREATED)
def create_slot(
    webinar_id: int,
    payload: SlotCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    webinar = db.get(Webinar, webinar_id)
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    slot = Slot(webinar_id=webinar_id, available_seats=payload.capacity, **payload.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.patch("/slots/{slot_id}", response_model=SlotOut)
def update_slot(
    slot_id: int,
    payload: SlotUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    slot = db.get(Slot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(slot, field, value)
    db.commit()
    db.refresh(slot)
    return slot
