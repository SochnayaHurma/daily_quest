"""Add unique contraint on contract_job and contract_room tables

Revision ID: 9d3be7d639b2
Revises: 140aadae5789
Create Date: 2024-04-19 16:39:30.190710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d3be7d639b2'
down_revision: Union[str, None] = '140aadae5789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'daily_contract_jobs', ['job_id', 'contract_id'])
    op.create_unique_constraint(None, 'daily_contract_rooms', ['room_id', 'contract_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'daily_contract_rooms', type_='unique')
    op.drop_constraint(None, 'daily_contract_jobs', type_='unique')
    # ### end Alembic commands ###
