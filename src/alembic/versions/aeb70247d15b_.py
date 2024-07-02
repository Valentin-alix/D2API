"""empty message

Revision ID: aeb70247d15b
Revises: ce8b57e537df
Create Date: 2024-07-02 16:56:44.861949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aeb70247d15b'
down_revision: Union[str, None] = 'ce8b57e537df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('range_hour_play_time', schema=None) as batch_op:
        batch_op.drop_constraint('range_hour_play_time_config_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'config_user', ['config_user_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('range_hour_play_time', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('range_hour_play_time_config_user_id_fkey', 'config_user', ['config_user_id'], ['id'])

    # ### end Alembic commands ###
