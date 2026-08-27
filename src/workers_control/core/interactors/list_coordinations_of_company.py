from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


@dataclass
class ListCoordinationsOfCompanyRequest:
    company: UUID


@dataclass
class CollaborationInfo:
    id: UUID
    creation_date: datetime
    name: str
    definition: str
    count_plans_in_collab: int


@dataclass
class ListCoordinationsOfCompanyResponse:
    coordinations: List[CollaborationInfo]


@dataclass
class ListCoordinationsOfCompanyInteractor:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def execute(
        self, request: ListCoordinationsOfCompanyRequest
    ) -> ListCoordinationsOfCompanyResponse:
        if not self.database_gateway.get_companies().with_id(request.company):
            return ListCoordinationsOfCompanyResponse(coordinations=[])
        now = self.datetime_service.now()
        collaborations = [
            CollaborationInfo(
                id=collab.id,
                creation_date=collab.creation_date,
                name=collab.name,
                definition=collab.definition,
                count_plans_in_collab=len(
                    self.database_gateway.get_plans()
                    .that_are_part_of_collaboration(collab.id)
                    .that_will_expire_after(now)
                ),
            )
            for collab in self.database_gateway.get_collaborations().coordinated_by_company(
                request.company
            )
        ]

        return ListCoordinationsOfCompanyResponse(coordinations=collaborations)
