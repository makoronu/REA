"""add_contractor_company_columns

Revision ID: 2d259ad1652c
Revises: c4e23b46d77e
Create Date: 2025-07-18 16:45:34.722997

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2d259ad1652c"
down_revision: Union[str, None] = "c4e23b46d77e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
