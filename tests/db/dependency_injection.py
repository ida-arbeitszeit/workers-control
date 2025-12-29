import os

from workers_control.core.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Module,
)
from workers_control.core.records import SocialAccounting
from workers_control.core.repositories import DatabaseGateway
from workers_control.db import get_social_accounting
from workers_control.db.db import Database
from workers_control.db.repositories import DatabaseGatewayImpl


def provide_test_database_uri() -> str:
    return os.environ["WOCO_TEST_DB"]


def provide_database() -> Database:
    Database().configure(uri=provide_test_database_uri())
    return Database()


class DatabaseTestModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Database] = CallableProvider(provide_database, is_singleton=True)
        binder[DatabaseGateway] = AliasProvider(DatabaseGatewayImpl)
        binder[SocialAccounting] = CallableProvider(get_social_accounting)
