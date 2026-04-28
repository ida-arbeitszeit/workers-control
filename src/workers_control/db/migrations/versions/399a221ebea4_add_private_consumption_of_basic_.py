"""add private consumption of basic service table

Revision ID: 399a221ebea4
Revises: 686f2af1cbfe
Create Date: 2026-04-27 21:06:39.948825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '399a221ebea4'
down_revision: Union[str, None] = '686f2af1cbfe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "private_consumption_of_basic_service",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("basic_service", sa.Uuid(), nullable=False),
        sa.Column("transfer", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["basic_service"],
            ["basic_service.id"],
        ),
        sa.ForeignKeyConstraint(
            ["transfer"],
            ["transfer.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("private_consumption_of_basic_service")
