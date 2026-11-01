from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.records import Collaboration, CoordinationTransferRequest
from workers_control.core.repositories import DatabaseGateway


@dataclass
class AcceptCoordinationTransferInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    @dataclass
    class Request:
        transfer_request_id: UUID
        accepting_company: UUID

    @dataclass
    class Response:
        class RejectionReason(Enum):
            transfer_request_not_found = auto()
            transfer_request_closed = auto()
            accepting_company_is_not_candidate = auto()

        rejection_reason: Optional[RejectionReason]
        collaboration_id: Optional[UUID]
        transfer_request_id: UUID

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    def accept_coordination_transfer(self, request: Request) -> Response:
        validation = self._validate_request(request)
        if isinstance(validation, self.Response.RejectionReason):
            return self.Response(
                rejection_reason=validation,
                collaboration_id=None,
                transfer_request_id=request.transfer_request_id,
            )
        transfer_request, collaboration = validation
        collaboration_id = self._create_new_coordination_tenure(
            transfer_request, collaboration
        )
        return self.Response(
            rejection_reason=None,
            collaboration_id=collaboration_id,
            transfer_request_id=request.transfer_request_id,
        )

    def _validate_request(
        self, request: Request
    ) -> tuple[CoordinationTransferRequest, Collaboration] | Response.RejectionReason:
        result = (
            self.database_gateway.get_coordination_transfer_requests()
            .with_id(request.transfer_request_id)
            .joined_with_collaboration()
            .first()
        )
        if result is None:
            return self.Response.RejectionReason.transfer_request_not_found
        transfer_request, collaboration = result
        if transfer_request.candidate != request.accepting_company:
            return self.Response.RejectionReason.accepting_company_is_not_candidate
        if self._collaboration_has_a_coordination_tenure_starting_after_transfer_request(
            collaboration=collaboration, transfer_request=transfer_request
        ):
            return self.Response.RejectionReason.transfer_request_closed
        return transfer_request, collaboration

    def _create_new_coordination_tenure(
        self,
        transfer_request: CoordinationTransferRequest,
        collaboration: Collaboration,
    ) -> UUID:
        new_tenure = self.database_gateway.create_coordination_tenure(
            company=transfer_request.candidate,
            collaboration=collaboration.id,
            start_date=self.datetime_service.now(),
        )
        return new_tenure.collaboration

    def _collaboration_has_a_coordination_tenure_starting_after_transfer_request(
        self,
        transfer_request: CoordinationTransferRequest,
        collaboration: Collaboration,
    ) -> bool:
        latest_coordination_tenure_of_collaboration = (
            self.database_gateway.get_coordination_tenures()
            .of_collaboration(collaboration.id)
            .ordered_by_start_date(ascending=False)
            .first()
        )
        assert latest_coordination_tenure_of_collaboration
        return (
            latest_coordination_tenure_of_collaboration.start_date
            > transfer_request.request_date
        )
