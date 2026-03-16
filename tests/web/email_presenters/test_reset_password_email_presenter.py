from tests.web.base_test_case import BaseTestCase
from tests.web.email import Email
from workers_control.core.email_notifications import (
    ResetPasswordConfirmation,
    ResetPasswordRequest,
)
from workers_control.web.email.reset_password_email_presenter import (
    ResetPasswordEmailPresenter,
)


class ResetPasswordRequestTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ResetPasswordEmailPresenter)

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.present_reset_password_request(self.create_message())
        self.assertTrue(self.email_service.sent_mails)

    def test_that_email_is_sent_to_exactly_one_recipient(self) -> None:
        self.presenter.present_reset_password_request(self.create_message())
        email = self.get_sent_email()
        self.assertEqual(len(email.recipients), 1)

    def test_that_email_is_sent_to_correct_address(self) -> None:
        self.presenter.present_reset_password_request(
            self.create_message(email_address="user@example.com")
        )
        email = self.get_sent_email()
        self.assertEqual(email.recipients[0], "user@example.com")

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.present_reset_password_request(self.create_message())
        email = self.get_sent_email()
        self.assertEqual(email.sender, self.email_configuration.get_sender_address())

    def test_that_subject_is_correct(self) -> None:
        self.presenter.present_reset_password_request(self.create_message())
        email = self.get_sent_email()
        self.assertEqual(
            email.subject,
            self.translator.gettext("Password reset requested"),
        )

    def test_that_html_body_is_rendered_correctly(self) -> None:
        self.presenter.present_reset_password_request(
            self.create_message(reset_token="abc123")
        )
        email = self.get_sent_email()
        expected_url = self.url_index.get_password_reset_url(token="abc123")
        self.assertEqual(
            email.html,
            self.text_renderer.render_password_reset_request_email(
                reset_url=expected_url
            ),
        )

    def create_message(
        self,
        email_address: str = "test@test.test",
        reset_token: str = "some-token",
    ) -> ResetPasswordRequest:
        return ResetPasswordRequest(
            email_address=email_address,
            reset_token=reset_token,
        )

    def get_sent_email(self) -> Email:
        return self.email_service.sent_mails[0]


class ResetPasswordConfirmationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ResetPasswordEmailPresenter)

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.present_reset_password_confirmation(self.create_message())
        self.assertTrue(self.email_service.sent_mails)

    def test_that_email_is_sent_to_exactly_one_recipient(self) -> None:
        self.presenter.present_reset_password_confirmation(self.create_message())
        email = self.get_sent_email()
        self.assertEqual(len(email.recipients), 1)

    def test_that_email_is_sent_to_correct_address(self) -> None:
        self.presenter.present_reset_password_confirmation(
            self.create_message(email_address="user@example.com")
        )
        email = self.get_sent_email()
        self.assertEqual(email.recipients[0], "user@example.com")

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.present_reset_password_confirmation(self.create_message())
        email = self.get_sent_email()
        self.assertEqual(email.sender, self.email_configuration.get_sender_address())

    def test_that_subject_is_correct(self) -> None:
        self.presenter.present_reset_password_confirmation(self.create_message())
        email = self.get_sent_email()
        self.assertEqual(
            email.subject,
            self.translator.gettext("Password reset successful"),
        )

    def test_that_html_body_is_rendered_correctly(self) -> None:
        self.presenter.present_reset_password_confirmation(self.create_message())
        email = self.get_sent_email()
        self.assertEqual(
            email.html,
            self.text_renderer.render_password_reset_confirmation_email(),
        )

    def create_message(
        self,
        email_address: str = "test@test.test",
    ) -> ResetPasswordConfirmation:
        return ResetPasswordConfirmation(
            email_address=email_address,
        )

    def get_sent_email(self) -> Email:
        return self.email_service.sent_mails[0]
