from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors import change_user_password
from workers_control.web.www.presenters.reset_password_presenter import (
    ResetPasswordPresenter,
)


class ResetPasswordPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ResetPasswordPresenter)

    def test_success_shows_info_notification(self) -> None:
        response = self._create_response(is_changed=True)
        self.presenter.present_password_change(response)
        self.assertTrue(self.notifier.infos)

    def test_success_shows_no_warning(self) -> None:
        response = self._create_response(is_changed=True)
        self.presenter.present_password_change(response)
        self.assertFalse(self.notifier.warnings)

    def test_success_shows_correct_message(self) -> None:
        response = self._create_response(is_changed=True)
        self.presenter.present_password_change(response)
        self.assertEqual(
            self.notifier.infos[-1],
            self.translator.gettext(
                "Your password has been reset. You can now log in with your new password."
            ),
        )

    def test_success_redirects_to_start_page(self) -> None:
        response = self._create_response(is_changed=True)
        view_model = self.presenter.present_password_change(response)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_start_page_url(),
        )

    def test_failure_shows_warning(self) -> None:
        response = self._create_response(is_changed=False)
        self.presenter.present_password_change(response)
        self.assertTrue(self.notifier.warnings)

    def test_failure_shows_no_info(self) -> None:
        response = self._create_response(is_changed=False)
        self.presenter.present_password_change(response)
        self.assertFalse(self.notifier.infos)

    def test_failure_shows_correct_warning_message(self) -> None:
        response = self._create_response(is_changed=False)
        self.presenter.present_password_change(response)
        self.assertEqual(
            self.notifier.warnings[-1],
            self.translator.gettext("Password reset failed. Please try again."),
        )

    def test_failure_redirects_to_request_password_reset(self) -> None:
        response = self._create_response(is_changed=False)
        view_model = self.presenter.present_password_change(response)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_request_password_reset_url(),
        )

    def _create_response(self, is_changed: bool) -> change_user_password.Response:
        return change_user_password.Response(is_changed=is_changed)
