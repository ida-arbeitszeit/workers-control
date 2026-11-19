"""Remove plan.hidden_by_user

Revision ID: b7d4e9a2c613
Revises: ea8f299002c8
Create Date: 2026-11-19 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7d4e9a2c613"
down_revision: Union[str, None] = "ea8f299002c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("plan") as batch_op:
        batch_op.drop_column("hidden_by_user")


def downgrade() -> None:
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(
            sa.Column(
                "hidden_by_user",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
