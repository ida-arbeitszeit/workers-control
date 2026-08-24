from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


@dataclass
class AcceptCollaborationRequest:
    requester_id: UUID
    plan_id: UUID
    collaboration_id: UUID


@dataclass
class AcceptCollaborationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        collaboration_not_found = auto()
        plan_inactive = auto()
        plan_has_collaboration = auto()
        plan_is_public_service = auto()
        collaboration_was_not_requested = auto()
        requester_is_not_coordinator = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class AcceptCollaborationInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(
        self, request: AcceptCollaborationRequest
    ) -> AcceptCollaborationResponse:
        try:
            self._validate_request(request)
        except AcceptCollaborationResponse.RejectionReason as reason:
            return AcceptCollaborationResponse(rejection_reason=reason)
        plan = self.database_gateway.get_plans().with_id(request.plan_id)
        plan.update().set_collaboration(
            request.collaboration_id
        ).set_requested_collaboration(None).perform()
        return AcceptCollaborationResponse(rejection_reason=None)

    def _validate_request(self, request: AcceptCollaborationRequest) -> None:
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
        now = self.datetime_service.now()
        if collaboration_and_coordinator is None:
            raise AcceptCollaborationResponse.RejectionReason.collaboration_not_found
        collaboration, coordinator = collaboration_and_coordinator
        if plan_and_collaboration is None:
            raise AcceptCollaborationResponse.RejectionReason.plan_not_found
        plan, current_collaboration = plan_and_collaboration
        if not plan.is_active_as_of(now):
            raise AcceptCollaborationResponse.RejectionReason.plan_inactive
        if current_collaboration:
            raise AcceptCollaborationResponse.RejectionReason.plan_has_collaboration
        if plan.is_public_service:
            raise AcceptCollaborationResponse.RejectionReason.plan_is_public_service
        if plan.requested_collaboration != collaboration.id:
            raise AcceptCollaborationResponse.RejectionReason.collaboration_was_not_requested
        if request.requester_id != coordinator.id:
            raise AcceptCollaborationResponse.RejectionReason.requester_is_not_coordinator
