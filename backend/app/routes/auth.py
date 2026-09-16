import logging

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.department import Department
from app.models.notification import NotificationType
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserOut,
)
from app.services.notification_service import notify, send_email
from app.utils.deps import get_current_user
from app.utils.security import (
    create_access_token,
    create_reset_token,
    decode_reset_token,
    hash_password,
    reset_token_still_valid,
    verify_password,
)

logger = logging.getLogger("auth")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    department = db.get(Department, payload.department_id)
    if not department:
        raise HTTPException(status_code=400, detail="Invalid department")

    department_other = payload.department_other.strip() if payload.department_other else None
    if department.name == "Other" and not department_other:
        raise HTTPException(status_code=400, detail="Please specify your department")

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        department_id=payload.department_id,
        department_other=department_other if department.name == "Other" else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    notify(
        db,
        user=user,
        type_=NotificationType.registration,
        subject="Welcome to Skill Cortex",
        message=f"Hi {user.name}, welcome to Skill Cortex! Your account has been created successfully.",
    )

    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    generic_response = {"message": "If that email is registered, a reset link has been sent."}

    if not user:
        # Don't reveal whether the email exists.
        return generic_response

    token = create_reset_token(subject=str(user.id), current_password_hash=user.password_hash)
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    sent = send_email(
        user.email,
        "Reset your Skill Cortex password",
        f"Hi {user.name}, click the link below to reset your password (valid for 15 minutes):\n\n{reset_link}",
    )
    if not sent:
        logger.info("[password reset link, not emailed] user=%s link=%s", user.email, reset_link)
        if settings.ENV != "production":
            # No SMTP configured (or delivery failed) — surface the link directly so
            # the reset flow is still usable in local/dev environments. Never do this
            # in production: it would let anyone reset any account's password.
            generic_response["reset_link"] = reset_link

    return generic_response


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        data = decode_reset_token(payload.token)
        user_id = int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    user = db.get(User, user_id)
    if not user or not reset_token_still_valid(data, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully."}
