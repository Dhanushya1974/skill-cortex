"""add department_other and seed degree branches

Revision ID: c2579b61034a
Revises: 605d8042a203
Create Date: 2026-09-16 12:00:01.517150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2579b61034a'
down_revision = '605d8042a203'
branch_labels = None
depends_on = None

NEW_DEPARTMENTS = [
    # B.Tech branches
    ("Information Technology", "B.Tech - Information Technology"),
    ("Electronics & Communication Engineering", "B.Tech - ECE"),
    ("Electrical & Electronics Engineering", "B.Tech - EEE"),
    ("Mechanical Engineering", "B.Tech - Mechanical Engineering"),
    ("Civil Engineering", "B.Tech - Civil Engineering"),
    ("Chemical Engineering", "B.Tech - Chemical Engineering"),
    ("Aeronautical Engineering", "B.Tech - Aeronautical/Aerospace Engineering"),
    ("Biotechnology Engineering", "B.Tech - Biotechnology Engineering"),
    ("Automobile Engineering", "B.Tech - Automobile Engineering"),
    ("Mining Engineering", "B.Tech - Mining Engineering"),
    ("Metallurgical Engineering", "B.Tech - Metallurgical Engineering"),
    ("Production Engineering", "B.Tech - Production Engineering"),
    ("Instrumentation Engineering", "B.Tech - Instrumentation Engineering"),
    ("Agricultural Engineering", "B.Tech - Agricultural Engineering"),
    ("Marine Engineering", "B.Tech - Marine Engineering"),
    ("Textile Engineering", "B.Tech - Textile Engineering"),
    ("Industrial Engineering", "B.Tech - Industrial Engineering"),
    ("Petroleum Engineering", "B.Tech - Petroleum Engineering"),
    ("Mechatronics Engineering", "B.Tech - Mechatronics Engineering"),
    ("Biomedical Engineering", "B.Tech - Biomedical Engineering"),
    ("Environmental Engineering", "B.Tech - Environmental Engineering"),
    ("Robotics Engineering", "B.Tech - Robotics Engineering"),
    # General degree programs
    ("B.Sc", "Bachelor of Science"),
    ("B.A", "Bachelor of Arts"),
    ("B.Com", "Bachelor of Commerce"),
    ("BBA", "Bachelor of Business Administration"),
    ("BCA", "Bachelor of Computer Applications"),
    ("B.Ed", "Bachelor of Education"),
    ("LLB", "Bachelor of Laws"),
    ("B.Pharm", "Bachelor of Pharmacy"),
    ("B.Arch", "Bachelor of Architecture"),
    ("BHM", "Bachelor of Hotel Management"),
    ("BPT", "Bachelor of Physiotherapy"),
    ("MBBS", "Bachelor of Medicine and Bachelor of Surgery"),
    ("BDS", "Bachelor of Dental Surgery"),
    ("B.Des", "Bachelor of Design"),
    ("BFA", "Bachelor of Fine Arts"),
    ("BSW", "Bachelor of Social Work"),
    ("BJMC", "Bachelor of Journalism and Mass Communication"),
    # Catch-all
    ("Other", "Not listed above - please specify"),
]


def upgrade() -> None:
    op.add_column("users", sa.Column("department_other", sa.String(length=255), nullable=True))

    bind = op.get_bind()
    departments_table = sa.table(
        "departments",
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    existing = {
        row[0] for row in bind.execute(sa.select(sa.column("name")).select_from(sa.table("departments", sa.column("name", sa.String))))
    }
    rows = [
        {"name": name, "description": description, "is_active": True}
        for name, description in NEW_DEPARTMENTS
        if name not in existing
    ]
    if rows:
        op.bulk_insert(departments_table, rows)


def downgrade() -> None:
    bind = op.get_bind()
    departments_table = sa.table("departments", sa.column("name", sa.String))
    names = [name for name, _ in NEW_DEPARTMENTS]
    bind.execute(departments_table.delete().where(departments_table.c.name.in_(names)))
    op.drop_column("users", "department_other")
