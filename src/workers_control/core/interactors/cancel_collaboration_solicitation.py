from dataclasses import dataclass
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class CancelCollaborationSolicitationRequest:
    requester_id: UUID
    plan_id: UUID


@dataclass
class CancelCollaborationSolicitationInteractor:
    database_gateway: DatabaseGateway

    def execute(self, request: CancelCollaborationSolicitationRequest) -> bool:
        plans_changed_count = (
            self.database_gateway.get_plans()
            .with_id(request.plan_id)
            .planned_by(request.requester_id)
            .that_request_collaboration_with_coordinator()
            .update()
            .set_requested_collaboration(None)
            .perform()
        )
        return bool(plans_changed_count)
