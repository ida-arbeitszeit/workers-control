"""Rename collaboration definition to description

Revision ID: ea8f299002c8
Revises: d8c3f5a90e21
Create Date: 2026-11-10 23:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ea8f299002c8"
down_revision: Union[str, None] = "d8c3f5a90e21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE "collaboration" RENAME COLUMN "definition" TO "description"')


def downgrade() -> None:
    op.execute('ALTER TABLE "collaboration" RENAME COLUMN "description" TO "definition"')
