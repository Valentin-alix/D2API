"""empty message

Revision ID: a4b0c391a9f3
Revises: e70db6b887cf
Create Date: 2024-07-11 20:07:17.911221

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4b0c391a9f3"
down_revision: Union[str, None] = "e70db6b887cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS spell_id_seq OWNED BY spell.id;
    """)
    op.execute("""
        ALTER TABLE spell
        ALTER COLUMN id SET DEFAULT nextval('spell_id_seq');
    """)
    op.execute("""
        SELECT setval('spell_id_seq', COALESCE(max(id), 1)) FROM spell;
    """)


def downgrade() -> None:
    pass
