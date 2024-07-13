"""empty message

Revision ID: 22fc7cd0b6d9
Revises: 4ec509332a7a
Create Date: 2024-07-13 22:29:10.702155

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "22fc7cd0b6d9"
down_revision: Union[str, None] = "4ec509332a7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("equipment", schema=None) as batch_op:
        batch_op.add_column(sa.Column("exo_stat_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("exo_attempt", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.drop_constraint("equipment_exo_line_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(None, "stat", ["exo_stat_id"], ["id"])
        batch_op.drop_column("exo_line_id")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("equipment", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("exo_line_id", sa.INTEGER(), autoincrement=False, nullable=True)
        )
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.create_foreign_key(
            "equipment_exo_line_id_fkey", "line", ["exo_line_id"], ["id"]
        )
        batch_op.drop_column("exo_attempt")
        batch_op.drop_column("exo_stat_id")

    # ### end Alembic commands ###
