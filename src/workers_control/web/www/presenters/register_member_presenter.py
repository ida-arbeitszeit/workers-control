from dataclasses import dataclass

from workers_control.core.interactors.register_member import RegisterMemberInteractor
from workers_control.web.forms import RegisterForm
from workers_control.web.request import Request
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.response import Redirect


@dataclass
class RegisterMemberPresenter:
    session: Session
    translator: Translator
    url_index: UrlIndex

    def present_member_registration(
        self, response: RegisterMemberInteractor.Response, request: Request
    ) -> Redirect | RegisterForm:
        if response.is_rejected:
            form = RegisterForm(
                email_value=request.get_form("email") or "",
                name_value=request.get_form("name") or "",
            )
            match response.rejection_reason:
                case RegisterMemberInteractor.Response.RejectionReason.invalid_email:
                    form.email_errors.append(
                        self.translator.gettext("Proper email address required")
                    )
                case (
                    RegisterMemberInteractor.Response.RejectionReason.member_already_exists
                ):
                    form.email_errors.append(
                        self.translator.gettext(
                            "This email address is already registered."
                        )
                    )
                case (
                    RegisterMemberInteractor.Response.RejectionReason.company_with_different_password_exists
                ):
                    form.email_errors.append(
                        self.translator.gettext(
                            "A company with the same email address already exists but the provided password does not match."
                        )
                    )
            return form
        assert response.user_id
        self.session.login_member(response.user_id)
        return Redirect(
            url=(
                self.url_index.get_unconfirmed_member_url()
                if response.is_confirmation_required
                else self.url_index.get_member_dashboard_url()
            )
        )
