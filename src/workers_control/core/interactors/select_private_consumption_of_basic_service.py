from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class Request:
    basic_service_id: UUID | None
    amount: Decimal | None


@dataclass
class NoBasicServiceResponse:
    amount: Decimal | None


@dataclass
class InvalidBasicServiceResponse:
    amount: Decimal | None


@dataclass
class ValidBasicServiceResponse:
    basic_service_id: UUID
    amount: Decimal | None
    basic_service_name: str
    basic_service_description: str
    provider_name: str


@dataclass
class SelectPrivateConsumptionOfBasicServiceInteractor:
    database: DatabaseGateway

    def select(
        self, request: Request
    ) -> (
        NoBasicServiceResponse | InvalidBasicServiceResponse | ValidBasicServiceResponse
    ):
        amount = request.amount
        if not request.basic_service_id:
            return NoBasicServiceResponse(amount=amount)
        result = (
            self.database.get_basic_services()
            .with_id(request.basic_service_id)
            .joined_with_provider()
            .first()
        )
        if result is None:
            return InvalidBasicServiceResponse(amount=amount)
        basic_service, provider = result
        return ValidBasicServiceResponse(
            basic_service_id=basic_service.id,
            amount=amount,
            basic_service_name=basic_service.name,
            basic_service_description=basic_service.description,
            provider_name=provider.name,
        )
