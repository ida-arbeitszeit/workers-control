from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from uuid import UUID

from workers_control.core.records import (
    BasicService,
    Plan,
    PrivateConsumption,
    PrivateConsumptionOfBasicService,
    Transfer,
)
from workers_control.core.repositories import DatabaseGateway


class ConsumptionType(Enum):
    plan = auto()
    basic_service = auto()


@dataclass
class Consumption:
    id: UUID
    consumption_type: ConsumptionType
    consumption_date: datetime
    name: str
    description: str
    paid_price_total: Decimal


@dataclass
class Response:
    consumptions: list[Consumption]


@dataclass
class Request:
    member: UUID


@dataclass
class QueryPrivateConsumptions:
    database_gateway: DatabaseGateway

    def query_private_consumptions(self, request: Request) -> Response:
        consumptions = [
            self._plan_consumption_to_response_model(consumption, transfer, plan)
            for consumption, transfer, plan in (
                self.database_gateway.get_private_consumptions()
                .where_consumer_is_member(member=request.member)
                .joined_with_transfer_and_plan()
            )
        ]
        consumptions.extend(
            self._basic_service_consumption_to_response_model(
                consumption, transfer, basic_service
            )
            for consumption, transfer, basic_service in (
                self.database_gateway.get_private_consumptions_of_basic_service()
                .where_consumer_is_member(member=request.member)
                .joined_with_transfer_and_basic_service()
            )
        )
        consumptions.sort(key=lambda c: c.consumption_date, reverse=True)
        return Response(consumptions=consumptions)

    def _plan_consumption_to_response_model(
        self, consumption: PrivateConsumption, transfer: Transfer, plan: Plan
    ) -> Consumption:
        return Consumption(
            id=consumption.id,
            consumption_type=ConsumptionType.plan,
            consumption_date=transfer.date,
            name=plan.prd_name,
            description=plan.description,
            paid_price_total=transfer.value,
        )

    def _basic_service_consumption_to_response_model(
        self,
        consumption: PrivateConsumptionOfBasicService,
        transfer: Transfer,
        basic_service: BasicService,
    ) -> Consumption:
        return Consumption(
            id=consumption.id,
            consumption_type=ConsumptionType.basic_service,
            consumption_date=transfer.date,
            name=basic_service.name,
            description=basic_service.description,
            paid_price_total=transfer.value,
        )
