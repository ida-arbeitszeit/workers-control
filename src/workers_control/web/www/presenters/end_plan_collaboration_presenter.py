from dataclasses import dataclass

from workers_control.core.interactors.end_collaboration import EndCollaborationResponse
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirection_url: str


@dataclass
class EndPlanCollaborationPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def render_response(self, response: EndCollaborationResponse) -> ViewModel:
        if not response.is_rejected:
            self.notifier.display_info(
                self.translator.gettext("Collaboration has been terminated.")
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext("Collaboration could not be terminated.")
            )
        return ViewModel(redirection_url=self.url_index.get_my_collaborations_url())
