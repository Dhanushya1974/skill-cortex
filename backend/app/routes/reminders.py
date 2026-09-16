from fastapi import APIRouter, Depends

from app.models.user import User
from app.scheduler.reminder_scheduler import run_reminder_check
from app.utils.deps import require_admin

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/run")
def trigger_reminders(_admin: User = Depends(require_admin)):
    sent = run_reminder_check()
    return {"sent": sent}
