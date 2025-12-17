import os

from flask import Flask

from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from arbeitszeit.records import SocialAccounting
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit_db import get_social_accounting
from arbeitszeit_db.db import Database
from arbeitszeit_db.repositories import DatabaseGatewayImpl
from arbeitszeit_flask import create_app
from arbeitszeit_flask.mail_service.debug_mail_service import DebugMailService
from tests.dependency_injection import TestingModule


class FlaskDevConfiguration:
    # keys must be uppercase

    FLASK_DEBUG = 1
    TESTING = True

    SERVER_NAME = os.environ.get("ARBEITSZEITAPP_SERVER_NAME", "127.0.0.1:5000")
    FORCE_HTTPS = True
    PREFERRED_URL_SCHEME = "http"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = os.environ.get("MAIL_PORT", "0")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "admin@dev.org")
    MAIL_ADMIN = os.environ.get("MAIL_ADMIN", "admin@dev.org")
    MAIL_PLUGIN_MODULE = DebugMailService.__module__
    MAIL_PLUGIN_CLASS = DebugMailService.__name__
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False

    FLASK_PROFILER = {
        "enabled": True,
        "endpointRoot": "profiling",
    }

    ALLOWED_OVERDRAW_MEMBER = os.environ.get("ALLOWED_OVERDRAW_MEMBER", "unlimited")
    ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION = os.environ.get(
        "ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION", "33"
    )
    LANGUAGES = {"en": "English", "de": "Deutsch", "es": "Español"}
    DEFAULT_USER_TIMEZONE = os.environ.get("DEFAULT_USER_TIMEZONE", "UTC")

    SECURITY_PASSWORD_SALT = os.environ.get(
        "SECURITY_PASSWORD_SALT", "dev password salt"
    )
    SECRET_KEY = os.environ.get("DEV_SECRET_KEY", "dev secret key")
    WTF_CSRF_ENABLED = False
    ARBEITSZEIT_PASSWORD_HASHER = "tests.password_hasher:PasswordHasherImpl"

    SQLALCHEMY_DATABASE_URI = os.environ["ARBEITSZEITAPP_DEV_DB"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALEMBIC_CONFIG = os.getenv("ALEMBIC_CONFIG")
    AUTO_MIGRATE = os.getenv("AUTO_MIGRATE", False)

    RESTX_MASK_SWAGGER = False
    # swagger placeholders are necessary until fix of bug in flask-restx:
    # https://github.com/python-restx/flask-restx/issues/565
    SWAGGER_UI_OAUTH_CLIENT_ID = "placeholder"
    SWAGGER_VALIDATOR_URL = "placeholder"
    SWAGGER_UI_OAUTH_REALM = "placeholder"
    SWAGGER_UI_OAUTH_APP_NAME = "placeholder"


def provide_dev_database() -> Database:
    Database().configure(uri=os.environ["ARBEITSZEITAPP_DEV_DB"])
    return Database()


class DatabaseDevModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Database] = CallableProvider(provide_dev_database, is_singleton=True)
        binder[DatabaseGateway] = AliasProvider(DatabaseGatewayImpl)
        binder[SocialAccounting] = CallableProvider(get_social_accounting)


def provide_dev_app(config: FlaskDevConfiguration) -> Flask:
    return create_app(dev_or_test_config=config)


class DevAppModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Flask] = CallableProvider(provide_dev_app, is_singleton=True)


def create_dependency_injector() -> Injector:
    return Injector(
        [
            DevAppModule(),
            DatabaseDevModule(),
            TestingModule(),
        ]
    )
