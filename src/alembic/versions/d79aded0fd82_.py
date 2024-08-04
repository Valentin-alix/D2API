"""empty message

Revision ID: d79aded0fd82
Revises: 84cef97cd767
Create Date: 2024-08-03 09:58:37.972837

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d79aded0fd82"
down_revision: Union[str, None] = "84cef97cd767"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE character DROP COLUMN IF EXISTS is_sub;")
    op.execute("ALTER TABLE character DROP COLUMN IF EXISTS time_spent;")
    op.execute("ALTER TABLE map DROP COLUMN IF EXISTS allow_monster_fight;")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("map", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "allow_monster_fight", sa.BOOLEAN(), autoincrement=False, nullable=False
            )
        )

    with op.batch_alter_table("character", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("is_sub", sa.BOOLEAN(), autoincrement=False, nullable=False)
        )
        batch_op.add_column(
            sa.Column(
                "time_spent",
                sa.DOUBLE_PRECISION(precision=53),
                autoincrement=False,
                nullable=False,
            )
        )

    # ### end Alembic commands ###