from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from workers_control.core import email_notifications
from workers_control.web.email.name_change_confirmation_presenter import (
    NameChangeConfirmationPresenter,
)


class NameChangeConfirmationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(NameChangeConfirmationPresenter)

    def test_that_one_email_is_sent_on_present(self) -> None:
        self.presenter.present_name_change_confirmation(self._message())
        assert len(self.email_service.sent_mails) == 1

    @parameterized.expand(
        [
            ("user@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_email_is_sent_to_the_users_address(
        self, expected_address: str
    ) -> None:
        self.presenter.present_name_change_confirmation(
            self._message(email_address=expected_address)
        )
        assert self.email_service.sent_mails[-1].recipient == expected_address

    def test_that_sender_is_the_default_one(self) -> None:
        self.presenter.present_name_change_confirmation(self._message())
        assert (
            self.email_service.sent_mails[-1].sender
            == self.email_configuration.get_sender_address()
        )

    def test_that_subject_line_is_correct(self) -> None:
        expected_subject = self.translator.gettext("Your account name was changed")
        self.presenter.present_name_change_confirmation(self._message())
        assert self.email_service.sent_mails[-1].subject == expected_subject

    @parameterized.expand(
        [
            ("New Name",),
            ("Some Other Name",),
        ]
    )
    def test_that_html_is_rendered_with_the_new_name(self, new_name: str) -> None:
        self.presenter.present_name_change_confirmation(
            self._message(new_name=new_name)
        )
        assert self.email_service.sent_mails[
            -1
        ].html == self.text_renderer.render_name_change_confirmation(new_name=new_name)

    def _message(
        self,
        *,
        email_address: str = "user@test.test",
        new_name: str = "New Name",
    ) -> email_notifications.NameChangeConfirmation:
        return email_notifications.NameChangeConfirmation(
            email_address=email_address,
            new_name=new_name,
        )
