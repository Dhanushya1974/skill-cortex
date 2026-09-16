from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.department import Department
from app.models.webinar import Webinar
from app.schemas.webinar import WebinarCreate, WebinarDetailOut, WebinarOut, WebinarUpdate
from app.utils.deps import require_admin

router = APIRouter(prefix="/webinars", tags=["webinars"])


@router.get("", response_model=list[WebinarOut])
def list_webinars(department_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Webinar).filter(Webinar.is_active.is_(True))
    if department_id is not None:
        query = query.filter(Webinar.department_id == department_id)
    return query.all()


@router.get("/admin/all", response_model=list[WebinarOut])
def list_all_webinars(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(Webinar).order_by(Webinar.title).all()


@router.get("/{webinar_id}", response_model=WebinarDetailOut)
def get_webinar(webinar_id: int, db: Session = Depends(get_db)):
    webinar = (
        db.query(Webinar)
        .options(joinedload(Webinar.slots))
        .filter(Webinar.id == webinar_id)
        .first()
    )
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    return webinar


@router.post("", response_model=WebinarOut, status_code=status.HTTP_201_CREATED)
def create_webinar(payload: WebinarCreate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    if not db.get(Department, payload.department_id):
        raise HTTPException(status_code=400, detail="Invalid department")
    webinar = Webinar(**payload.model_dump())
    db.add(webinar)
    db.commit()
    db.refresh(webinar)
    return webinar


@router.patch("/{webinar_id}", response_model=WebinarOut)
def update_webinar(
    webinar_id: int,
    payload: WebinarUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    webinar = db.get(Webinar, webinar_id)
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(webinar, field, value)
    db.commit()
    db.refresh(webinar)
    return webinar
