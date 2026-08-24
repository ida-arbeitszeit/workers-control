from dataclasses import dataclass

from workers_control.core.interactors.deny_collaboration import (
    DenyCollaborationResponse,
)
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirection_url: str


@dataclass
class DenyCollaborationPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def render_response(
        self, deny_collaboration_response: DenyCollaborationResponse
    ) -> ViewModel:
        if not deny_collaboration_response.is_rejected:
            self.notifier.display_info(
                self.translator.gettext("Collaboration request has been denied.")
            )
        else:
            rejection_reason = DenyCollaborationResponse.RejectionReason
            match deny_collaboration_response.rejection_reason:
                case (
                    rejection_reason.plan_not_found
                    | rejection_reason.collaboration_not_found
                ):
                    self.notifier.display_warning(
                        self.translator.gettext("Plan or collaboration not found.")
                    )
                case rejection_reason.collaboration_was_not_requested:
                    self.notifier.display_warning(
                        self.translator.gettext(
                            "This collaboration request does not exist."
                        )
                    )
                case rejection_reason.requester_is_not_coordinator:
                    self.notifier.display_warning(
                        self.translator.gettext(
                            "You are not coordinator of this collaboration."
                        )
                    )
                case _:
                    # catchall for rejected responses where rejection
                    # reason cannot be handled by presenter.
                    self.notifier.display_warning(
                        self.translator.gettext("Could not deny collaboration")
                    )
        return ViewModel(redirection_url=self.url_index.get_my_collaborations_url())
