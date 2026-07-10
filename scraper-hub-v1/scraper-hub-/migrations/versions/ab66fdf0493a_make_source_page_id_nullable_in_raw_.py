"""make source_page_id nullable in raw_snapshots

Revision ID: ab66fdf0493a
Revises: 78c16c1186df
Create Date: 2026-04-17 14:25:01.998764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab66fdf0493a'
down_revision: Union[str, None] = '78c16c1186df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
