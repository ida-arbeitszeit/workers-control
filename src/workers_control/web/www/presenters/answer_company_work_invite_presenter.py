from dataclasses import dataclass

from workers_control.core.interactors.answer_company_work_invite import (
    AnswerCompanyWorkInviteResponse,
)
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class AnswerCompanyWorkInvitePresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present(self, response: AnswerCompanyWorkInviteResponse) -> ViewModel:
        if response.is_success:
            if response.is_accepted:
                self.user_notifier.display_info(
                    self.translator.gettext('You successfully joined "%(company)s".')
                    % dict(company=response.company_name)
                )
            else:
                self.user_notifier.display_info(
                    self.translator.gettext(
                        'You rejected the invitation from "%(company)s".'
                    )
                    % dict(company=response.company_name)
                )
        else:
            self.user_notifier.display_warning(
                self.translator.gettext("Accepting or rejecting is not possible.")
            )
        return self.ViewModel(redirect_url=self.url_index.get_member_dashboard_url())
