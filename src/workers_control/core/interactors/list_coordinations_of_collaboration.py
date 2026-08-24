from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class CoordinationInfo:
    coordinator_id: UUID
    coordinator_name: str
    start_time: datetime
    end_time: Optional[datetime]


@dataclass
class ListCoordinationsOfCollaborationInteractor:
    database_gateway: DatabaseGateway

    @dataclass
    class Request:
        collaboration: UUID

    @dataclass
    class Response:
        coordinations: list[CoordinationInfo]
        collaboration_id: UUID
        collaboration_name: str

    def list_coordinations(self, request: Request) -> Response:
        tenures_and_coordinators = list(
            self.database_gateway.get_coordination_tenures()
            .of_collaboration(request.collaboration)
            .ordered_by_start_date(ascending=False)
            .joined_with_coordinator()
        )
        coordinations: list[CoordinationInfo] = []
        end_timestamp = None
        for tenure, coordinator in tenures_and_coordinators:
            coordinations.append(
                CoordinationInfo(
                    coordinator_id=coordinator.id,
                    coordinator_name=coordinator.name,
                    start_time=tenure.start_date,
                    end_time=end_timestamp,
                )
            )
            end_timestamp = tenure.start_date
        assert coordinations  # there cannot be a collaboration without at least one coordination_tenure
        collaboration = (
            self.database_gateway.get_collaborations()
            .with_id(request.collaboration)
            .first()
        )
        assert collaboration

        return self.Response(
            coordinations=coordinations,
            collaboration_id=request.collaboration,
            collaboration_name=collaboration.name,
        )
