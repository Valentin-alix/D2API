"""

Revision ID: f01116de10ef
Revises: 3bb05417e9d9
Create Date: 2024-08-15 15:22:49.918824

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f01116de10ef"
down_revision: Union[str, None] = "3bb05417e9d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("character_path_map")
    op.drop_table("character_path_info")
    pass


def downgrade() -> None:
    pass
