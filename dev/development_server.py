import json
import os
from logging.config import dictConfig
from pathlib import Path

from flask import Flask

import workers_control.flask
from dev.dependency_injection import (
    create_dependency_injector,
)
from dev.dev_cli import (
    create_generate_cli_group,
)

config_path = Path(__file__).parent / "logging_config.json"

with open(config_path, "r") as f:
    config = json.load(f)
    dictConfig(config)


class FlaskDevConfiguration:
    # keys must be uppercase

    FLASK_DEBUG = 1
    TESTING = True

    SERVER_NAME = os.environ.get("WOCO_SERVER_NAME", "127.0.0.1:5000")
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
    MAIL_PLUGIN = (
        "workers_control.flask.mail_service.debug_mail_service:DebugMailService"
    )
    MAIL_ENCRYPTION_TYPE = "tls"

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
    PAYOUT_FACTOR_CALCULATION_WINDOW = 180

    SECURITY_PASSWORD_SALT = "dev password salt"
    SECRET_KEY = os.environ.get("DEV_SECRET_KEY", "dev secret key")
    WTF_CSRF_ENABLED = False
    WOCO_PASSWORD_HASHER = "tests.password_hasher:PasswordHasherImpl"

    SQLALCHEMY_DATABASE_URI = os.environ["WOCO_DEV_DB"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALEMBIC_CONFIG = os.getenv("ALEMBIC_CONFIG")
    AUTO_MIGRATE = os.getenv("AUTO_MIGRATE", False)


def register_cli_commands(app: Flask) -> Flask:
    injector = create_dependency_injector()
    generate = create_generate_cli_group(injector)
    app.cli.add_command(generate)
    return app


def create_app() -> Flask:
    app = workers_control.flask.create_app(dev_or_test_config=FlaskDevConfiguration())
    app = register_cli_commands(app)
    return app
