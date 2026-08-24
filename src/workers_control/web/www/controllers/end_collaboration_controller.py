from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from workers_control.core.interactors.end_collaboration import EndCollaborationRequest
from workers_control.web.request import Request
from workers_control.web.session import Session


@dataclass
class EndCollaborationController:
    session: Session

    def process_request_data(
        self, request: Request
    ) -> Optional[EndCollaborationRequest]:
        plan_id = request.get_form("plan_id")
        collaboration_id = request.get_form("collaboration_id")
        current_user = self.session.get_current_user()
        if not all([plan_id, collaboration_id, current_user]):
            return None
        assert plan_id
        assert collaboration_id
        assert current_user

        try:
            plan_uuid = UUID(plan_id)
            collaboration_uuid = UUID(collaboration_id)
        except ValueError:
            return None

        interactor_request = EndCollaborationRequest(
            current_user, plan_uuid, collaboration_uuid
        )
        return interactor_request
