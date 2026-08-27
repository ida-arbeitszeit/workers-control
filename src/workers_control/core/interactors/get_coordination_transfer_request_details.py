from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from workers_control.core.records import Collaboration, CoordinationTransferRequest
from workers_control.core.repositories import DatabaseGateway


@dataclass
class GetCoordinationTransferRequestDetailsInteractor:
    @dataclass
    class Request:
        coordination_transfer_request: UUID

    @dataclass
    class Response:
        request_date: datetime
        collaboration_id: UUID
        collaboration_name: str
        candidate_id: UUID
        candidate_name: str
        request_is_pending: bool

    database_gateway: DatabaseGateway

    def get_details(self, request: Request) -> Optional[Response]:
        transfer_request_and_collaboration = (
            self.database_gateway.get_coordination_transfer_requests()
            .with_id(request.coordination_transfer_request)
            .joined_with_collaboration()
            .first()
        )
        if not transfer_request_and_collaboration:
            return None
        transfer_request, collaboration = transfer_request_and_collaboration
        candidate = (
            self.database_gateway.get_companies()
            .with_id(transfer_request.candidate)
            .first()
        )
        assert candidate
        return self.Response(
            request_date=transfer_request.request_date,
            collaboration_id=collaboration.id,
            collaboration_name=collaboration.name,
            candidate_id=transfer_request.candidate,
            candidate_name=candidate.name,
            request_is_pending=not self._collaboration_has_a_coordination_tenure_starting_after_transfer_request(
                transfer_request=transfer_request, collaboration=collaboration
            ),
        )

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
