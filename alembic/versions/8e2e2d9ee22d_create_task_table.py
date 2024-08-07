"""Create task table

Revision ID: 8e2e2d9ee22d
Revises: 3ea9daf61eb3
Create Date: 2024-03-12 15:35:52.676043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e2e2d9ee22d'
down_revision: Union[str, None] = '3ea9daf61eb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_task',
    sa.Column('job', sa.Integer(), nullable=True),
    sa.Column('done', sa.Boolean(), server_default=sa.text('False'), nullable=False),
    sa.Column('room', sa.Integer(), nullable=False),
    sa.Column('user_committed_id', sa.Integer(), nullable=True),
    sa.Column('last_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['job'], ['daily_job.id'], ),
    sa.ForeignKeyConstraint(['room'], ['daily_room.id'], ),
    sa.ForeignKeyConstraint(['user_committed_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('daily_task')
    # ### end Alembic commands ###
