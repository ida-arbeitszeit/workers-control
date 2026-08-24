from dataclasses import dataclass
from typing import List
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.records import Collaboration
from workers_control.core.repositories import DatabaseGateway


@dataclass
class ListedCollaboration:
    id: UUID
    name: str
    plan_count: int


@dataclass
class ListAllCollaborationsResponse:
    collaborations: List[ListedCollaboration]


@dataclass
class ListAllCollaborationsInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(self) -> ListAllCollaborationsResponse:
        all_collaborations = self.database_gateway.get_collaborations()
        if not all_collaborations:
            return ListAllCollaborationsResponse(collaborations=[])
        collaborations = [
            self._collab_to_response_model(collab) for collab in all_collaborations
        ]
        return ListAllCollaborationsResponse(collaborations=collaborations)

    def _collab_to_response_model(self, collab: Collaboration) -> ListedCollaboration:
        now = self.datetime_service.now()
        plan_count = len(
            self.database_gateway.get_plans()
            .that_are_part_of_collaboration(collab.id)
            .that_will_expire_after(now)
        )
        return ListedCollaboration(
            id=collab.id, name=collab.name, plan_count=plan_count
        )
