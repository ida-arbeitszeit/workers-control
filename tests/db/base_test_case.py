from pathlib import Path
from typing import Any
from unittest import TestCase

from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from tests import data_generators
from tests.datetime_service import FakeDatetimeService
from tests.db.dependency_injection import (
    DatabaseTestModule,
    provide_test_database_uri,
)
from tests.db.isolation import get_isolation_engine
from tests.dependency_injection import TestingModule
from tests.lazy_property import _lazy_property
from tests.markers import database_required
from tests.web.www.datetime_formatter import FakeTimezoneConfiguration
from workers_control.core.injector import Injector, Module
from workers_control.db.db import Base, Database
from workers_control.db.repositories import DatabaseGatewayImpl


@database_required
class DatabaseTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._lazy_property_cache: dict[str, Any] = dict()
        self.dependencies: list[Module] = [DatabaseTestModule(), TestingModule()]
        self.injector = Injector(self.dependencies)
        self.db = self.injector.get(Database)
        reset_test_db_once_per_testrun()

        # Run every test inside a transaction that is rolled back in
        # tearDown, see tests.db.isolation.
        self.connection = get_isolation_engine().connect()
        self.transaction = self.connection.begin()

        # expire_on_commit=False prevents objects from expiring after flush.
        # create_savepoint lets code under test call commit() without
        # committing the transaction of the test itself.
        session_factory = sessionmaker(
            bind=self.connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        self.test_session = scoped_session(session_factory)
        self.db._session = self.test_session

    def tearDown(self) -> None:
        self._lazy_property_cache = dict()
        self.test_session.remove()
        self.transaction.rollback()
        self.connection.close()
        super().tearDown()

    accountant_generator = _lazy_property(data_generators.AccountantGenerator)
    basic_service_generator = _lazy_property(data_generators.BasicServiceGenerator)
    company_generator = _lazy_property(data_generators.CompanyGenerator)
    consumption_generator = _lazy_property(data_generators.ConsumptionGenerator)
    cooperation_generator = _lazy_property(data_generators.CooperationGenerator)
    coordination_tenure_generator = _lazy_property(
        data_generators.CoordinationTenureGenerator
    )
    coordination_transfer_request_generator = _lazy_property(
        data_generators.CoordinationTransferRequestGenerator
    )
    database_gateway = _lazy_property(DatabaseGatewayImpl)
    datetime_service = _lazy_property(FakeDatetimeService)
    email_generator = _lazy_property(data_generators.EmailGenerator)
    member_generator = _lazy_property(data_generators.MemberGenerator)
    plan_generator = _lazy_property(data_generators.PlanGenerator)
    registered_hours_worked_generator = _lazy_property(
        data_generators.RegisteredHoursWorkedGenerator
    )
    timezone_configuration = _lazy_property(FakeTimezoneConfiguration)
    transfer_generator = _lazy_property(data_generators.TransferGenerator)
    worker_affiliation_generator = _lazy_property(
        data_generators.WorkerAffiliationGenerator
    )


_is_db_resetted = False


def reset_test_db_once_per_testrun() -> None:
    """Reset the test database at most once per process.

    Resetting is deliberately not repeated because for SQLite it unlinks
    the database file, which would leave the engine of the `Database`
    singleton bound to a deleted file.  Test cases that drop the schema
    are therefore required to restore it themselves instead of relying
    on another reset.
    """
    global _is_db_resetted
    if not _is_db_resetted:
        reset_test_db()
        _is_db_resetted = True


def reset_test_db() -> None:
    engine = create_engine(provide_test_database_uri())
    try:
        dialect = engine.dialect.name
        if dialect == "postgresql":
            with engine.begin() as conn:
                conn.execute(text("DROP SCHEMA public CASCADE"))
                conn.execute(text("CREATE SCHEMA public"))
        elif dialect == "sqlite":
            path_string = engine.url.database
            assert path_string, "Expected a file path for SQLite database"
            path = Path(path_string)
            if path.exists():
                path.unlink()
        Base.metadata.create_all(bind=engine)
    finally:
        engine.dispose()
        _discard_pooled_connections()


def _discard_pooled_connections() -> None:
    """Drop the connections that were pooled before the database was reset.

    For SQLite the reset unlinks the database file, so a pooled connection
    would keep operating on a file that no longer exists.  Disposing a pool
    does not invalidate its engine: the next use simply opens a fresh
    connection.
    """
    database_engine = Database()._engine
    if database_engine is not None:
        database_engine.dispose()
    get_isolation_engine().dispose()
