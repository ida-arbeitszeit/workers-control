"""Rename cooperation to collaboration

Revision ID: d8c3f5a90e21
Revises: f4a9c2e1b6d3
Create Date: 2026-08-24 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d8c3f5a90e21"
down_revision: Union[str, None] = "f4a9c2e1b6d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (table, old column name, new column name)
RENAMED_COLUMNS = [
    ("plan", "requested_cooperation", "requested_collaboration"),
    ("plan_collaboration", "cooperation", "collaboration"),
    ("coordination_tenure", "cooperation", "collaboration"),
]


def upgrade() -> None:
    op.rename_table("cooperation", "collaboration")
    op.rename_table("plan_cooperation", "plan_collaboration")
    for table, old, new in RENAMED_COLUMNS:
        _rename_column(table, old, new)
    _rename_transfer_type("compensation_for_coop", "compensation_for_collab")


def downgrade() -> None:
    _rename_transfer_type("compensation_for_collab", "compensation_for_coop")
    for table, old, new in RENAMED_COLUMNS:
        _rename_column(table, new, old)
    op.rename_table("plan_collaboration", "plan_cooperation")
    op.rename_table("collaboration", "cooperation")


def _rename_column(table: str, old: str, new: str) -> None:
    op.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{old}" TO "{new}"')


def _rename_transfer_type(old: str, new: str) -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(f"ALTER TYPE transfertype RENAME VALUE '{old}' TO '{new}'")
    else:
        op.execute(f"UPDATE transfer SET type = '{new}' WHERE type = '{old}'")
