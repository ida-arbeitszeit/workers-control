from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.email_notifications import (
    CollaborationRequestEmail,
    EmailSender,
)
from workers_control.core.records import Company, EmailAddress
from workers_control.core.repositories import DatabaseGateway


@dataclass
class RequestCollaborationRequest:
    requester_id: UUID
    plan_id: UUID
    collaboration_id: UUID


@dataclass
class RequestCollaborationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        collaboration_not_found = auto()
        plan_inactive = auto()
        plan_has_collaboration = auto()
        plan_is_already_requesting_collaboration = auto()
        plan_is_public_service = auto()
        requester_is_not_planner = auto()

    coordinator_name: Optional[str]
    coordinator_email: Optional[str]
    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class RequestCollaborationInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    email_sender: EmailSender

    def execute(
        self, request: RequestCollaborationRequest
    ) -> RequestCollaborationResponse:
        try:
            coordinator, email = self._validate_request(request)
        except RequestCollaborationResponse.RejectionReason as reason:
            return RequestCollaborationResponse(
                coordinator_name=None, coordinator_email=None, rejection_reason=reason
            )
        self.email_sender.send_email(
            CollaborationRequestEmail(
                coordinator_email_address=email.address,
                coordinator_name=coordinator.name,
            )
        )
        self.database_gateway.get_plans().with_id(
            request.plan_id
        ).update().set_requested_collaboration(request.collaboration_id).perform()
        return RequestCollaborationResponse(
            coordinator_name=coordinator.name,
            coordinator_email=email.address,
            rejection_reason=None,
        )

    def _validate_request(
        self, request: RequestCollaborationRequest
    ) -> Tuple[Company, EmailAddress]:
        now = self.datetime_service.now()
        plan_and_current_collaboration = (
            self.database_gateway.get_plans()
            .with_id(request.plan_id)
            .joined_with_collaboration()
            .first()
        )
        collaboration_and_coordinator = (
            self.database_gateway.get_companies()
            .that_is_coordinating_collaboration(request.collaboration_id)
            .joined_with_email_address()
            .first()
        )
        if collaboration_and_coordinator is None:
            raise RequestCollaborationResponse.RejectionReason.collaboration_not_found
        if plan_and_current_collaboration is None:
            raise RequestCollaborationResponse.RejectionReason.plan_not_found
        plan, current_collaboration = plan_and_current_collaboration
        if not plan.is_active_as_of(now):
            raise RequestCollaborationResponse.RejectionReason.plan_inactive
        if current_collaboration:
            raise RequestCollaborationResponse.RejectionReason.plan_has_collaboration
        if plan.requested_collaboration:
            raise RequestCollaborationResponse.RejectionReason.plan_is_already_requesting_collaboration
        if plan.is_public_service:
            raise RequestCollaborationResponse.RejectionReason.plan_is_public_service
        if request.requester_id != plan.planner:
            raise RequestCollaborationResponse.RejectionReason.requester_is_not_planner
        return collaboration_and_coordinator
