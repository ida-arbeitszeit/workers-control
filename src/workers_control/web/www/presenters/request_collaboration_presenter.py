from dataclasses import dataclass
from typing import List

from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationResponse,
)
from workers_control.web.translator import Translator
from workers_control.web.www.navbar import NavbarItem


@dataclass
class RequestCollaborationViewModel:
    notifications: List[str]
    is_error: bool


@dataclass
class RequestCollaborationPresenter:
    translator: Translator

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(text=self.translator.gettext("Request collaboration"), url=None)
        ]

    def present(
        self, interactor_response: RequestCollaborationResponse
    ) -> RequestCollaborationViewModel:
        view_model = self._create_view_model(interactor_response)
        return view_model

    def _create_view_model(
        self, interactor_response: RequestCollaborationResponse
    ) -> RequestCollaborationViewModel:
        notifications = []
        if not interactor_response.is_rejected:
            is_error = False
            notifications.append(self.translator.gettext("Request has been sent."))
        else:
            is_error = True
            if (
                interactor_response.rejection_reason
                == RequestCollaborationResponse.RejectionReason.plan_not_found
            ):
                notifications.append(self.translator.gettext("Plan not found."))
            elif (
                interactor_response.rejection_reason
                == RequestCollaborationResponse.RejectionReason.collaboration_not_found
            ):
                notifications.append(
                    self.translator.gettext("Collaboration not found.")
                )
            elif (
                interactor_response.rejection_reason
                == RequestCollaborationResponse.RejectionReason.plan_inactive
            ):
                notifications.append(self.translator.gettext("Plan not active."))
            elif interactor_response.rejection_reason in (
                RequestCollaborationResponse.RejectionReason.plan_has_collaboration,
                RequestCollaborationResponse.RejectionReason.plan_is_already_requesting_collaboration,
            ):
                notifications.append(
                    self.translator.gettext(
                        "Plan is already collaborating or requested a collaboration."
                    )
                )
            elif (
                interactor_response.rejection_reason
                == RequestCollaborationResponse.RejectionReason.plan_is_public_service
            ):
                notifications.append(
                    self.translator.gettext("Public plans cannot collaborate.")
                )
            elif (
                interactor_response.rejection_reason
                == RequestCollaborationResponse.RejectionReason.requester_is_not_planner
            ):
                notifications.append(
                    self.translator.gettext(
                        "Only the creator of a plan can request a collaboration."
                    )
                )
        return RequestCollaborationViewModel(
            notifications=notifications, is_error=is_error
        )
