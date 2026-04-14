"""add owner_id and surprise_mode to item_read_models

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "item_read_models",
        sa.Column("owner_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "item_read_models",
        sa.Column("surprise_mode", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("item_read_models", "surprise_mode")
    op.drop_column("item_read_models", "owner_id")
