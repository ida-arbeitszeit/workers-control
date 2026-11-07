from typing import Optional
from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.register_company import RegisterCompany
from workers_control.web.forms import RegisterForm
from workers_control.web.www.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from workers_control.web.www.response import Redirect

RejectionReason = RegisterCompany.Response.RejectionReason


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterCompanyPresenter)

    def test_that_correct_error_message_is_displayed_when_email_is_invalid(
        self,
    ) -> None:
        form = self.present_rejection(RejectionReason.invalid_email)
        self.assertEqual(
            form.email_errors,
            [self.translator.gettext("Proper email address required")],
        )

    def test_that_correct_error_message_is_displayed_when_email_is_already_registered(
        self,
    ) -> None:
        form = self.present_rejection(RejectionReason.company_already_exists)
        self.assertEqual(
            form.email_errors,
            [self.translator.gettext("This email address is already registered.")],
        )

    def test_that_correct_error_message_is_displayed_on_password_field_when_password_is_invalid(
        self,
    ) -> None:
        form = self.present_rejection(RejectionReason.user_password_is_invalid)
        self.assertEqual(
            form.password_errors,
            [self.translator.gettext("Wrong password.")],
        )

    def test_that_entered_email_and_name_are_kept_in_form_when_registration_was_rejected(
        self,
    ) -> None:
        self.request.set_form("email", "test@cp.org")
        self.request.set_form("name", "test name")
        form = self.present_rejection(RejectionReason.company_already_exists)
        self.assertEqual(form.email_value, "test@cp.org")
        self.assertEqual(form.name_value, "test name")

    def test_that_user_is_not_logged_in_when_registration_was_rejected(
        self,
    ) -> None:
        self.present_rejection(RejectionReason.company_already_exists)
        self.assertFalse(self.session.is_logged_in())

    def test_that_user_is_redirected_to_unconfirmed_company_page_on_successful_registration(
        self,
    ) -> None:
        response = self.create_response()
        view_model = self.presenter.present_company_registration(response, self.request)
        self.assertEqual(
            view_model, Redirect(url=self.url_index.get_unconfirmed_company_url())
        )

    def test_that_user_is_logged_in_on_successful_registration(self) -> None:
        response = self.create_response()
        self.presenter.present_company_registration(response, self.request)
        self.assertTrue(self.session.is_logged_in())

    def present_rejection(self, rejection_reason: RejectionReason) -> RegisterForm:
        response = self.create_response(rejection_reason=rejection_reason)
        view_model = self.presenter.present_company_registration(response, self.request)
        assert isinstance(view_model, RegisterForm)
        return view_model

    def create_response(
        self,
        *,
        rejection_reason: Optional[RejectionReason] = None,
    ) -> RegisterCompany.Response:
        company_id: Optional[UUID]
        if rejection_reason is None:
            company_id = uuid4()
        else:
            company_id = None
        return RegisterCompany.Response(
            rejection_reason=rejection_reason, company_id=company_id
        )
