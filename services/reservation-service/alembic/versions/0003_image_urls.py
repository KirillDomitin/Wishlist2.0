"""replace image_url with image_urls array in item_read_models

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "item_read_models",
        sa.Column("image_urls", ARRAY(sa.Text()), nullable=False, server_default="{}"),
    )
    op.execute(
        "UPDATE item_read_models SET image_urls = ARRAY[image_url] WHERE image_url IS NOT NULL"
    )
    op.drop_column("item_read_models", "image_url")


def downgrade() -> None:
    op.add_column(
        "item_read_models",
        sa.Column("image_url", sa.String(2048), nullable=True),
    )
    op.execute(
        "UPDATE item_read_models SET image_url = image_urls[1] WHERE array_length(image_urls, 1) > 0"
    )
    op.drop_column("item_read_models", "image_urls")
