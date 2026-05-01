from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.records import (
    BasicService,
    Company,
    Plan,
    ProductiveConsumption,
    ProductiveConsumptionOfBasicService,
    Transfer,
)
from workers_control.core.repositories import DatabaseGateway


class ConsumptionKind(Enum):
    plan_with_means_of_prod = auto()
    plan_with_raw_materials = auto()
    basic_service = auto()


@dataclass
class Consumption:
    id: UUID
    consumption_date: datetime
    plan_id: Optional[UUID]
    product_name: str
    product_description: str
    kind: ConsumptionKind
    paid_price_total: Decimal


@dataclass
class Response:
    consumptions: list[Consumption]


@dataclass
class QueryCompanyConsumptionsInteractor:
    database_gateway: DatabaseGateway

    def execute(
        self,
        company: UUID,
    ) -> Response:
        company_record = self.database_gateway.get_companies().with_id(company).first()
        assert company_record
        consumptions: list[Consumption] = [
            self._plan_consumption_to_response_model(
                consumption, transfer, plan, company_record
            )
            for consumption, transfer, plan in (
                self.database_gateway.get_productive_consumptions()
                .where_consumer_is_company(company=company)
                .joined_with_transfer_and_plan()
            )
        ]
        consumptions.extend(
            self._basic_service_consumption_to_response_model(
                consumption, transfer, basic_service
            )
            for consumption, transfer, basic_service in (
                self.database_gateway.get_productive_consumptions_of_basic_service()
                .where_consumer_is_company(company=company)
                .joined_with_transfer_and_basic_service()
            )
        )
        consumptions.sort(key=lambda r: r.consumption_date, reverse=True)
        return Response(consumptions=consumptions)

    def _plan_consumption_to_response_model(
        self,
        consumption: ProductiveConsumption,
        transfer: Transfer,
        plan: Plan,
        company: Company,
    ) -> Consumption:
        if transfer.debit_account == company.raw_material_account:
            kind = ConsumptionKind.plan_with_raw_materials
        else:
            kind = ConsumptionKind.plan_with_means_of_prod
        return Consumption(
            id=consumption.id,
            consumption_date=transfer.date,
            plan_id=plan.id,
            product_name=plan.prd_name,
            product_description=plan.description,
            kind=kind,
            paid_price_total=transfer.value,
        )

    def _basic_service_consumption_to_response_model(
        self,
        consumption: ProductiveConsumptionOfBasicService,
        transfer: Transfer,
        basic_service: BasicService,
    ) -> Consumption:
        return Consumption(
            id=consumption.id,
            consumption_date=transfer.date,
            plan_id=None,
            product_name=basic_service.name,
            product_description=basic_service.description,
            kind=ConsumptionKind.basic_service,
            paid_price_total=transfer.value,
        )
