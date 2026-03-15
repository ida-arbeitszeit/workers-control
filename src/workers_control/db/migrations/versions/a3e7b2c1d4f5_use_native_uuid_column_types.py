"""Use native UUID column types

Revision ID: a3e7b2c1d4f5
Revises: 4fd90069eb82
Create Date: 2026-03-13 22:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3e7b2c1d4f5"
down_revision: Union[str, None] = "4fd90069eb82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All tables and their UUID columns that need to be migrated
UUID_COLUMNS: dict[str, list[str]] = {
    "account": ["id"],
    "user": ["id"],
    "social_accounting": ["id", "account_psf"],
    "member": ["id", "user_id", "account"],
    "company": [
        "id",
        "user_id",
        "p_account",
        "r_account",
        "a_account",
        "prd_account",
    ],
    "accountant": ["id", "user_id"],
    "plan_draft": ["id", "planner"],
    "plan": ["id", "planner", "requested_cooperation"],
    "plan_cooperation": ["plan", "cooperation"],
    "plan_review": ["id", "plan_id"],
    "plan_approval": [
        "id",
        "plan_id",
        "transfer_of_credit_p",
        "transfer_of_credit_r",
        "transfer_of_credit_a",
    ],
    "transfer": ["id", "debit_account", "credit_account"],
    "private_consumption": [
        "id",
        "plan_id",
        "transfer_of_private_consumption",
        "transfer_of_compensation",
    ],
    "productive_consumption": [
        "id",
        "plan_id",
        "transfer_of_productive_consumption",
        "transfer_of_compensation",
    ],
    "registered_hours_worked": [
        "id",
        "company",
        "worker",
        "transfer_of_work_certificates",
        "transfer_of_taxes",
    ],
    "company_work_invite": ["id", "company", "member"],
    "cooperation": ["id", "account"],
    "coordination_tenure": ["id", "company", "cooperation"],
    "coordination_transfer_request": [
        "id",
        "requesting_coordination_tenure",
        "candidate",
    ],
    "password_reset_request": ["id"],
    "jobs": ["member_id", "company_id"],
}


def upgrade() -> None:
    dialect = op.get_bind().dialect.name

    if dialect == "sqlite":
        _upgrade_sqlite()
    elif dialect == "postgresql":
        _upgrade_postgresql()
    else:
        raise NotImplementedError(f"UUID migration not implemented for dialect {dialect}")


def downgrade() -> None:
    dialect = op.get_bind().dialect.name

    if dialect == "sqlite":
        _downgrade_sqlite()
    elif dialect == "postgresql":
        _downgrade_postgresql()
    else:
        raise NotImplementedError(
            f"UUID migration downgrade not implemented for dialect {dialect}"
        )


def _upgrade_sqlite() -> None:
    """On SQLite, the Uuid type stores as CHAR(32) (hex without hyphens).

    Convert existing hyphenated UUID strings to the compact format.
    """
    conn = op.get_bind()
    conn.execute(sa.text("PRAGMA foreign_keys=OFF"))
    try:
        for table_name, columns in UUID_COLUMNS.items():
            for col in columns:
                conn.execute(
                    sa.text(
                        f'UPDATE "{table_name}" '
                        f'SET "{col}" = REPLACE("{col}", \'-\', \'\') '
                        f'WHERE "{col}" IS NOT NULL AND "{col}" LIKE \'%-%\''
                    )
                )
    finally:
        conn.execute(sa.text("PRAGMA foreign_keys=ON"))


def _upgrade_postgresql() -> None:
    """On PostgreSQL, change VARCHAR columns to native UUID type.

    FK constraints must be dropped first because PostgreSQL checks type
    compatibility immediately when a column type is altered.  After all
    columns are converted we recreate the constraints from their saved
    definitions (which include ON DELETE clauses etc.).
    """
    conn = op.get_bind()
    saved_fks = _get_fk_constraints(conn)

    for conname, table, _definition in saved_fks:
        conn.execute(
            sa.text(f'ALTER TABLE "{table}" DROP CONSTRAINT "{conname}"')
        )

    for table_name, columns in UUID_COLUMNS.items():
        for col in columns:
            conn.execute(
                sa.text(
                    f'ALTER TABLE "{table_name}" '
                    f'ALTER COLUMN "{col}" TYPE UUID USING "{col}"::uuid'
                )
            )

    for conname, table, definition in saved_fks:
        conn.execute(
            sa.text(f'ALTER TABLE "{table}" ADD CONSTRAINT "{conname}" {definition}')
        )


def _downgrade_sqlite() -> None:
    """On SQLite, convert compact UUIDs back to hyphenated format."""
    conn = op.get_bind()
    conn.execute(sa.text("PRAGMA foreign_keys=OFF"))
    try:
        for table_name, columns in UUID_COLUMNS.items():
            for col in columns:
                conn.execute(
                    sa.text(
                        f'UPDATE "{table_name}" SET "{col}" = '
                        f"SUBSTR(\"{col}\", 1, 8) || '-' || "
                        f"SUBSTR(\"{col}\", 9, 4) || '-' || "
                        f"SUBSTR(\"{col}\", 13, 4) || '-' || "
                        f"SUBSTR(\"{col}\", 17, 4) || '-' || "
                        f"SUBSTR(\"{col}\", 21) "
                        f'WHERE "{col}" IS NOT NULL AND "{col}" NOT LIKE \'%-%\''
                    )
                )
    finally:
        conn.execute(sa.text("PRAGMA foreign_keys=ON"))


def _downgrade_postgresql() -> None:
    """On PostgreSQL, change UUID columns back to VARCHAR.

    Same FK drop/recreate strategy as the upgrade – see
    ``_upgrade_postgresql`` for rationale.
    """
    conn = op.get_bind()
    saved_fks = _get_fk_constraints(conn)

    for conname, table, _definition in saved_fks:
        conn.execute(
            sa.text(f'ALTER TABLE "{table}" DROP CONSTRAINT "{conname}"')
        )

    for table_name, columns in UUID_COLUMNS.items():
        for col in columns:
            conn.execute(
                sa.text(
                    f'ALTER TABLE "{table_name}" '
                    f'ALTER COLUMN "{col}" TYPE VARCHAR USING "{col}"::text'
                )
            )

    for conname, table, definition in saved_fks:
        conn.execute(
            sa.text(f'ALTER TABLE "{table}" ADD CONSTRAINT "{conname}" {definition}')
        )


def _get_fk_constraints(
    conn: sa.engine.Connection,
) -> list[tuple[str, str, str]]:
    """Return all FK constraints in the public schema.

    Each element is ``(constraint_name, table_name, definition)`` where
    *definition* is the output of ``pg_get_constraintdef`` (e.g.
    ``FOREIGN KEY (col) REFERENCES other(id) ON DELETE CASCADE``).
    """
    rows = conn.execute(
        sa.text(
            """
            SELECT con.conname,
                   cls.relname,
                   pg_get_constraintdef(con.oid)
              FROM pg_constraint con
              JOIN pg_class cls ON con.conrelid = cls.oid
              JOIN pg_namespace ns  ON cls.relnamespace = ns.oid
             WHERE con.contype = 'f'
               AND ns.nspname = 'public'
            """
        )
    ).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]
