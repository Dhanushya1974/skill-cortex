from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai import types
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from app.schemas.assistant import ChatRequest, ChatResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/assistant", tags=["assistant"])

MAX_HISTORY_MESSAGES = 12

SYSTEM_PROMPT = (
    "You are the Skill Cortex AI assistant, embedded in the Skill Cortex webinar "
    "booking platform. Help the logged-in user with questions about their bookings, "
    "payments, webinars, departments, and how the platform works (booking a slot, "
    "paying via Razorpay, reminders, password reset). Use the account context below "
    "to answer personally when relevant. Keep answers short and friendly. You cannot "
    "perform actions yourself (you cannot book, cancel, or refund anything) — if "
    "asked to do something, tell the user which page or button to use instead. If "
    "you don't know something, say so plainly."
)


def _build_context(db: Session, user: User) -> str:
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.webinar), joinedload(Booking.slot))
        .filter(Booking.user_id == user.id)
        .order_by(Booking.created_at.desc())
        .limit(10)
        .all()
    )
    booking_lines = [
        f"- '{b.webinar.title}' on {b.slot.date} at {b.slot.start_time}: {b.status.value}" for b in bookings
    ] or ["- No bookings yet."]

    payments = (
        db.query(Payment)
        .join(Booking)
        .filter(Booking.user_id == user.id)
        .order_by(Payment.created_at.desc())
        .limit(10)
        .all()
    )
    payment_lines = [
        f"- Rs.{p.amount} for booking #{p.booking_id}: {p.status.value}" for p in payments
    ] or ["- No payments yet."]

    return (
        f"User: {user.name} ({user.email}), role: {user.role.value}.\n"
        "Their bookings:\n" + "\n".join(booking_lines) + "\n"
        "Their payments:\n" + "\n".join(payment_lines)
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="AI assistant is not configured yet.")

    context = _build_context(db, current_user)
    history = payload.history[-MAX_HISTORY_MESSAGES:]

    contents = [
        types.Content(role="model" if m.role == "assistant" else "user", parts=[types.Part(text=m.content)])
        for m in history
    ]
    contents.append(types.Content(role="user", parts=[types.Part(text=payload.message)]))

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=f"{SYSTEM_PROMPT}\n\nAccount context:\n{context}",
                max_output_tokens=1024,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Assistant request failed: {exc}")

    return ChatResponse(reply=response.text or "Sorry, I couldn't come up with a response.")
