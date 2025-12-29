from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors.log_in_member import LogInMemberInteractor
from workers_control.web.forms import LoginMemberForm
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class LogInMemberPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    session: Session
    translator: Translator
    member_url_index: UrlIndex

    def present_login_process(
        self, response: LogInMemberInteractor.Response, form: LoginMemberForm
    ) -> ViewModel:
        if response.is_logged_in:
            assert response.user_id
            self.session.login_member(
                member=response.user_id, remember=form.remember_field().get_value()
            )
            next_url = (
                self.session.pop_next_url()
                or self.member_url_index.get_member_dashboard_url()
            )
            return self.ViewModel(redirect_url=next_url)
        else:
            if (
                response.rejection_reason
                == LogInMemberInteractor.RejectionReason.unknown_email_address
            ):
                form.email_field().attach_error(
                    self.translator.gettext(
                        "Email address incorrect. Are you already registered as a member?"
                    ),
                )
            else:
                form.password_field().attach_error(
                    self.translator.gettext("Incorrect password"),
                )
            return self.ViewModel(redirect_url=None)
