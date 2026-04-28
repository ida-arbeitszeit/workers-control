from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class GetPrivateConsumptionDetailsInteractor:
    @dataclass
    class Request:
        consumption_id: UUID
        member: UUID

    @dataclass
    class Response:
        consumption_date: datetime
        plan_id: UUID
        plan_name: str
        plan_description: str
        amount: int
        paid_price_per_unit: Decimal
        paid_price_total: Decimal

    database_gateway: DatabaseGateway

    def get_details(self, request: Request) -> Optional[Response]:
        row = (
            self.database_gateway.get_private_consumptions()
            .with_id(request.consumption_id)
            .where_consumer_is_member(member=request.member)
            .joined_with_transfer_and_plan()
            .first()
        )
        if not row:
            return None
        consumption, transfer, plan = row
        return self.Response(
            consumption_date=transfer.date,
            plan_id=plan.id,
            plan_name=plan.prd_name,
            plan_description=plan.description,
            amount=consumption.amount,
            paid_price_per_unit=transfer.value / consumption.amount,
            paid_price_total=transfer.value,
        )
