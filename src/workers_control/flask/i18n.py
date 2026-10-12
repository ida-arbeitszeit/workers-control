import gettext
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from typing import Generator

from flask import (
    Flask,
    current_app,
    g,
    has_app_context,
    has_request_context,
    request,
    session,
)

TRANSLATIONS_DIRECTORY = Path(__file__).parent / "translations"
DEFAULT_LOCALE = "en"


def initialize_i18n(app: Flask) -> None:
    app.jinja_env.add_extension("jinja2.ext.i18n")
    app.jinja_env.install_gettext_callables(  # type: ignore[attr-defined]
        gettext=lambda message: get_translations().gettext(message),
        ngettext=lambda singular, plural, n: get_translations().ngettext(
            singular, plural, n
        ),
        pgettext=lambda context, message: get_translations().pgettext(context, message),
        npgettext=lambda context, singular, plural, n: get_translations().npgettext(
            context, singular, plural, n
        ),
        newstyle=True,
    )


def get_translations() -> gettext.NullTranslations:
    if not has_app_context():
        return gettext.NullTranslations()
    return _load_translations(get_locale())


def get_locale() -> str:
    if forced_locale := g.get("forced_locale"):
        return forced_locale
    if not has_request_context():
        return DEFAULT_LOCALE
    languages = current_app.config["LANGUAGES"]
    selected_language: str = session.get("language", "")
    if selected_language in languages:
        return selected_language
    return request.accept_languages.best_match(languages.keys()) or DEFAULT_LOCALE


@contextmanager
def force_locale(locale: str) -> Generator[None]:
    previous_locale = g.get("forced_locale")
    g.forced_locale = locale
    try:
        yield
    finally:
        g.forced_locale = previous_locale


@cache
def _load_translations(locale: str) -> gettext.NullTranslations:
    return gettext.translation(
        "messages", TRANSLATIONS_DIRECTORY, languages=[locale], fallback=True
    )
