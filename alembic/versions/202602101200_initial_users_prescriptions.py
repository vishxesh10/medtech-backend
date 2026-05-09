"""initial users and prescriptions

Revision ID: 202602101200
Revises:
Create Date: 2026-02-10

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "202602101200"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "prescriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=True),
        sa.Column("extracted_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prescriptions_id"), "prescriptions", ["id"], unique=False)
    op.create_index(op.f("ix_prescriptions_user_id"), "prescriptions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_prescriptions_user_id"), table_name="prescriptions")
    op.drop_index(op.f("ix_prescriptions_id"), table_name="prescriptions")
    op.drop_table("prescriptions")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
