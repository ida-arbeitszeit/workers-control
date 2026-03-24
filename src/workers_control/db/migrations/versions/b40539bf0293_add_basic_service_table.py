"""add basic_service table

Revision ID: b40539bf0293
Revises: a3e7b2c1d4f5
Create Date: 2026-03-23 21:06:52.453276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b40539bf0293'
down_revision: Union[str, None] = 'a3e7b2c1d4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "basic_service",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=1000), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=False),
        sa.Column("provider", sa.Uuid(), nullable=False),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["provider"],
            ["member.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("basic_service")
