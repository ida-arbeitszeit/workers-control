from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.email_notifications import EmailSenderTestImpl
from tests.interactors import repositories
from tests.mail_service import MockEmailService
from tests.password_hasher import PasswordHasherImpl
from tests.payout_factor import PayoutFactorConfigTestImpl
from tests.token import FakeTokenService
from tests.web.email_configuration import FakeEmailConfiguration
from tests.web.email_presenters.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from tests.web.email_presenters.text_renderer import TextRendererTestImpl
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
from workers_control.core.control_thresholds import ControlThresholds
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.email_notifications import EmailSender
from workers_control.core.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Module,
)
from workers_control.core.password_hasher import PasswordHasher
from workers_control.core.records import SocialAccounting
from workers_control.core.repositories import DatabaseGateway, LanguageRepository
from workers_control.core.services.payout_factor import PayoutFactorConfig
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
from workers_control.web.token import TokenService
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[AccountantInvitationEmailView] = AliasProvider(
            AccountantInvitationEmailViewImpl
        )
        binder[EmailConfiguration] = AliasProvider(FakeEmailConfiguration)
        binder[EmailSender] = AliasProvider(EmailSenderTestImpl)
        binder[EmailSenderTestImpl] = CallableProvider(
            self.provide_email_sender, is_singleton=True
        )
        binder[ControlThresholds] = AliasProvider(ControlThresholdsTestImpl)
        binder[DatetimeFormatter] = AliasProvider(FakeDatetimeFormatter)
        binder[DatabaseGateway] = AliasProvider(repositories.MockDatabase)
        binder[DatetimeService] = AliasProvider(FakeDatetimeService)
        binder[PasswordHasher] = AliasProvider(PasswordHasherImpl)
        binder[PayoutFactorConfig] = AliasProvider(PayoutFactorConfigTestImpl)
        binder[LanguageRepository] = AliasProvider(repositories.FakeLanguageRepository)
        binder[LanguageService] = AliasProvider(FakeLanguageService)
        binder[MailService] = AliasProvider(MockEmailService)
        binder[Notifier] = AliasProvider(NotifierTestImpl)
        binder[Request] = AliasProvider(FakeRequest)
        binder[FakeRequest] = CallableProvider(
            self.provide_fake_request, is_singleton=True
        )
        binder[Session] = AliasProvider(FakeSession)
        binder[SocialAccounting] = CallableProvider(
            self.provide_social_accounting_instance
        )
        binder[TextRenderer] = AliasProvider(TextRendererTestImpl)
        binder[TimezoneConfiguration] = AliasProvider(FakeTimezoneConfiguration)
        binder[TokenService] = AliasProvider(FakeTokenService)
        binder[Translator] = AliasProvider(FakeTranslator)
        binder[HexColors] = AliasProvider(ColorsTestImpl)
        binder[UrlIndex] = AliasProvider(UrlIndexTestImpl)

    @staticmethod
    def provide_social_accounting_instance(
        mock_database: repositories.MockDatabase,
    ) -> SocialAccounting:
        return mock_database.social_accounting

    @staticmethod
    def provide_email_sender() -> EmailSenderTestImpl:
        return EmailSenderTestImpl()

    @classmethod
    def provide_fake_request(self) -> FakeRequest:
        return FakeRequest()
