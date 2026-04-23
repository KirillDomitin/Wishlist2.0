"""add item priority and wishlist event_date

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "wishlist_items",
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "wishlists",
        sa.Column("event_date", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("wishlist_items", "priority")
    op.drop_column("wishlists", "event_date")