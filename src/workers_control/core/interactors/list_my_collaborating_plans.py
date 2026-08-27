from __future__ import annotations

from dataclasses import dataclass
from typing import List
from uuid import UUID

from workers_control.core import records
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


@dataclass
class ListMyCollaboratingPlansInteractor:
    @dataclass
    class Request:
        company: UUID

    @dataclass
    class CollaboratingPlan:
        plan_id: UUID
        plan_name: str
        collab_id: UUID
        collab_name: str

    @dataclass
    class Response:
        collaborating_plans: List[ListMyCollaboratingPlansInteractor.CollaboratingPlan]

    class Failure(Exception):
        pass

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def list_collaborations(self, request: Request) -> Response:
        if not self.database_gateway.get_companies().with_id(request.company):
            raise self.Failure()
        now = self.datetime_service.now()
        plans = (
            self.database_gateway.get_plans()
            .that_will_expire_after(now)
            .that_were_approved_before(now)
            .planned_by(request.company)
            .that_are_collaborating()
        )
        return self.Response(
            collaborating_plans=[
                self._create_plan_object(plan, collaboration)
                for plan, collaboration in plans.joined_with_collaboration()
                if collaboration
            ]
        )

    def _create_plan_object(
        self, plan: records.Plan, collaboration: records.Collaboration
    ) -> CollaboratingPlan:
        return self.CollaboratingPlan(
            plan_id=plan.id,
            plan_name=plan.prd_name,
            collab_id=collaboration.id,
            collab_name=collaboration.name,
        )
