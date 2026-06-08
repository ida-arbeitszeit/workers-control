from dataclasses import dataclass

from workers_control.core.interactors.end_cooperation import EndCooperationResponse
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirection_url: str


@dataclass
class EndPlanCooperationPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def render_response(self, response: EndCooperationResponse) -> ViewModel:
        if not response.is_rejected:
            self.notifier.display_info(
                self.translator.gettext("Cooperation has been terminated.")
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext("Cooperation could not be terminated.")
            )
        return ViewModel(redirection_url=self.url_index.get_my_cooperations_url())
