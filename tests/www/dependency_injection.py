from tests.dependency_injection import TestingModule
from tests.email import FakeEmailConfiguration, FakeEmailService
from tests.email_presenters.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from tests.interactors.dependency_injection import InMemoryModule
from tests.language_service import FakeLanguageService
from tests.request import FakeRequest
from tests.session import FakeSession
from tests.www.datetime_formatter import (
    FakeDatetimeFormatter,
    FakeTimezoneConfiguration,
)
from workers_control.core.injector import AliasProvider, Binder, Injector, Module
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.email.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from workers_control.web.formatters.datetime_formatter import (
    DatetimeFormatter,
    TimezoneConfiguration,
)
from workers_control.web.language_service import LanguageService
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.session import Session
from workers_control.web.url_index import UrlIndex

from .presenters.notifier import NotifierTestImpl
from .presenters.url_index import UrlIndexTestImpl


class WwwTestsInjector(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[AccountantInvitationEmailView] = AliasProvider(
            AccountantInvitationEmailViewImpl
        )
        binder[EmailConfiguration] = AliasProvider(FakeEmailConfiguration)
        binder[Notifier] = AliasProvider(NotifierTestImpl)
        binder[UrlIndex] = AliasProvider(UrlIndexTestImpl)
        binder[Session] = AliasProvider(FakeSession)
        binder[Request] = AliasProvider(FakeRequest)
        binder[LanguageService] = AliasProvider(FakeLanguageService)
        binder[MailService] = AliasProvider(FakeEmailService)
        binder[DatetimeFormatter] = AliasProvider(FakeDatetimeFormatter)
        binder[TimezoneConfiguration] = AliasProvider(FakeTimezoneConfiguration)


def get_dependency_injector() -> Injector:
    return Injector(modules=[TestingModule(), InMemoryModule(), WwwTestsInjector()])
