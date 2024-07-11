"""empty message

Revision ID: f187bd667697
Revises: b11459a36c90
Create Date: 2024-07-08 20:11:56.272415

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f187bd667697"
down_revision: Union[str, None] = "b11459a36c90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("character_job_info", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("weight", sa.Float(), nullable=False, server_default="1")
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("character_job_info", schema=None) as batch_op:
        batch_op.drop_column("weight")

    # ### end Alembic commands ###