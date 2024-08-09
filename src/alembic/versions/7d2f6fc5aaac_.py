"""empty message

Revision ID: 7d2f6fc5aaac
Revises: 491d8aaa6926
Create Date: 2024-08-09 15:29:42.849411

"""

import sqlalchemy as sa
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7d2f6fc5aaac"
down_revision: Union[str, None] = "491d8aaa6926"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "character_sell_item_info",
        "character_id",
        type_=sa.String,
        existing_type=sa.INTEGER,
    )


def downgrade() -> None:
    op.alter_column(
        "character_sell_item_info",
        "character_id",
        type_=sa.INTEGER,
        existing_type=sa.String,
    )
