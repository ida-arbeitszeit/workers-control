from dataclasses import dataclass
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


@dataclass
class Request:
    plan_id: UUID | None
    amount: int | None


@dataclass
class NoPlanResponse:
    amount: int | None


@dataclass
class InvalidPlanResponse:
    amount: int | None


@dataclass
class ValidPlanResponse:
    plan_id: UUID
    amount: int | None
    plan_name: str
    plan_description: str


@dataclass
class SelectPrivateConsumptionInteractor:
    database: DatabaseGateway
    datetime_service: DatetimeService

    def select_private_consumption(
        self, request: Request
    ) -> NoPlanResponse | InvalidPlanResponse | ValidPlanResponse:
        amount = request.amount
        if not request.plan_id:
            return NoPlanResponse(amount=amount)
        plan_result = (
            self.database.get_plans()
            .with_id(request.plan_id)
            .that_will_expire_after(self.datetime_service.now())
        )
        if not plan_result:
            return InvalidPlanResponse(amount=amount)
        plan = plan_result.first()
        assert plan
        return ValidPlanResponse(
            plan_id=request.plan_id,
            amount=amount,
            plan_name=plan.prd_name,
            plan_description=plan.description,
        )
