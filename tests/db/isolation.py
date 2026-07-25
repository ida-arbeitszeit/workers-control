from functools import cache
from typing import Any

from sqlalchemy import Connection, Engine, create_engine, event

from tests.db.dependency_injection import provide_test_database_uri


@cache
def get_isolation_engine() -> Engine:
    """Provide the engine whose connections DatabaseTestCase wraps in a
    transaction that is rolled back after every test.

    Deliberately not the engine of the Database singleton, see
    _make_transactions_explicit.
    """
    engine = create_engine(provide_test_database_uri())
    if engine.dialect.name == "sqlite":
        _make_transactions_explicit(engine)
    return engine


def _make_transactions_explicit(engine: Engine) -> None:
    """Make connection.begin() open a transaction that can be rolled back.

    The pysqlite driver manages transactions itself and never emits BEGIN.
    Every statement is then committed right away, so the SAVEPOINT a test
    writes into ends up in the database and the rollback in tearDown has
    nothing left to undo.  Sqlalchemy documents this workaround under
    "Serializable isolation / Savepoints / Transactional DDL" of the
    pysqlite dialect.

    Only this engine is treated that way.  The migration tests run long
    blocks of DDL over the engine of the Database singleton and fail with
    "database is locked" if their transactions are held open.
    """

    @event.listens_for(engine, "connect")
    def stop_driver_from_managing_transactions(
        dbapi_connection: Any, connection_record: Any
    ) -> None:
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def begin_transaction(connection: Connection) -> None:
        connection.exec_driver_sql("BEGIN")
