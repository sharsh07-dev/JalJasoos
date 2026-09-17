"""Seed initial data: roles + super admin user.

Revision ID: 0002_seed_roles_and_admin
Revises: 0001_initial_schema
Create Date: 2026-09-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext

revision: str = "0002_seed_roles_and_admin"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    now = datetime.now(timezone.utc)

    # Seed roles
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    role_data = [
        {"id": str(uuid.uuid4()), "name": "SUPER_ADMIN", "description": "Full system access"},
        {"id": str(uuid.uuid4()), "name": "FACILITY_MANAGER", "description": "Society-level management"},
        {"id": str(uuid.uuid4()), "name": "MAINTENANCE_STAFF", "description": "Zone-level maintenance tasks"},
        {"id": str(uuid.uuid4()), "name": "RESIDENT", "description": "Personal consumption and alerts only"},
    ]

    for r in role_data:
        r["created_at"] = now
        r["updated_at"] = now

    op.bulk_insert(roles_table, role_data)

    # Get SUPER_ADMIN role id
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM roles WHERE name = 'SUPER_ADMIN'"))
    super_admin_role_id = result.fetchone()[0]

    # Seed default super admin user
    users_table = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("email", sa.String),
        sa.column("full_name", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("role_id", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("is_verified", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    op.bulk_insert(users_table, [{
        "id": str(uuid.uuid4()),
        "email": "admin@jaljasoos.local",
        "full_name": "JalJasoos Super Admin",
        "hashed_password": pwd_context.hash("changeme"),  # MUST change in production
        "role_id": str(super_admin_role_id),
        "is_active": True,
        "is_verified": True,
        "created_at": now,
        "updated_at": now,
    }])


def downgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'admin@jaljasoos.local'")
    op.execute("DELETE FROM roles")
