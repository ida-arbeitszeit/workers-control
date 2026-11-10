from uuid import uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.register_member import RegisterMemberInteractor
from workers_control.web.forms import RegisterForm
from workers_control.web.www.presenters.register_member_presenter import (
    RegisterMemberPresenter,
)
from workers_control.web.www.response import Redirect

RejectionReason = RegisterMemberInteractor.Response.RejectionReason


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterMemberPresenter)

    def test_that_error_message_is_rendered_correctly_when_email_is_invalid(
        self,
    ) -> None:
        form = self.present_rejection(RejectionReason.invalid_email)
        assert form.email_errors == [
            self.translator.gettext("Proper email address required")
        ]

    def test_that_error_message_is_rendered_correctly_when_email_already_exists(
        self,
    ) -> None:
        form = self.present_rejection(RejectionReason.member_already_exists)
        self.assertEqual(
            form.email_errors,
            [self.translator.gettext("This email address is already registered.")],
        )

    def test_that_error_message_states_password_mismatch_when_rejection_reason_was_company_with_different_password(
        self,
    ) -> None:
        form = self.present_rejection(
            RejectionReason.company_with_different_password_exists
        )
        self.assertEqual(
            form.email_errors,
            [
                self.translator.gettext(
                    "A company with the same email address already exists but the provided password does not match."
                )
            ],
        )

    def test_that_entered_email_and_name_are_kept_in_form_when_registration_was_rejected(
        self,
    ) -> None:
        self.request.set_form("email", "test@cp.org")
        self.request.set_form("name", "test name")
        form = self.present_rejection(RejectionReason.member_already_exists)
        self.assertEqual(form.email_value, "test@cp.org")
        self.assertEqual(form.name_value, "test name")

    def test_that_user_is_redirected_to_unconfirmed_paged_if_confirmation_is_necessary(
        self,
    ) -> None:
        response = self.create_success_response(is_confirmation_required=True)
        view_model = self.presenter.present_member_registration(response, self.request)
        assert view_model == Redirect(url=self.url_index.get_unconfirmed_member_url())

    def test_that_user_is_redirected_to_dashboard_if_confirmation_is_not_necessary(
        self,
    ) -> None:
        response = self.create_success_response(is_confirmation_required=False)
        view_model = self.presenter.present_member_registration(response, self.request)
        assert view_model == Redirect(url=self.url_index.get_member_dashboard_url())

    def present_rejection(self, reason: RejectionReason) -> RegisterForm:
        response = RegisterMemberInteractor.Response(
            rejection_reason=reason, user_id=None, is_confirmation_required=False
        )
        view_model = self.presenter.present_member_registration(response, self.request)
        assert isinstance(view_model, RegisterForm)
        return view_model

    def create_success_response(
        self, is_confirmation_required: bool = True
    ) -> RegisterMemberInteractor.Response:
        return RegisterMemberInteractor.Response(
            rejection_reason=None,
            user_id=uuid4(),
            is_confirmation_required=is_confirmation_required,
        )
