"""create reservation tables

Revision ID: 0001
Revises:
Create Date: 2026-04-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "item_read_models",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("wishlist_id", UUID(as_uuid=True), nullable=False),
        sa.Column("target_quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "reservations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "item_id",
            UUID(as_uuid=True),
            sa.ForeignKey("item_read_models.id"),
            nullable=False,
        ),
        sa.Column("reserver_id", UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "status",
            sa.Enum("active", "cancelled", name="reservationstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reservations_item_id", "reservations", ["item_id"])
    op.create_index("ix_reservations_reserver_id", "reservations", ["reserver_id"])


def downgrade() -> None:
    op.drop_index("ix_reservations_reserver_id", table_name="reservations")
    op.drop_index("ix_reservations_item_id", table_name="reservations")
    op.drop_table("reservations")
    op.execute("DROP TYPE IF EXISTS reservationstatus")
    op.drop_table("item_read_models")
