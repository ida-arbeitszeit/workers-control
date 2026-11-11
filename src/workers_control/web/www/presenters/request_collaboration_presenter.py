from dataclasses import dataclass

from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationResponse,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class RequestCollaborationViewModel:
    notification: str
    redirect_url: str | None


@dataclass
class RequestCollaborationPresenter:
    translator: Translator
    url_index: UrlIndex

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("My collaborations"),
                url=self.url_index.get_my_collaborations_url(),
            ),
            NavbarItem(text=self.translator.gettext("Request collaboration"), url=None),
        ]

    def present(
        self, interactor_response: RequestCollaborationResponse
    ) -> RequestCollaborationViewModel:
        if interactor_response.is_rejected:
            assert interactor_response.rejection_reason
            return RequestCollaborationViewModel(
                notification=self._create_rejection_notification(
                    interactor_response.rejection_reason
                ),
                redirect_url=None,
            )
        return RequestCollaborationViewModel(
            notification=self.translator.gettext("Request has been sent."),
            redirect_url=self.url_index.get_my_collaborations_url(),
        )

    def _create_rejection_notification(
        self, rejection_reason: RequestCollaborationResponse.RejectionReason
    ) -> str:
        match rejection_reason:
            case RequestCollaborationResponse.RejectionReason.plan_not_found:
                return self.translator.gettext("Plan not found.")
            case RequestCollaborationResponse.RejectionReason.collaboration_not_found:
                return self.translator.gettext("Collaboration not found.")
            case RequestCollaborationResponse.RejectionReason.plan_inactive:
                return self.translator.gettext("Plan not active.")
            case (
                RequestCollaborationResponse.RejectionReason.plan_has_collaboration
                | RequestCollaborationResponse.RejectionReason.plan_is_already_requesting_collaboration
            ):
                return self.translator.gettext(
                    "Plan is already collaborating or requested a collaboration."
                )
            case RequestCollaborationResponse.RejectionReason.plan_is_public_service:
                return self.translator.gettext("Public plans cannot collaborate.")
            case RequestCollaborationResponse.RejectionReason.requester_is_not_planner:
                return self.translator.gettext(
                    "Only the creator of a plan can request a collaboration."
                )
            case _:
                return self.translator.gettext("An error occurred.")
