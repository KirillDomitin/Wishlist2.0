"""create wishlist tables

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
        "wishlists",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("share_token", sa.String(64), nullable=False, unique=True),
        sa.Column("surprise_mode", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_wishlists_owner_id", "wishlists", ["owner_id"])

    op.create_table(
        "wishlist_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "wishlist_id",
            UUID(as_uuid=True),
            sa.ForeignKey("wishlists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("target_quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("reserved_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_wishlist_items_wishlist_id", "wishlist_items", ["wishlist_id"])


def downgrade() -> None:
    op.drop_table("wishlist_items")
    op.drop_index("ix_wishlists_owner_id", table_name="wishlists")
    op.drop_table("wishlists")
