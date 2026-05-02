from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.records import SocialAccounting
from workers_control.core.repositories import DatabaseGateway
from workers_control.core.services.payout_factor import PayoutFactorService
from workers_control.core.transfers import TransferType


class RejectionReason(Exception, Enum):
    basic_service_not_found = auto()


@dataclass
class Request:
    consumer: UUID
    basic_service: UUID
    amount: Decimal


@dataclass
class Response:
    rejection_reason: Optional[RejectionReason]

    @property
    def is_accepted(self) -> bool:
        return self.rejection_reason is None


@dataclass
class RegisterProductiveConsumptionOfBasicServiceInteractor:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway
    payout_factor_service: PayoutFactorService
    social_accounting: SocialAccounting

    def execute(self, request: Request) -> Response:
        try:
            return self._perform_registration(request)
        except RejectionReason as reason:
            return Response(rejection_reason=reason)

    def _perform_registration(self, request: Request) -> Response:
        basic_service = (
            self.database_gateway.get_basic_services()
            .with_id(request.basic_service)
            .first()
        )
        if not basic_service:
            raise RejectionReason.basic_service_not_found
        consumer = (
            self.database_gateway.get_companies().with_id(request.consumer).first()
        )
        assert consumer
        provider = (
            self.database_gateway.get_members().with_id(basic_service.provider).first()
        )
        assert provider
        now = self.datetime_service.now()
        fic = self.payout_factor_service.calculate_current_payout_factor()
        transfer_of_consumption = self.database_gateway.create_transfer(
            date=now,
            debit_account=consumer.raw_material_account,
            credit_account=provider.account,
            value=request.amount,
            type=TransferType.productive_consumption_of_basic_service,
        )
        transfer_of_taxes = self.database_gateway.create_transfer(
            date=now,
            debit_account=provider.account,
            credit_account=self.social_accounting.account_psf,
            value=request.amount * (Decimal(1) - fic),
            type=TransferType.taxes,
        )
        self.database_gateway.create_productive_consumption_of_basic_service(
            basic_service=basic_service.id,
            transfer_of_consumption=transfer_of_consumption.id,
            transfer_of_taxes=transfer_of_taxes.id,
        )
        return Response(rejection_reason=None)
