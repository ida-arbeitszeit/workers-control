from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


@dataclass
class DenyCollaborationRequest:
    requester_id: UUID
    plan_id: UUID
    collaboration_id: UUID


@dataclass
class DenyCollaborationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        collaboration_not_found = auto()
        collaboration_was_not_requested = auto()
        requester_is_not_coordinator = auto()
        plan_is_inactive = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class DenyCollaborationInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(self, request: DenyCollaborationRequest) -> DenyCollaborationResponse:
        try:
            self._validate_request(request)
        except DenyCollaborationResponse.RejectionReason as reason:
            return DenyCollaborationResponse(rejection_reason=reason)

        self.database_gateway.get_plans().with_id(
            request.plan_id
        ).update().set_requested_collaboration(None).perform()
        return DenyCollaborationResponse(rejection_reason=None)

    def _validate_request(self, request: DenyCollaborationRequest) -> None:
        plan = self.database_gateway.get_plans().with_id(request.plan_id).first()
        now = self.datetime_service.now()
        collaboration_and_coordinator = (
            self.database_gateway.get_collaborations()
            .with_id(request.collaboration_id)
            .joined_with_current_coordinator()
            .first()
        )
        if not collaboration_and_coordinator:
            raise DenyCollaborationResponse.RejectionReason.collaboration_not_found
        collaboration, coordinator = collaboration_and_coordinator
        if plan is None:
            raise DenyCollaborationResponse.RejectionReason.plan_not_found
        if not plan.is_active_as_of(now):
            raise DenyCollaborationResponse.RejectionReason.plan_is_inactive
        if plan.requested_collaboration != collaboration.id:
            raise DenyCollaborationResponse.RejectionReason.collaboration_was_not_requested
        if request.requester_id != coordinator.id:
            raise DenyCollaborationResponse.RejectionReason.requester_is_not_coordinator
