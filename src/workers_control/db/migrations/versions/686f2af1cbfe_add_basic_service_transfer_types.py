"""add basic service transfer types

Revision ID: 686f2af1cbfe
Revises: b40539bf0293
Create Date: 2026-04-24 20:17:38.952108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '686f2af1cbfe'
down_revision: Union[str, None] = 'b40539bf0293'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dialect = op.get_bind().dialect.name

    if dialect == "postgresql":
        op.execute("ALTER TYPE transfertype ADD VALUE IF NOT EXISTS 'private_consumption_of_basic_service'")
        op.execute("ALTER TYPE transfertype ADD VALUE IF NOT EXISTS 'productive_consumption_of_basic_service'")


def downgrade() -> None:
    pass
