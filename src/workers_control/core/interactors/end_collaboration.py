from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class EndCollaborationRequest:
    requester_id: UUID
    plan_id: UUID
    collaboration_id: UUID


@dataclass
class EndCollaborationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        collaboration_not_found = auto()
        plan_has_no_collaboration = auto()
        requester_is_not_authorized = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class EndCollaborationInteractor:
    database_gateway: DatabaseGateway

    def execute(self, request: EndCollaborationRequest) -> EndCollaborationResponse:
        try:
            self._validate_request(request)
        except EndCollaborationResponse.RejectionReason as reason:
            return EndCollaborationResponse(rejection_reason=reason)
        assert (
            self.database_gateway.get_plans()
            .with_id(request.plan_id)
            .update()
            .set_collaboration(None)
            .perform()
        )
        return EndCollaborationResponse(rejection_reason=None)

    def _validate_request(self, request: EndCollaborationRequest) -> None:
        plan_and_collaboration = (
            self.database_gateway.get_plans()
            .with_id(request.plan_id)
            .joined_with_collaboration()
            .first()
        )
        collaboration_and_coordinator = (
            self.database_gateway.get_collaborations()
            .with_id(request.collaboration_id)
            .joined_with_current_coordinator()
            .first()
        )
        if not collaboration_and_coordinator:
            raise EndCollaborationResponse.RejectionReason.collaboration_not_found
        if plan_and_collaboration is None:
            raise EndCollaborationResponse.RejectionReason.plan_not_found
        plan, current_collaboration = plan_and_collaboration
        if not current_collaboration:
            raise EndCollaborationResponse.RejectionReason.plan_has_no_collaboration
        coordinator = collaboration_and_coordinator[1]
        if (request.requester_id != coordinator.id) and (
            request.requester_id != plan.planner
        ):
            raise EndCollaborationResponse.RejectionReason.requester_is_not_authorized
