from tests.base_test_case import BaseTestCase
from tests.web.www.forms import ChangeUserNameFormImpl
from workers_control.core.interactors import change_user_name as interactor
from workers_control.web.www.presenters import change_user_name_presenter as presenter

rr = interactor.Response.RejectionReason


class ChangeUserNamePresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(presenter.ChangeUserNamePresenter)

    def test_on_success_redirects_to_account_details(self) -> None:
        view_model = self.presenter.render_response(self._response(None), self._form())
        assert view_model.redirect_url == self.url_index.get_user_account_details_url()

    def test_on_failure_does_not_redirect(self) -> None:
        view_model = self.presenter.render_response(
            self._response(rr.invalid_name), self._form()
        )
        assert view_model.redirect_url is None

    def test_on_success_shows_info_message(self) -> None:
        self.presenter.render_response(self._response(None), self._form())
        expected = self.translator.gettext("Your name has been changed.")
        assert expected in self.notifier.infos

    def test_on_failure_shows_warning(self) -> None:
        self.presenter.render_response(self._response(rr.invalid_name), self._form())
        expected = self.translator.gettext(
            "Your request to change your name was rejected."
        )
        assert expected in self.notifier.warnings

    def test_invalid_name_error_is_attached_to_new_name_field(self) -> None:
        form = self._form()
        self.presenter.render_response(self._response(rr.invalid_name), form)
        assert self.translator.gettext("The new name is invalid.") in (
            form.new_name_field.errors
        )

    def test_incorrect_password_error_is_attached_to_password_field(self) -> None:
        form = self._form()
        self.presenter.render_response(self._response(rr.incorrect_password), form)
        assert self.translator.gettext("The password is incorrect.") in (
            form.current_password_field.errors
        )

    def _form(self) -> ChangeUserNameFormImpl:
        return ChangeUserNameFormImpl.from_values("New Name", "pw1234")

    def _response(
        self, rejection_reason: interactor.Response.RejectionReason | None
    ) -> interactor.Response:
        return interactor.Response(rejection_reason=rejection_reason)
