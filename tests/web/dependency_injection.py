from tests.dependency_injection import TestingModule
from tests.email import FakeEmailConfiguration, FakeEmailService
from tests.interactors.dependency_injection import InMemoryModule
from tests.web.email_presenters.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from tests.web.email_presenters.text_renderer import TextRendererImpl
from tests.web.www.datetime_formatter import (
    FakeDatetimeFormatter,
    FakeTimezoneConfiguration,
)
from tests.web.www.language_service import FakeLanguageService
from tests.web.www.presenters.notifier import NotifierTestImpl
from tests.web.www.presenters.test_colors import ColorsTestImpl
from tests.web.www.presenters.url_index import UrlIndexTestImpl
from tests.web.www.request import FakeRequest
from tests.web.www.session import FakeSession
from tests.web.www.translator import FakeTranslator
from workers_control.core.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from workers_control.web.colors import HexColors
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
from workers_control.web.text_renderer import TextRenderer
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


class WebTestsModule(Module):
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
        binder[FakeRequest] = CallableProvider(
            self.provide_fake_request, is_singleton=True
        )
        binder[LanguageService] = AliasProvider(FakeLanguageService)
        binder[MailService] = AliasProvider(FakeEmailService)
        binder[TextRenderer] = AliasProvider(TextRendererImpl)
        binder[DatetimeFormatter] = AliasProvider(FakeDatetimeFormatter)
        binder[TimezoneConfiguration] = AliasProvider(FakeTimezoneConfiguration)
        binder[HexColors] = AliasProvider(ColorsTestImpl)
        binder[Translator] = AliasProvider(FakeTranslator)

    @classmethod
    def provide_fake_request(self) -> FakeRequest:
        return FakeRequest()


def get_dependency_injector() -> Injector:
    return Injector(modules=[TestingModule(), InMemoryModule(), WebTestsModule()])
