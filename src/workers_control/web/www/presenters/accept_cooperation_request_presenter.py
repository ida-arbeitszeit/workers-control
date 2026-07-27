from dataclasses import dataclass

from workers_control.core.interactors.accept_cooperation import (
    AcceptCooperationResponse,
)
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirection_url: str


@dataclass
class AcceptCooperationRequestPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def render_response(self, response: AcceptCooperationResponse) -> ViewModel:
        if not response.is_rejected:
            self.notifier.display_info(
                self.translator.gettext("Cooperation request has been accepted.")
            )
        else:
            rejection_reason = AcceptCooperationResponse.RejectionReason
            match response.rejection_reason:
                case (
                    rejection_reason.plan_not_found
                    | rejection_reason.cooperation_not_found
                ):
                    self.notifier.display_warning(
                        self.translator.gettext("Plan or cooperation not found.")
                    )
                case (
                    rejection_reason.plan_inactive
                    | rejection_reason.plan_has_cooperation
                    | rejection_reason.plan_is_public_service
                ):
                    self.notifier.display_warning(
                        self.translator.gettext("Something's wrong with that plan.")
                    )
                case rejection_reason.cooperation_was_not_requested:
                    self.notifier.display_warning(
                        self.translator.gettext(
                            "This cooperation request does not exist."
                        )
                    )
                case rejection_reason.requester_is_not_coordinator:
                    self.notifier.display_warning(
                        self.translator.gettext(
                            "You are not coordinator of this cooperation."
                        )
                    )
        return ViewModel(redirection_url=self.url_index.get_my_cooperations_url())
