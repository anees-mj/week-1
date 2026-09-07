"""Initial schema setup with async models and indexes

Revision ID: 4749145dd857
Revises: cfd64ca2394b
Create Date: 2026-09-07 11:47:25.876582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4749145dd857'
down_revision: Union[str, Sequence[str], None] = 'cfd64ca2394b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
