from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class GetPlanForReviewInteractor:
    @dataclass
    class Request:
        plan: UUID

    @dataclass
    class Response:
        plan_id: UUID
        product_name: str

    database_gateway: DatabaseGateway

    def get_plan_for_review(self, request: Request) -> Response | None:
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        if plan is None:
            return None
        return self.Response(plan_id=plan.id, product_name=plan.prd_name)
