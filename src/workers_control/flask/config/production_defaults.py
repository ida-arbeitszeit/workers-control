import os

WOCO_PASSWORD_HASHER = "workers_control.flask.password_hasher:PasswordHasherImpl"

FLASK_DEBUG = 0
TESTING = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

LANGUAGES = {"en": "English", "de": "Deutsch", "es": "Español"}
MAIL_PLUGIN_MODULE = "workers_control.flask.mail_service.flask_mail_service"
MAIL_PLUGIN_CLASS = "FlaskMailService"
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_PORT = 587
AUTO_MIGRATE = os.getenv("AUTO_MIGRATE", False)
FORCE_HTTPS = True
PREFERRED_URL_SCHEME = "https"

FLASK_PROFILER = {
    "enabled": False,
}

ALEMBIC_CONFIG = os.environ["ALEMBIC_CONFIG"]

DEFAULT_USER_TIMEZONE = "UTC"
ALLOWED_OVERDRAW_MEMBER = "0"
ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION = "33"
PAYOUT_FACTOR_CALCULATION_WINDOW = 180

SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/workers_control.db"
