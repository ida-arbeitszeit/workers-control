"""add productive consumption of basic service table

Revision ID: 7a4d0412c2a7
Revises: 399a221ebea4
Create Date: 2026-04-28 19:52:52.142040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a4d0412c2a7'
down_revision: Union[str, None] = '399a221ebea4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "productive_consumption_of_basic_service",
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
    op.drop_table("productive_consumption_of_basic_service")
