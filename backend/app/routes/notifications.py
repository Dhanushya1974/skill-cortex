from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationAdminOut, NotificationOut
from app.utils.deps import get_current_user, require_admin

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=list[NotificationOut])
def my_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.get("", response_model=list[NotificationAdminOut])
def list_notifications(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return (
        db.query(Notification)
        .options(joinedload(Notification.user))
        .order_by(Notification.created_at.desc())
        .all()
    )
