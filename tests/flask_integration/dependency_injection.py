from typing import Any

from flask import Flask

from tests.db.dependency_injection import provide_test_database_uri
from tests.mail_service import MockEmailService
from workers_control.core.injector import Binder, CallableProvider, Injector, Module
from workers_control.flask import create_app
from workers_control.flask.mail_service import set_email_plugin


class FlaskTestConfiguration(dict):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if key.isupper():
                setattr(self, key, value)

    @classmethod
    def default(cls) -> "FlaskTestConfiguration":
        return cls(
            {
                "SQLALCHEMY_DATABASE_URI": provide_test_database_uri(),
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SECRET_KEY": "dev secret key",
                "WTF_CSRF_ENABLED": False,
                "SERVER_NAME": "test.name",
                "DEBUG": True,
                "SECURITY_PASSWORD_SALT": "test password salt",
                "TESTING": True,
                "MAIL_DEFAULT_SENDER": "test_sender@cp.org",
                "MAIL_ADMIN": "test_admin@cp.org",
                "MAIL_PLUGIN": "tests.mail_service:MockEmailService",
                "MAIL_ENCRYPTION_TYPE": "tls",
                "MAIL_SERVER": "localhost",
                "MAIL_PORT": 0,
                "MAIL_USERNAME": "",
                "MAIL_PASSWORD": "",
                "LANGUAGES": {"en": "English", "de": "Deutsch", "es": "Español"},
                "WOCO_PASSWORD_HASHER": "tests.password_hasher:PasswordHasherImpl",
                "AUTO_MIGRATE": False,
                "DEFAULT_USER_TIMEZONE": "UTC",
                "ALEMBIC_CONFIG": "tests/flask_integration/alembic.ini",
                "ALLOWED_OVERDRAW_MEMBER": "unlimited",
                "ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION": 33,
                "PAYOUT_FACTOR_CALCULATION_WINDOW": 180,
                "FORCE_HTTPS": True,
            }
        )

    def _get_template_folder(self) -> str | None:
        return self.get("template_folder")

    def _set_template_folder(self, template_folder: str | None) -> None:
        self["template_folder"] = template_folder

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(key, value)
        if key.isupper():
            setattr(self, key, value)

    def __delitem__(self, key: str) -> None:
        super().__delitem__(key)
        if key.isupper():
            delattr(self, key)

    # Allows you to control where flask loads templates from.
    template_folder = property(_get_template_folder, _set_template_folder)


class FlaskTestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Flask] = CallableProvider(self.provide_app, is_singleton=True)
        binder[FlaskTestConfiguration] = CallableProvider(
            FlaskTestConfiguration.default
        )

    @staticmethod
    def provide_app(config: FlaskTestConfiguration, injector: Injector) -> Flask:
        # A new Injector is built for every test, so the is_singleton flag
        # above only spans a single test.  Building the app dominates the
        # setup of a flask integration test and nearly all tests use the
        # same configuration, so keep the apps for the whole test run.
        # Sharing them is safe because an app holds no per-test state: the
        # database session is looked up on the Database singleton whenever
        # it is needed.
        app = _get_cached_app(config)
        if app is None:
            # Take the snapshot before create_app, in case it modifies the
            # configuration it is handed.
            configuration_used = dict(config)
            app = create_app(
                dev_or_test_config=config, template_folder=config.template_folder
            )
            _cached_apps.append((configuration_used, app))
        # The mail service is the one exception to the rule above: an app
        # keeps the plugin it was first asked for.  Hand it the mail service
        # of the current test, which is also what self.email_service yields,
        # so that the app of the previous test does not send its emails
        # through a mock that belongs to a test that is already over.
        set_email_plugin(app, injector.get(MockEmailService))
        return app


def _get_cached_app(config: FlaskTestConfiguration) -> Flask | None:
    for cached_config, cached_app in _cached_apps:
        if cached_config == config:
            return cached_app
    return None


_cached_apps: list[tuple[dict[str, Any], Flask]] = []
