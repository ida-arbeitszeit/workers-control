from typing import Any, Callable, TypeVar, cast

import tests.email_notifications
import workers_control.core.repositories as interfaces
from tests.dependency_injection import TestingModule
from tests.interactors import repositories
from tests.token import FakeTokenService
from workers_control.core import records
from workers_control.core.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from workers_control.web.token import TokenService


class InMemoryModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[interfaces.LanguageRepository] = AliasProvider(
            repositories.FakeLanguageRepository
        )
        binder[records.SocialAccounting] = CallableProvider(
            self.provide_social_accounting_instance
        )
        binder.bind(
            interfaces.DatabaseGateway,
            to=AliasProvider(repositories.MockDatabase),
        )
        binder.bind(
            TokenService,
            to=AliasProvider(FakeTokenService),
        )
        binder[tests.email_notifications.EmailSenderTestImpl] = CallableProvider(
            self.provide_email_sender, is_singleton=True
        )

    @staticmethod
    def provide_social_accounting_instance(
        mock_database: repositories.MockDatabase,
    ) -> records.SocialAccounting:
        return mock_database.social_accounting

    @staticmethod
    def provide_email_sender() -> tests.email_notifications.EmailSenderTestImpl:
        return tests.email_notifications.EmailSenderTestImpl()


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])


CallableT = TypeVar("CallableT", bound=Callable)


def injection_test(original_test: CallableT) -> CallableT:
    injector = get_dependency_injector()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return injector.call_with_injection(original_test, args=args, kwargs=kwargs)

    return cast(CallableT, wrapper)
