"""empty message

Revision ID: ec6dec1f7ebf
Revises: a4b0c391a9f3
Create Date: 2024-07-13 14:27:51.576686

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec6dec1f7ebf"
down_revision: Union[str, None] = "a4b0c391a9f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("equipment", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("count_attempt", sa.Integer(), nullable=False, server_default="0")
        )

    with op.batch_alter_table("line", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "spent_quantity", sa.Integer(), nullable=False, server_default="0"
            )
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("line", schema=None) as batch_op:
        batch_op.drop_column("spent_quantity")

    with op.batch_alter_table("equipment", schema=None) as batch_op:
        batch_op.drop_column("count_attempt")

    # ### end Alembic commands ###
