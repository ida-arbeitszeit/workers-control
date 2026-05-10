from tests.datetime_service import datetime_utc
from tests.web.base_test_case import BaseTestCase
from workers_control.core import records
from workers_control.web.email.registration_email_presenter import (
    RegistrationEmailPresenter,
)


class MemberPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.email_address = "test@test.test"

    def test_that_one_email_is_sent_out(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        assert len(self.email_service.sent_mails) == 1

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        self.assertEqual(
            self.email_service.sent_mails[0].sender,
            self.email_configuration.get_sender_address(),
        )

    def test_that_email_is_sent_to_member_address(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        recipient = self.email_service.sent_mails[0].recipient
        self.assertEqual(self.email_address, recipient)

    def test_that_correct_message_is_rendered(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        token = self.token_service.generate_token(self.email_address)
        expected_url = self.url_index.get_member_confirmation_url(token=token)
        self.presenter.show_member_registration_message(self.email_address)
        email = self.email_service.sent_mails[0]
        self.assertEqual(
            email.html,
            self.text_renderer.render_member_registration_message(
                confirmation_url=expected_url
            ),
        )

    def test_that_subject_line_is_correct(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        email = self.email_service.sent_mails[0]
        self.assertEqual(email.subject, self.translator.gettext("Account confirmation"))


class CompanyPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.email_address = "test@test.test"

    def test_that_one_email_is_sent_out(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        assert len(self.email_service.sent_mails) == 1

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(email.sender, self.email_configuration.get_sender_address())

    def test_that_email_is_sent_to_company_address(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        recipient = email.recipient
        self.assertEqual(self.email_address, recipient)

    def test_that_correct_message_is_rendered(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        token = self.token_service.generate_token(self.email_address)
        expected_url = self.url_index.get_company_confirmation_url(token=token)
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(
            email.html,
            self.text_renderer.render_company_registration_message(
                confirmation_url=expected_url
            ),
        )

    def test_that_subject_line_is_correct(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(email.subject, self.translator.gettext("Account confirmation"))

    def get_sent_email(self) -> records.Email:
        return self.email_service.sent_mails[0]
