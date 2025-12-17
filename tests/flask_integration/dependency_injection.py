from flask import Flask

from arbeitszeit.injector import Binder, CallableProvider, Module
from arbeitszeit_flask import create_app
from tests.db.dependency_injection import provide_test_database_uri
from tests.flask_integration.mail_service import MockEmailService


class FlaskTestConfiguration(dict):
    def __init__(self, *args, **kwargs):
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
                "SECURITY_PASSWORD_SALT": "dev password salt",
                "TESTING": True,
                "MAIL_DEFAULT_SENDER": "test_sender@cp.org",
                "MAIL_ADMIN": "test_admin@cp.org",
                "MAIL_PLUGIN_MODULE": MockEmailService.__module__,
                "MAIL_PLUGIN_CLASS": MockEmailService.__name__,
                "MAIL_USE_TLS": False,
                "MAIL_USE_SSL": False,
                "MAIL_SERVER": "localhost",
                "MAIL_PORT": 0,
                "MAIL_USERNAME": "",
                "MAIL_PASSWORD": "",
                "LANGUAGES": {"en": "English", "de": "Deutsch", "es": "Español"},
                "ARBEITSZEIT_PASSWORD_HASHER": "tests.password_hasher:PasswordHasherImpl",
                "AUTO_MIGRATE": False,
                "DEFAULT_USER_TIMEZONE": "UTC",
                "ALEMBIC_CONFIG": "tests/flask_integration/alembic.ini",
                "ALLOWED_OVERDRAW_MEMBER": "unlimited",
                "ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION": 33,
                "FORCE_HTTPS": True,
                # swagger placeholders are necessary until fix of bug in flask-restx:
                # https://github.com/python-restx/flask-restx/issues/565
                "SWAGGER_UI_OAUTH_CLIENT_ID": "placeholder",
                "SWAGGER_VALIDATOR_URL": "placeholder",
                "SWAGGER_UI_OAUTH_REALM": "placeholder",
                "SWAGGER_UI_OAUTH_APP_NAME": "placeholder",
            }
        )

    def _get_template_folder(self) -> str | None:
        return self.get("template_folder")

    def _set_template_folder(self, template_folder: str | None) -> None:
        self["template_folder"] = template_folder

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key.isupper():
            setattr(self, key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        if key.isupper():
            delattr(self, key)

    # Allows you to control where flask loads templates from.
    template_folder = property(_get_template_folder, _set_template_folder)


def provide_app(config: FlaskTestConfiguration) -> Flask:
    return create_app(dev_or_test_config=config, template_folder=config.template_folder)


class FlaskTestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Flask] = CallableProvider(provide_app, is_singleton=True)
        binder[FlaskTestConfiguration] = CallableProvider(
            FlaskTestConfiguration.default
        )
