from click.testing import Result

from .base_test_case import FlaskTestCase
from .translation_catalogs import compile_translation_catalogs


class InviteAccountantTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        compile_translation_catalogs()

    def test_invitation_is_sent_in_english_by_default(self) -> None:
        with self.email_service.record_messages() as outbox:
            result = self.invite_accountant("test@test.test")
        assert result.exit_code == 0
        assert outbox[0].subject == "Invitation to Workers Control app"

    def test_invitation_is_sent_in_requested_language(self) -> None:
        with self.email_service.record_messages() as outbox:
            result = self.invite_accountant("test@test.test", "--language", "de")
        assert result.exit_code == 0
        assert outbox[0].subject == "Einladung zur Workers Control App"

    def test_unavailable_language_is_rejected_without_sending_an_invitation(
        self,
    ) -> None:
        with self.email_service.record_messages() as outbox:
            result = self.invite_accountant("test@test.test", "--language", "xx")
        assert result.exit_code == 2
        assert not outbox

    def invite_accountant(self, *args: str) -> Result:
        runner = self.app.test_cli_runner()
        return runner.invoke(args=["invite-accountant", *args])
