from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.records import Plan
from workers_control.core.repositories import DatabaseGateway
from workers_control.core.services.price_calculator import PriceCalculator


@dataclass
class GetCollabSummaryRequest:
    requester_id: UUID
    collab_id: UUID


@dataclass
class AssociatedPlan:
    plan_id: UUID
    plan_name: str
    plan_individual_price: Decimal
    planner_id: UUID
    planner_name: str
    requester_is_planner: bool


@dataclass
class GetCollabSummaryResponse:
    requester_is_coordinator: bool
    collab_id: UUID
    collab_name: str
    collab_definition: str
    current_coordinator: UUID
    current_coordinator_name: str
    collab_price: Optional[Decimal]
    plans: List[AssociatedPlan]


@dataclass
class GetCollabSummaryInteractor:
    database_gateway: DatabaseGateway
    price_calculator: PriceCalculator
    datetime_service: DatetimeService

    def execute(
        self, request: GetCollabSummaryRequest
    ) -> Optional[GetCollabSummaryResponse]:
        collab_and_coordinator = (
            self.database_gateway.get_collaborations()
            .with_id(request.collab_id)
            .joined_with_current_coordinator()
            .first()
        )
        if collab_and_coordinator is None:
            return None
        collab, coordinator = collab_and_coordinator
        now = self.datetime_service.now()
        plan_result = (
            self.database_gateway.get_plans()
            .that_are_part_of_collaboration(request.collab_id)
            .that_will_expire_after(now)
        )
        plans = list(plan_result)
        return GetCollabSummaryResponse(
            requester_is_coordinator=coordinator.id == request.requester_id,
            collab_id=collab.id,
            collab_name=collab.name,
            collab_definition=collab.definition,
            current_coordinator=coordinator.id,
            current_coordinator_name=coordinator.name,
            collab_price=self._get_collaborative_price(plans),
            plans=self._get_associated_plans(plans, request.requester_id),
        )

    def _get_planner_name(self, planner_id: UUID) -> str:
        planner = self.database_gateway.get_companies().with_id(planner_id).first()
        assert planner
        return planner.name

    def _get_collaborative_price(self, plans: list[Plan]) -> Optional[Decimal]:
        if not plans:
            return None
        return self.price_calculator.calculate_price(plans[0].id)

    def _get_associated_plans(
        self, plans: list[Plan], requester: UUID
    ) -> list[AssociatedPlan]:
        return [
            AssociatedPlan(
                plan_id=plan.id,
                plan_name=plan.prd_name,
                plan_individual_price=plan.cost_per_unit(),
                planner_id=plan.planner,
                planner_name=self._get_planner_name(plan.planner),
                requester_is_planner=plan.planner == requester,
            )
            for plan in plans
        ]
