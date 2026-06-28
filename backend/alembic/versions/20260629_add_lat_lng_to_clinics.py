"""add lat lng to clinics

Revision ID: a1b2c3d4e5f6
Revises: 4f02281c903f
Create Date: 2026-06-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '4f02281c903f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clinics', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('clinics', sa.Column('lng', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('clinics', 'lng')
    op.drop_column('clinics', 'lat')
