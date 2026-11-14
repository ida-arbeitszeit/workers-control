from dataclasses import dataclass
from typing import assert_never

from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationResponse,
)
from workers_control.web.forms import RequestCollaborationForm
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem
from workers_control.web.www.response import Redirect


@dataclass
class RequestCollaborationPresenter:
    translator: Translator
    url_index: UrlIndex
    notifier: Notifier

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("My collaborations"),
                url=self.url_index.get_my_collaborations_url(),
            ),
            NavbarItem(text=self.translator.gettext("Request collaboration"), url=None),
        ]

    def present(
        self, interactor_response: RequestCollaborationResponse, request: Request
    ) -> Redirect | RequestCollaborationForm:
        if interactor_response.is_rejected:
            assert interactor_response.rejection_reason
            form = RequestCollaborationForm(
                plan_id_value=request.get_form("plan_id") or "",
                collaboration_id_value=request.get_form("collaboration_id") or "",
            )
            form = self._append_form_errors(form, interactor_response.rejection_reason)
            self.notifier.display_warning(
                self.translator.gettext("Request was not successful.")
            )
            return form
        self.notifier.display_info(self.translator.gettext("Request has been sent."))
        return Redirect(
            url=self.url_index.get_my_collaborations_url(),
        )

    def _append_form_errors(
        self,
        form: RequestCollaborationForm,
        rejection_reason: RequestCollaborationResponse.RejectionReason,
    ) -> RequestCollaborationForm:
        match rejection_reason:
            case RequestCollaborationResponse.RejectionReason.plan_not_found:
                error_msg = self.translator.gettext("Plan not found.")
            case RequestCollaborationResponse.RejectionReason.collaboration_not_found:
                error_msg = self.translator.gettext("Collaboration not found.")
            case RequestCollaborationResponse.RejectionReason.plan_inactive:
                error_msg = self.translator.gettext("Plan not active.")
            case (
                RequestCollaborationResponse.RejectionReason.plan_has_collaboration
                | RequestCollaborationResponse.RejectionReason.plan_is_already_requesting_collaboration
            ):
                error_msg = self.translator.gettext(
                    "Plan is already collaborating or requested a collaboration."
                )
            case RequestCollaborationResponse.RejectionReason.plan_is_public_service:
                error_msg = self.translator.gettext("Public plans cannot collaborate.")
            case RequestCollaborationResponse.RejectionReason.requester_is_not_planner:
                error_msg = self.translator.gettext(
                    "Only the creator of a plan can request a collaboration."
                )
            case _:
                assert_never(rejection_reason)
        form.general_errors.append(error_msg)
        return form
