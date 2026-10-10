from flask import render_template_string
from werkzeug.datastructures import MultiDict

from workers_control.flask.forms import LoginForm, RegisterForm
from workers_control.flask.i18n import force_locale
from workers_control.flask.translator import FlaskTranslator

from .base_test_case import FlaskTestCase, ViewTestCase
from .translation_catalogs import compile_translation_catalogs


class LocaleSelectionTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        compile_translation_catalogs()

    def test_page_is_english_without_language_preference(self) -> None:
        response = self.client.get("/help")
        assert "User manual" in response.text

    def test_page_is_in_language_selected_in_session(self) -> None:
        self.client.get("/language=de")
        response = self.client.get("/help")
        assert "Nutzerhandbuch" in response.text

    def test_page_is_in_language_requested_by_browser(self) -> None:
        response = self.client.get("/help", headers={"Accept-Language": "de"})
        assert "Nutzerhandbuch" in response.text

    def test_language_selected_in_session_takes_precedence_over_browser(
        self,
    ) -> None:
        self.client.get("/language=es")
        response = self.client.get("/help", headers={"Accept-Language": "de"})
        assert "Manual de usuario" in response.text

    def test_unavailable_language_in_session_falls_back_to_english(self) -> None:
        self.client.get("/language=xx")
        response = self.client.get("/help")
        assert response.status_code == 200
        assert "User manual" in response.text

    def test_unavailable_language_in_session_falls_back_to_browser_language(
        self,
    ) -> None:
        self.client.get("/language=xx")
        response = self.client.get("/help", headers={"Accept-Language": "es"})
        assert "Manual de usuario" in response.text


class TranslationTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        compile_translation_catalogs()
        self.translator = FlaskTranslator()

    def test_english_is_used_outside_of_requests(self) -> None:
        assert self.translator.gettext("User manual") == "User manual"

    def test_forced_locale_is_used_inside_of_context(self) -> None:
        with force_locale("de"):
            assert self.translator.gettext("User manual") == "Nutzerhandbuch"

    def test_previous_locale_is_restored_after_leaving_forced_locale(
        self,
    ) -> None:
        with force_locale("de"):
            with force_locale("es"):
                pass
            assert self.translator.gettext("User manual") == "Nutzerhandbuch"
        assert self.translator.gettext("User manual") == "User manual"

    def test_pgettext_translates_message_with_context(self) -> None:
        with force_locale("de"):
            translation = self.translator.pgettext(
                "Text should be short", "Fixed means"
            )
        assert translation == "Feste PM"

    def test_ngettext_substitutes_num(self) -> None:
        assert self.translator.ngettext("%(num)d beer", "%(num)d beers", 1) == (
            "1 beer"
        )
        assert self.translator.ngettext("%(num)d beer", "%(num)d beers", 2) == (
            "2 beers"
        )

    def test_template_gettext_translates_and_escapes_variables(self) -> None:
        with self.app.test_request_context(), force_locale("de"):
            rendered = render_template_string(
                '{{ gettext("Welcome, %(name)s!", name="<b>Ada</b>") }}'
            )
        assert rendered == "Willkommen, &lt;b&gt;Ada&lt;/b&gt;!"

    def test_lazy_form_label_is_translated_when_rendered(self) -> None:
        with self.app.test_request_context(), force_locale("de"):
            label = LoginForm().email.label()
        assert ">E-Mail</label>" in label

    def test_lazy_validation_message_is_translated(self) -> None:
        with self.app.test_request_context(), force_locale("de"):
            form = LoginForm(MultiDict())
            form.validate()
            error = str(form.email.errors[0])
        assert error == "E-Mail-Adresse erforderlich"

    def test_lazy_validation_message_with_formatting_is_translated(self) -> None:
        with self.app.test_request_context(), force_locale("de"):
            form = RegisterForm(MultiDict({"password": "short"}))
            form.validate()
            error = str(form.password.errors[0])
        assert error == "Das Passwort muss mindestens 8 Zeichen lang sein"
