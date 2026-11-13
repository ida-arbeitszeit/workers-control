from tests.flask_integration.base_test_case import ViewTestCase
from tests.flask_integration.translation_catalogs import compile_translation_catalogs

INVALID_LINK_PATH = "/confirm-member/not-a-token"


class ConfirmationLinkNotificationTranslationTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        compile_translation_catalogs()

    def test_notification_is_english_in_english_ui(self) -> None:
        self.client.get("/language=en")
        response = self.client.get(INVALID_LINK_PATH, follow_redirects=True)
        assert "The confirmation link is invalid or has expired." in response.text

    def test_notification_is_spanish_in_spanish_ui(self) -> None:
        self.client.get("/language=es")
        response = self.client.get(INVALID_LINK_PATH, follow_redirects=True)
        assert "El enlace de confirmación no es válido o ha caducado." in response.text

    def test_company_notification_is_english_in_english_ui(self) -> None:
        self.client.get("/language=en")
        response = self.client.get(
            "/company/confirm/not-a-token", follow_redirects=True
        )
        assert "The confirmation link is invalid or has expired." in response.text

    def test_confirmed_company_notification_is_english_in_english_ui(self) -> None:
        email = self.email_generator.get_random_email()
        self.company_generator.create_company(email=email, confirmed=False)
        token = self.token_service.generate_token(email)
        self.client.get("/language=en")
        response = self.client.get(f"/company/confirm/{token}", follow_redirects=True)
        assert "The account has been confirmed. Thank you!" in response.text
