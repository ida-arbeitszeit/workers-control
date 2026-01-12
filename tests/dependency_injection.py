from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.email_notifications import EmailSenderTestImpl
from tests.password_hasher import PasswordHasherImpl
from tests.payout_factor import PayoutFactorConfigTestImpl
from tests.request import FakeRequest
from tests.text_renderer import TextRendererImpl
from tests.translator import FakeTranslator
from tests.www.presenters.test_colors import ColorsTestImpl
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
from workers_control.web.colors import HexColors
from workers_control.web.request import Request
from workers_control.web.text_renderer import TextRenderer
from workers_control.web.translator import Translator


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[EmailSender] = AliasProvider(EmailSenderTestImpl)
        binder[TextRenderer] = AliasProvider(TextRendererImpl)
        binder[HexColors] = AliasProvider(ColorsTestImpl)
        binder[ControlThresholds] = AliasProvider(ControlThresholdsTestImpl)
        binder[Translator] = AliasProvider(FakeTranslator)
        binder[DatetimeService] = AliasProvider(FakeDatetimeService)
        binder[Request] = AliasProvider(FakeRequest)
        binder[FakeRequest] = CallableProvider(
            self.provide_fake_request, is_singleton=True
        )
        binder[PasswordHasher] = AliasProvider(PasswordHasherImpl)
        binder[PayoutFactorConfig] = AliasProvider(PayoutFactorConfigTestImpl)

    @classmethod
    def provide_fake_request(self) -> FakeRequest:
        return FakeRequest()
