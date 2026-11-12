from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationRequest,
)
from workers_control.web.forms import RequestCollaborationForm
from workers_control.web.request import Request
from workers_control.web.session import Session
from workers_control.web.translator import Translator


@dataclass
class RequestCollaborationController:
    session: Session
    translator: Translator

    def import_form_data(
        self, request: Request
    ) -> RequestCollaborationRequest | RequestCollaborationForm | None:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        form = RequestCollaborationForm(
            plan_id_value=request.get_form("plan_id") or "",
            collaboration_id_value=request.get_form("collaboration_id") or "",
        )
        plan_id = self._parse_uuid(form.plan_id_value)
        if plan_id is None:
            form.plan_id_errors.append(self.translator.gettext("Invalid plan ID."))
        collaboration_id = self._parse_uuid(form.collaboration_id_value)
        if collaboration_id is None:
            form.collaboration_id_errors.append(
                self.translator.gettext("Invalid collaboration ID.")
            )
        if plan_id is None or collaboration_id is None:
            return form
        return RequestCollaborationRequest(
            requester_id=current_user,
            plan_id=plan_id,
            collaboration_id=collaboration_id,
        )

    def _parse_uuid(self, value: str) -> UUID | None:
        try:
            return UUID(value.strip())
        except ValueError:
            return None
