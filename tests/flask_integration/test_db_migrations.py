from collections.abc import Iterator
from contextlib import contextmanager
from unittest import TestCase

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, MetaData, inspect, text

from tests.db.dependency_injection import DatabaseTestModule
from tests.markers import database_required
from workers_control.core.injector import Injector
from workers_control.db.db import Base, Database
from workers_control.flask import create_app

from .dependency_injection import FlaskTestConfiguration

UPGRADABLE_VERSION = "480a749375de"


@database_required
class MigrationsTests(TestCase):
    """
    Migration tests need to perform actual DDL operations (CREATE TABLE, etc.)
    so they cannot use the transaction rollback pattern of DatabaseTestCase.
    Instead, they start from an empty database and clean up after each test.
    All they need is a configured database to run their DDL against.
    """

    def setUp(self) -> None:
        super().setUp()
        self.db = Injector([DatabaseTestModule()]).get(Database)
        self.flask_config = FlaskTestConfiguration.default()
        self.alembic_config = Config(self.flask_config["ALEMBIC_CONFIG"])
        with self.db.engine.begin() as conn:
            self._drop_all_tables(conn)

    def tearDown(self) -> None:
        with self.db.engine.begin() as conn:
            self._drop_all_tables(conn)
            # Leave the database with the schema that DatabaseTestCase
            # expects.  Without this, tests running after the migration tests
            # would find no tables at all, since the database is only reset
            # once per test run.
            Base.metadata.create_all(bind=conn)
        super().tearDown()

    def test_that_tables_are_created_on_fresh_database_with_auto_migration(
        self,
    ) -> None:
        assert not self.table_exists("alembic_version")
        assert not self.table_exists("plan")
        self.start_app(auto_migrate=True)
        assert self.table_exists("alembic_version")
        assert self.table_exists("plan")

    def test_that_tables_are_created_on_fresh_database_without_auto_migration(
        self,
    ) -> None:
        assert not self.table_exists("alembic_version")
        assert not self.table_exists("plan")
        self.start_app(auto_migrate=False)
        assert self.table_exists("alembic_version")
        assert self.table_exists("plan")

    def test_that_migration_version_is_recorded_on_fresh_database(self) -> None:
        self.start_app(auto_migrate=False)
        assert self.current_migration_version()

    def test_that_outdated_database_is_upgraded_to_head_with_auto_migration(
        self,
    ) -> None:
        self.bring_database_to_upgradable_version()
        assert not self.is_db_at_head()
        self.start_app(auto_migrate=True)
        assert self.is_db_at_head()

    def test_that_outdated_database_stays_outdated_without_auto_migration(self) -> None:
        self.bring_database_to_upgradable_version()
        self.start_app(auto_migrate=False)
        assert not self.is_db_at_head()

    def test_that_downgrade_to_base_is_possible_after_an_upgrade_to_head(self) -> None:
        with self.alembic_connection() as config:
            command.upgrade(config, "head")
            command.downgrade(config, "base")

    def test_that_after_downgrade_to_base_upgrading_to_head_is_possible(self) -> None:
        with self.alembic_connection() as config:
            command.upgrade(config, "head")
            command.downgrade(config, "base")
            command.upgrade(config, "head")

    def start_app(self, *, auto_migrate: bool) -> None:
        self.flask_config["AUTO_MIGRATE"] = auto_migrate
        create_app(self.flask_config)

    def bring_database_to_upgradable_version(self) -> None:
        with self.alembic_connection() as config:
            command.upgrade(config, "head")
            command.downgrade(config, UPGRADABLE_VERSION)
        assert self.current_migration_version() == UPGRADABLE_VERSION

    @contextmanager
    def alembic_connection(self) -> Iterator[Config]:
        """Yield the alembic config bound to a connection, so that a sequence
        of alembic commands runs in a single transaction.
        """
        with self.db.engine.begin() as connection:
            self.alembic_config.attributes["connection"] = connection
            yield self.alembic_config

    def current_migration_version(self) -> str | None:
        with self.db.engine.connect() as conn:
            row = conn.execute(text("select version_num from alembic_version;")).first()
        return row[0] if row else None

    def is_db_at_head(self) -> bool:
        head_revisions = ScriptDirectory.from_config(self.alembic_config).get_heads()
        return self.current_migration_version() in head_revisions

    def table_exists(self, table_name: str) -> bool:
        return table_name in inspect(self.db.engine).get_table_names()

    @staticmethod
    def _drop_all_tables(conn: Connection) -> None:
        metadata = MetaData()
        metadata.reflect(bind=conn)
        metadata.drop_all(bind=conn)
