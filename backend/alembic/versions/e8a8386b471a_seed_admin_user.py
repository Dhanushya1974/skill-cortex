"""seed admin user

Revision ID: e8a8386b471a
Revises: 3c1b661e31ed
Create Date: 2026-09-13 22:21:57.369004

"""
import os

import bcrypt
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8a8386b471a'
down_revision = '3c1b661e31ed'
branch_labels = None
depends_on = None

ADMIN_EMAIL = os.environ.get("INITIAL_ADMIN_EMAIL", "admin@skillcortex.com")
# Never hardcode a real password in a version-controlled migration. This
# fallback is a known, publicly-visible dev default — override it via
# INITIAL_ADMIN_PASSWORD before running migrations against any shared or
# production database, and rotate it immediately after first login regardless.
ADMIN_PASSWORD = os.environ.get("INITIAL_ADMIN_PASSWORD", "Admin@12345")


def upgrade() -> None:
    bind = op.get_bind()

    departments_table = sa.table(
        "departments",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    cse_id = bind.execute(
        sa.select(departments_table.c.id).where(departments_table.c.name == "CSE")
    ).scalar_one()

    users_table = sa.table(
        "users",
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("phone", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("department_id", sa.Integer),
        sa.column("role", sa.String),
    )
    password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    op.bulk_insert(
        users_table,
        [
            {
                "name": "Skill Cortex Admin",
                "email": ADMIN_EMAIL,
                "phone": "0000000000",
                "password_hash": password_hash,
                "department_id": cse_id,
                "role": "admin",
            }
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    users_table = sa.table("users", sa.column("email", sa.String))
    bind.execute(users_table.delete().where(users_table.c.email == ADMIN_EMAIL))
