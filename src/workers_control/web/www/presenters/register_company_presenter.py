from dataclasses import dataclass

from workers_control.core.interactors.register_company import RegisterCompany
from workers_control.web.forms import RegisterForm
from workers_control.web.session import Session
from workers_control.web.translator import Translator


@dataclass
class ViewModel:
    is_success_view: bool


@dataclass
class RegisterCompanyPresenter:
    translator: Translator
    session: Session

    def present_company_registration(
        self, response: RegisterCompany.Response, form: RegisterForm
    ) -> ViewModel:
        if response.is_rejected:
            match response.rejection_reason:
                case RegisterCompany.Response.RejectionReason.invalid_email:
                    form.email_field.attach_error(
                        self.translator.gettext("Proper email address required")
                    )
                case RegisterCompany.Response.RejectionReason.company_already_exists:
                    form.email_field.attach_error(
                        self.translator.gettext(
                            "This email address is already registered."
                        )
                    )
                case RegisterCompany.Response.RejectionReason.user_password_is_invalid:
                    form.password_field.attach_error(
                        self.translator.gettext("Wrong password.")
                    )
            return ViewModel(is_success_view=False)
        assert response.company_id
        self.session.login_company(company=response.company_id)
        return ViewModel(is_success_view=True)
