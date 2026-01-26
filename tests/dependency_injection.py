from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.email_notifications import EmailSenderTestImpl
from tests.password_hasher import PasswordHasherImpl
from tests.payout_factor import PayoutFactorConfigTestImpl
from workers_control.core.control_thresholds import ControlThresholds
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.email_notifications import EmailSender
from workers_control.core.injector import (
    AliasProvider,
    Binder,
    Module,
)
from workers_control.core.password_hasher import PasswordHasher
from workers_control.core.services.payout_factor import PayoutFactorConfig


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[EmailSender] = AliasProvider(EmailSenderTestImpl)
        binder[ControlThresholds] = AliasProvider(ControlThresholdsTestImpl)
        binder[DatetimeService] = AliasProvider(FakeDatetimeService)
        binder[PasswordHasher] = AliasProvider(PasswordHasherImpl)
        binder[PayoutFactorConfig] = AliasProvider(PayoutFactorConfigTestImpl)
