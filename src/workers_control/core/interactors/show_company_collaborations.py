from dataclasses import dataclass
from typing import List
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.records import Plan
from workers_control.core.repositories import DatabaseGateway


@dataclass
class Request:
    company: UUID


@dataclass
class InboundCollabRequest:
    collab_id: UUID
    collab_name: str
    plan_id: UUID
    plan_name: str
    planner_name: str
    planner_id: UUID


@dataclass
class OutboundCollabRequest:
    plan_id: UUID
    plan_name: str
    collab_id: UUID
    collab_name: str


@dataclass
class Response:
    inbound_collaboration_requests: List[InboundCollabRequest]
    outbound_collaboration_requests: List[OutboundCollabRequest]


@dataclass
class ShowCompanyCollaborationsInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def show_company_collaborations(self, request: Request) -> Response:
        now = self.datetime_service.now()
        inbound_collaboration_requests = [
            self._plan_to_inbound_collab_request(plan)
            for plan in self.database_gateway.get_plans()
            .that_request_collaboration_with_coordinator(request.company)
            .that_will_expire_after(now)
        ]
        plans_with_open_requests = (
            self.database_gateway.get_plans()
            .planned_by(request.company)
            .with_open_collaboration_request()
            .that_will_expire_after(now)
        )
        outbound_collaboration_requests = [
            self._plan_to_outbound_collab_request(plan)
            for plan in plans_with_open_requests
        ]
        return Response(
            inbound_collaboration_requests=inbound_collaboration_requests,
            outbound_collaboration_requests=outbound_collaboration_requests,
        )

    def _plan_to_outbound_collab_request(self, plan: Plan) -> OutboundCollabRequest:
        assert plan.requested_collaboration
        requested_collaboration = (
            self.database_gateway.get_collaborations()
            .with_id(plan.requested_collaboration)
            .first()
        )
        assert requested_collaboration
        return OutboundCollabRequest(
            plan_id=plan.id,
            plan_name=plan.prd_name,
            collab_id=plan.requested_collaboration,
            collab_name=requested_collaboration.name,
        )

    def _company_exists(self, request: Request) -> bool:
        return bool(self.database_gateway.get_companies().with_id(request.company))

    def _plan_to_inbound_collab_request(self, plan: Plan) -> InboundCollabRequest:
        assert plan.requested_collaboration
        requested_collaboration = (
            self.database_gateway.get_collaborations()
            .with_id(plan.requested_collaboration)
            .first()
        )
        assert requested_collaboration
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        return InboundCollabRequest(
            collab_id=plan.requested_collaboration,
            collab_name=requested_collaboration.name,
            plan_id=plan.id,
            plan_name=plan.prd_name,
            planner_name=planner.name,
            planner_id=planner.id,
        )
