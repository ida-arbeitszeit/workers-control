from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationRequest,
)
from workers_control.web.malformed_input_data import MalformedInputData
from workers_control.web.session import Session
from workers_control.web.translator import Translator


class RequestCollaborationForm(Protocol):
    def get_plan_id_string(self) -> str: ...

    def get_collaboration_id_string(self) -> str: ...


@dataclass
class RequestCollaborationController:
    session: Session
    translator: Translator

    def import_form_data(
        self, form: RequestCollaborationForm
    ) -> Union[RequestCollaborationRequest, MalformedInputData, None]:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        try:
            plan_uuid = UUID(form.get_plan_id_string())
        except (ValueError, TypeError):
            return MalformedInputData(
                "plan_id", self.translator.gettext("Invalid plan ID.")
            )
        try:
            collaboration_uuid = UUID(form.get_collaboration_id_string())
        except ValueError:
            return MalformedInputData(
                "collaboration_id",
                self.translator.gettext("Invalid collaboration ID."),
            )
        return RequestCollaborationRequest(
            requester_id=current_user,
            plan_id=plan_uuid,
            collaboration_id=collaboration_uuid,
        )
