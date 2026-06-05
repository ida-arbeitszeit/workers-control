"""Replace plan_review with plan_rejection

Revision ID: f4a9c2e1b6d3
Revises: c9f2e1a4b8d7
Create Date: 2026-05-31 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4a9c2e1b6d3"
down_revision: Union[str, None] = "c9f2e1a4b8d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plan_rejection",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plan.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        "INSERT INTO plan_rejection (id, plan_id, date) "
        "SELECT id, plan_id, rejection_date FROM plan_review "
        "WHERE rejection_date IS NOT NULL"
    )
    op.drop_table("plan_review")


def downgrade() -> None:
    op.create_table(
        "plan_review",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rejection_date", sa.DateTime(), nullable=True),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plan.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        "INSERT INTO plan_review (id, plan_id, rejection_date) "
        "SELECT plan.id, plan.id, plan_rejection.date "
        "FROM plan LEFT JOIN plan_rejection ON plan_rejection.plan_id = plan.id"
    )
    op.drop_table("plan_rejection")
