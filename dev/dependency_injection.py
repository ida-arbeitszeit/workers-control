import os

from flask import Flask

from tests.dependency_injection import TestingModule
from workers_control.core.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from workers_control.core.records import SocialAccounting
from workers_control.core.repositories import DatabaseGateway
from workers_control.core.services.payout_factor import PayoutFactorConfig
from workers_control.db import get_social_accounting
from workers_control.db.db import Database
from workers_control.db.repositories import DatabaseGatewayImpl
from workers_control.flask.payout_factor import PayoutFactorConfigImpl

from . import development_server


class DatabaseDevModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Database] = CallableProvider(
            self.provide_dev_database, is_singleton=True
        )
        binder[DatabaseGateway] = AliasProvider(DatabaseGatewayImpl)
        binder[SocialAccounting] = CallableProvider(get_social_accounting)

    @staticmethod
    def provide_dev_database() -> Database:
        Database().configure(uri=os.environ["WOCO_DEV_DB"])
        return Database()


class DevAppModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Flask] = CallableProvider(
            development_server.create_app, is_singleton=True
        )
        binder[PayoutFactorConfig] = AliasProvider(PayoutFactorConfigImpl)


def create_dependency_injector() -> Injector:
    return Injector(
        [
            TestingModule(),
            DatabaseDevModule(),
            DevAppModule(),
        ]
    )
