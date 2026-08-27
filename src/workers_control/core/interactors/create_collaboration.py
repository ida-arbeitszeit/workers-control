from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.records import Company
from workers_control.core.repositories import DatabaseGateway


@dataclass
class CreateCollaborationRequest:
    coordinator_id: UUID
    name: str
    definition: str


@dataclass
class CreateCollaborationResponse:
    class RejectionReason(Exception, Enum):
        coordinator_not_found = auto()
        collaboration_with_name_exists = auto()

    rejection_reason: Optional[RejectionReason]
    collaboration_id: Optional[UUID]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class CreateCollaborationInteractor:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def execute(
        self, request: CreateCollaborationRequest
    ) -> CreateCollaborationResponse:
        try:
            coordinator = self._validate_request(request)
        except CreateCollaborationResponse.RejectionReason as reason:
            return CreateCollaborationResponse(
                rejection_reason=reason, collaboration_id=None
            )
        account = self.database_gateway.create_account()
        collaboration = self.database_gateway.create_collaboration(
            self.datetime_service.now(),
            request.name,
            request.definition,
            account.id,
        )
        self.database_gateway.create_coordination_tenure(
            company=coordinator.id,
            collaboration=collaboration.id,
            start_date=self.datetime_service.now(),
        )
        return CreateCollaborationResponse(
            rejection_reason=None, collaboration_id=collaboration.id
        )

    def _validate_request(self, request: CreateCollaborationRequest) -> Company:
        coordinator = (
            self.database_gateway.get_companies()
            .with_id(request.coordinator_id)
            .first()
        )
        collabs_with_requested_name = (
            self.database_gateway.get_collaborations().with_name_ignoring_case(
                request.name
            )
        )
        if coordinator is None:
            raise CreateCollaborationResponse.RejectionReason.coordinator_not_found
        if collabs_with_requested_name:
            raise CreateCollaborationResponse.RejectionReason.collaboration_with_name_exists
        return coordinator
