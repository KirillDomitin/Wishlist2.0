"""add item details to item_read_models

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "item_read_models",
        sa.Column("title", sa.String(255), nullable=False, server_default=""),
    )
    op.add_column(
        "item_read_models",
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "item_read_models",
        sa.Column("image_url", sa.String(2048), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("item_read_models", "image_url")
    op.drop_column("item_read_models", "price")
    op.drop_column("item_read_models", "title")
