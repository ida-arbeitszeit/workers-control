from __future__ import annotations

from functools import wraps

from workers_control.core import records
from workers_control.core import repositories as interfaces
from workers_control.core.control_thresholds import ControlThresholds
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.email_notifications import EmailSender
from workers_control.core.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from workers_control.core.password_hasher import PasswordHasher
from workers_control.core.services.payout_factor import PayoutFactorConfig
from workers_control.db import get_social_accounting
from workers_control.db.db import Database
from workers_control.db.repositories import DatabaseGatewayImpl
from workers_control.flask.control_thresholds import ControlThresholdsFlask
from workers_control.flask.datetime import (
    FlaskDatetimeFormatter,
    FlaskTimezoneConfiguration,
    RealtimeDatetimeService,
)
from workers_control.flask.email_configuration import FlaskEmailConfiguration
from workers_control.flask.flask_colors import FlaskColors
from workers_control.flask.flask_plotter import FlaskPlotter
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.language_repository import LanguageRepositoryImpl
from workers_control.flask.mail_service import get_mail_service
from workers_control.flask.notifications import FlaskFlashNotifier
from workers_control.flask.password_hasher import provide_password_hasher
from workers_control.flask.payout_factor import PayoutFactorConfigImpl
from workers_control.flask.text_renderer import TextRendererImpl
from workers_control.flask.token import FlaskTokenService
from workers_control.flask.translator import FlaskTranslator
from workers_control.flask.url_index import GeneralUrlIndex
from workers_control.flask.views.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from workers_control.web.colors import HexColors
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.email.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from workers_control.web.email.email_sender import EmailSender as EmailSenderImpl
from workers_control.web.formatters.datetime_formatter import (
    DatetimeFormatter,
    TimezoneConfiguration,
)
from workers_control.web.language_service import LanguageService
from workers_control.web.notification import Notifier
from workers_control.web.plotter import Plotter
from workers_control.web.request import Request
from workers_control.web.session import Session
from workers_control.web.text_renderer import TextRenderer
from workers_control.web.token import TokenService
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


class FlaskModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder.bind(
            records.SocialAccounting,
            to=CallableProvider(get_social_accounting),
        )
        binder.bind(
            DatetimeService,
            to=AliasProvider(RealtimeDatetimeService),
        )
        binder.bind(
            Database,
            to=CallableProvider(self.provide_database, is_singleton=True),
        )
        binder[TextRenderer] = AliasProvider(TextRendererImpl)
        binder[Request] = AliasProvider(FlaskRequest)
        binder[UrlIndex] = AliasProvider(GeneralUrlIndex)
        binder[interfaces.LanguageRepository] = AliasProvider(LanguageRepositoryImpl)
        binder[LanguageService] = AliasProvider(LanguageRepositoryImpl)
        binder[EmailConfiguration] = AliasProvider(FlaskEmailConfiguration)
        binder.bind(
            interfaces.DatabaseGateway,
            to=AliasProvider(DatabaseGatewayImpl),
        )
        binder[Session] = AliasProvider(FlaskSession)
        binder[Notifier] = AliasProvider(FlaskFlashNotifier)
        binder[MailService] = CallableProvider(get_mail_service)
        binder[Translator] = AliasProvider(FlaskTranslator)
        binder[Plotter] = AliasProvider(FlaskPlotter)
        binder[HexColors] = AliasProvider(FlaskColors)
        binder[ControlThresholds] = AliasProvider(ControlThresholdsFlask)
        binder[DatetimeFormatter] = AliasProvider(FlaskDatetimeFormatter)
        binder[TimezoneConfiguration] = AliasProvider(FlaskTimezoneConfiguration)
        binder[PayoutFactorConfig] = AliasProvider(PayoutFactorConfigImpl)
        binder.bind(
            AccountantInvitationEmailView,
            to=AliasProvider(AccountantInvitationEmailViewImpl),
        )
        binder.bind(
            PasswordHasher,
            to=CallableProvider(provide_password_hasher),
        )
        binder.bind(
            TokenService,
            to=AliasProvider(FlaskTokenService),
        )
        binder.bind(
            EmailSender,
            to=AliasProvider(EmailSenderImpl),
        )

    @staticmethod
    def provide_database() -> Database:
        #  db gets configured in create_app
        return Database()


class with_injection:
    def __init__(self) -> None:
        self._injector = create_dependency_injector()

    def __call__(self, original_function):
        """When you wrap a function, make sure that the parameters to be
        injected come after the the parameters that the caller should
        provide.
        """

        @wraps(original_function)
        def wrapped_function(*args, **kwargs):
            return self._injector.call_with_injection(
                original_function, args=args, kwargs=kwargs
            )

        return wrapped_function


def create_dependency_injector() -> Injector:
    return Injector([FlaskModule()])
