import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import auth, bookings, departments, health, notifications, payments, reminders, slots, users, webinars
from app.scheduler.reminder_scheduler import run_reminder_check

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(run_reminder_check, "cron", hour=9, minute=0, id="daily_reminders")
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Skill Cortex API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(webinars.router)
app.include_router(slots.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(notifications.router)
app.include_router(reminders.router)
app.include_router(users.router)
