from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
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
    datetime_service: DatetimeService

    @dataclass
    class Request:
        collaboration: UUID
        requester: UUID

    @dataclass
    class Response:
        coordinations: list[CoordinationInfo]
        collaboration_id: UUID
        collaboration_name: str
        requester_is_involved: bool

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
        _, current_coordinator = tenures_and_coordinators[0]

        return self.Response(
            coordinations=coordinations,
            collaboration_id=request.collaboration,
            collaboration_name=collaboration.name,
            requester_is_involved=current_coordinator.id == request.requester
            or self._has_active_plan_in_collaboration(
                request.requester, request.collaboration
            ),
        )

    def _has_active_plan_in_collaboration(
        self, planner: UUID, collaboration: UUID
    ) -> bool:
        return bool(
            self.database_gateway.get_plans()
            .that_are_part_of_collaboration(collaboration)
            .that_will_expire_after(self.datetime_service.now())
            .planned_by(planner)
        )
