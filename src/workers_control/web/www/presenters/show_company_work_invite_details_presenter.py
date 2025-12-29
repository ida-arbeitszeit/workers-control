from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors.show_company_work_invite_details import (
    ShowCompanyWorkInviteDetailsResponse,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ShowCompanyWorkInviteDetailsPresenter:
    @dataclass
    class ViewModel:
        answer_invite_url: str
        explanation_text: str

    url_index: UrlIndex
    translator: Translator

    def render_response(
        self, response: ShowCompanyWorkInviteDetailsResponse
    ) -> Optional[ViewModel]:
        if (details := response.details) is not None:
            return self.ViewModel(
                answer_invite_url=self.url_index.get_answer_company_work_invite_url(
                    invite_id=details.invite_id, is_absolute=False
                ),
                explanation_text=self.translator.gettext(
                    'The company "%(company_name)s" invites you to join them. Do you want to accept this invitation?'
                )
                % dict(company_name=details.company_name),
            )
        else:
            return None
