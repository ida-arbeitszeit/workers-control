import workers_control.core.repositories as interfaces
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.email_notifications import EmailSenderTestImpl
from tests.interactors import repositories
from tests.password_hasher import PasswordHasherImpl
from tests.payout_factor import PayoutFactorConfigTestImpl
from tests.token import FakeTokenService
from workers_control.core import records
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
from workers_control.core.services.payout_factor import PayoutFactorConfig
from workers_control.web.token import TokenService


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[EmailSender] = AliasProvider(EmailSenderTestImpl)
        binder[EmailSenderTestImpl] = CallableProvider(
            self.provide_email_sender, is_singleton=True
        )
        binder[ControlThresholds] = AliasProvider(ControlThresholdsTestImpl)
        binder[DatetimeService] = AliasProvider(FakeDatetimeService)
        binder[PasswordHasher] = AliasProvider(PasswordHasherImpl)
        binder[PayoutFactorConfig] = AliasProvider(PayoutFactorConfigTestImpl)
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

    @staticmethod
    def provide_social_accounting_instance(
        mock_database: repositories.MockDatabase,
    ) -> records.SocialAccounting:
        return mock_database.social_accounting

    @staticmethod
    def provide_email_sender() -> EmailSenderTestImpl:
        return EmailSenderTestImpl()
