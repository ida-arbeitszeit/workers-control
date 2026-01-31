"""Create table EmailOutbox

Revision ID: 68ac7ccf6086
Revises: a3e7b2c1d4f5
Create Date: 2026-01-31 07:42:03.847387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68ac7ccf6086'
down_revision: Union[str, None] = 'a3e7b2c1d4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('email_outbox',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('recipient', sa.String(length=1000), nullable=False),
    sa.Column('sender', sa.String(length=1000), nullable=False),
    sa.Column('subject', sa.String(length=1000), nullable=False),
    sa.Column('html', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('email_outbox')
