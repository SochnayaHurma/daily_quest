"""Create room table

Revision ID: 3ea9daf61eb3
Revises: e460d90b3de2
Create Date: 2024-03-12 15:34:26.515097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ea9daf61eb3'
down_revision: Union[str, None] = 'e460d90b3de2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_room',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('daily_room')
    # ### end Alembic commands ###
