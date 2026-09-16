# Skill Cortex

Webinar/course booking, payment (Razorpay) and notification platform. See the architecture, workflow and BRD PDFs in this folder for the full spec.

## Local setup (backend)

```bash
docker-compose up -d          # starts PostgreSQL
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`

The first migration seeds a bootstrap admin account (`admin@skillcortex.com` / `Admin@12345` by default). **Override this before running migrations against any shared or real database** by exporting real shell environment variables (not just editing `backend/.env` — Alembic reads these directly via `os.environ`, not through the app's `.env`-backed settings):

```bash
INITIAL_ADMIN_EMAIL=you@example.com INITIAL_ADMIN_PASSWORD='a-strong-password' alembic upgrade head
```

Rotate the admin password after first login regardless — the fallback default is visible in source control.

## Local setup (frontend)

```bash
cd frontend
npm install
npm run dev
```

## Running tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Tests run against an in-memory SQLite database and never touch the real Postgres instance.

## Configuration

Real third-party credentials go in `backend/.env` (gitignored):
- `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` — from the [Razorpay dashboard](https://dashboard.razorpay.com/app/keys) (test mode keys work for local dev)
- `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` — any SMTP provider; leave `SMTP_HOST` empty to skip sending (notifications are still recorded, marked `FAILED`)
- SMS is not wired to a provider yet — it's logged only (see `app/services/notification_service.py`)
