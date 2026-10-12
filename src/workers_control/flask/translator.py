from typing import Any, Callable

from workers_control.flask.i18n import get_translations
from workers_control.web.translator import Number, Translator


class LazyString:
    def __init__(self, translate: Callable[[str], str], text: str) -> None:
        self._translate = translate
        self._text = text

    def __str__(self) -> str:
        return self._translate(self._text)

    def __mod__(self, other: Any) -> str:
        return str(self) % other


class FlaskTranslator(Translator):
    def gettext(self, text: str) -> str:
        return get_translations().gettext(text)

    def pgettext(self, context: str, text: str) -> str:
        return get_translations().pgettext(context, text)

    def ngettext(self, singular: str, plural: str, n: Number) -> str:
        translated = get_translations().ngettext(singular, plural, n)  # type: ignore[arg-type]
        return translated % {"num": n}

    def lazy_gettext(self, text: str) -> LazyString:
        return LazyString(self.gettext, text)
