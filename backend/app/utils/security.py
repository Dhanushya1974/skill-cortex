import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire, "typ": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    if payload.get("typ") != "access":
        raise jwt.InvalidTokenError("Not an access token")
    return payload


RESET_TOKEN_EXPIRE_MINUTES = 15


def _password_fingerprint(password_hash: str) -> str:
    # Binds the reset token to the password hash at issuance time, so using
    # the token once (which changes the hash) invalidates it even though it's
    # a stateless JWT with no server-side revocation list.
    return hashlib.sha256(password_hash.encode("utf-8")).hexdigest()[:16]


def create_reset_token(subject: str, current_password_hash: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "exp": expire,
        "typ": "reset",
        "pwf": _password_fingerprint(current_password_hash),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_reset_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    if payload.get("typ") != "reset":
        raise jwt.InvalidTokenError("Not a reset token")
    return payload


def reset_token_still_valid(payload: dict, current_password_hash: str) -> bool:
    """False once the password has changed since the token was issued (single-use)."""
    return payload.get("pwf") == _password_fingerprint(current_password_hash)
