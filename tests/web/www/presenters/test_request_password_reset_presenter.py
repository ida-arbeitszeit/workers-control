from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.presenters.request_password_reset_presenter import (
    RequestPasswordResetPresenter,
)


class RequestPasswordResetPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RequestPasswordResetPresenter)

    def test_info_notification_is_shown(self) -> None:
        self.presenter.present_password_reset_request()
        self.assertTrue(self.notifier.infos)

    def test_no_warning_is_shown(self) -> None:
        self.presenter.present_password_reset_request()
        self.assertFalse(self.notifier.warnings)

    def test_correct_info_message_is_shown(self) -> None:
        self.presenter.present_password_reset_request()
        self.assertEqual(
            self.notifier.infos[-1],
            self.translator.gettext(
                "If an account with that email exists, we have sent a password reset link."
            ),
        )

    def test_redirect_url_is_returned(self) -> None:
        view_model = self.presenter.present_password_reset_request()
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_request_password_reset_url(),
        )
