from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.control_thresholds import ControlThresholds
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway
from workers_control.core.transfers import TransferType


class RejectionReason(Exception, Enum):
    basic_service_not_found = auto()
    consumer_does_not_exist = auto()
    insufficient_balance = auto()
    consumer_is_provider = auto()


@dataclass
class RegisterPrivateConsumptionOfBasicServiceRequest:
    consumer: UUID
    basic_service: UUID
    amount: Decimal


@dataclass
class RegisterPrivateConsumptionOfBasicServiceResponse:
    rejection_reason: Optional[RejectionReason]

    @property
    def is_accepted(self) -> bool:
        return self.rejection_reason is None


@dataclass
class RegisterPrivateConsumptionOfBasicServiceInteractor:
    control_thresholds: ControlThresholds
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def execute(
        self, request: RegisterPrivateConsumptionOfBasicServiceRequest
    ) -> RegisterPrivateConsumptionOfBasicServiceResponse:
        try:
            return self._perform_registration(request)
        except RejectionReason as reason:
            return RegisterPrivateConsumptionOfBasicServiceResponse(
                rejection_reason=reason
            )

    def _perform_registration(
        self, request: RegisterPrivateConsumptionOfBasicServiceRequest
    ) -> RegisterPrivateConsumptionOfBasicServiceResponse:
        basic_service = (
            self.database_gateway.get_basic_services()
            .with_id(request.basic_service)
            .first()
        )
        if basic_service is None:
            raise RejectionReason.basic_service_not_found
        consumer = self.database_gateway.get_members().with_id(request.consumer).first()
        if consumer is None:
            raise RejectionReason.consumer_does_not_exist
        if consumer.id == basic_service.provider:
            raise RejectionReason.consumer_is_provider
        provider = (
            self.database_gateway.get_members().with_id(basic_service.provider).first()
        )
        assert provider
        if not self._is_account_balance_sufficient(request.amount, consumer.account):
            raise RejectionReason.insufficient_balance
        transfer = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=consumer.account,
            credit_account=provider.account,
            value=request.amount,
            type=TransferType.private_consumption_of_basic_service,
        )
        self.database_gateway.create_private_consumption_of_basic_service(
            basic_service=basic_service.id,
            transfer=transfer.id,
        )
        return RegisterPrivateConsumptionOfBasicServiceResponse(rejection_reason=None)

    def _is_account_balance_sufficient(
        self, transfer_value: Decimal, account: UUID
    ) -> bool:
        if transfer_value <= 0:
            return True
        allowed_overdraw = (
            self.control_thresholds.get_allowed_overdraw_of_member_account()
        )
        if allowed_overdraw is None:
            return True
        account_balance = self._get_account_balance(account)
        if account_balance is None:
            return False
        if transfer_value > account_balance + allowed_overdraw:
            return False
        return True

    def _get_account_balance(self, account: UUID) -> Optional[Decimal]:
        result = (
            self.database_gateway.get_accounts()
            .with_id(account)
            .joined_with_balance()
            .first()
        )
        if result:
            return result[1]
        else:
            return None
