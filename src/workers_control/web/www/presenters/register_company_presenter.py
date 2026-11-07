from dataclasses import dataclass

from workers_control.core.interactors.register_company import RegisterCompany
from workers_control.web.forms import RegisterForm
from workers_control.web.request import Request
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.response import Redirect


@dataclass
class RegisterCompanyPresenter:
    translator: Translator
    session: Session
    url_index: UrlIndex

    def present_company_registration(
        self, response: RegisterCompany.Response, request: Request
    ) -> Redirect | RegisterForm:
        if response.is_rejected:
            form = RegisterForm(
                email_value=request.get_form("email") or "",
                name_value=request.get_form("name") or "",
            )
            match response.rejection_reason:
                case RegisterCompany.Response.RejectionReason.invalid_email:
                    form.email_errors.append(
                        self.translator.gettext("Proper email address required")
                    )
                case RegisterCompany.Response.RejectionReason.company_already_exists:
                    form.email_errors.append(
                        self.translator.gettext(
                            "This email address is already registered."
                        )
                    )
                case RegisterCompany.Response.RejectionReason.user_password_is_invalid:
                    form.password_errors.append(
                        self.translator.gettext("Wrong password.")
                    )
            return form
        assert response.company_id
        self.session.login_company(company=response.company_id)
        return Redirect(url=self.url_index.get_unconfirmed_company_url())
