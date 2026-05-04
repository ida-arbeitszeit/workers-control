"""add deactivated_on to basic_service

Revision ID: 17911726c134
Revises: c5e8a9d0f1b2
Create Date: 2026-05-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "17911726c134"
down_revision: Union[str, None] = "c5e8a9d0f1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("basic_service") as batch_op:
        batch_op.add_column(
            sa.Column("deactivated_on", sa.DateTime(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("basic_service") as batch_op:
        batch_op.drop_column("deactivated_on")
