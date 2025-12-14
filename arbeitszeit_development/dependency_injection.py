import os

from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from arbeitszeit.records import SocialAccounting
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit_db import get_social_accounting
from arbeitszeit_db.db import Database
from arbeitszeit_db.repositories import DatabaseGatewayImpl
from tests.dependency_injection import TestingModule


def provide_dev_database() -> Database:
    Database().configure(uri=os.environ["ARBEITSZEITAPP_DEV_DB"])
    return Database()


class DatabaseDevModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Database] = CallableProvider(provide_dev_database, is_singleton=True)
        binder[DatabaseGateway] = AliasProvider(DatabaseGatewayImpl)
        binder[SocialAccounting] = CallableProvider(get_social_accounting)


def create_dependency_injector() -> Injector:
    return Injector(
        [
            DatabaseDevModule(),
            TestingModule(),
        ]
    )
