"""Add status columns to email_outbox

Revision ID: c9f2e1a4b8d7
Revises: 68ac7ccf6086
Create Date: 2026-05-09 16:55:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9f2e1a4b8d7'
down_revision: Union[str, Sequence[str], None] = '68ac7ccf6086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'email_outbox',
        sa.Column('sent_at', sa.DateTime(), nullable=True),
    )
    op.add_column(
        'email_outbox',
        sa.Column(
            'retry_count',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
    )
    op.add_column(
        'email_outbox',
        sa.Column('last_error', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('email_outbox', 'last_error')
    op.drop_column('email_outbox', 'retry_count')
    op.drop_column('email_outbox', 'sent_at')
