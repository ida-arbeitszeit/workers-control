"""add taxes to basic service consumptions

Revision ID: c5e8a9d0f1b2
Revises: 7a4d0412c2a7
Create Date: 2026-05-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c5e8a9d0f1b2"
down_revision: Union[str, None] = "7a4d0412c2a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = (
    "private_consumption_of_basic_service",
    "productive_consumption_of_basic_service",
)


def upgrade() -> None:
    for table_name in TABLES:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column("transfer", new_column_name="transfer_of_consumption")
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.add_column(
                sa.Column("transfer_of_taxes", sa.Uuid(), nullable=False)
            )
            batch_op.create_foreign_key(
                f"{table_name}_transfer_of_taxes_fkey",
                "transfer",
                ["transfer_of_taxes"],
                ["id"],
            )


def downgrade() -> None:
    for table_name in TABLES:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column("transfer_of_taxes")
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column(
                "transfer_of_consumption", new_column_name="transfer"
            )
