from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from workers_control.core.interactors.register_private_consumption_of_basic_service import (
    RegisterPrivateConsumptionOfBasicServiceInteractor,
    RegisterPrivateConsumptionOfBasicServiceRequest,
    RejectionReason,
)
from workers_control.core.records import Transfer
from workers_control.core.transfers import TransferType

from .base_test_case import BaseTestCase


class RegisterPrivateConsumptionOfBasicServiceTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            RegisterPrivateConsumptionOfBasicServiceInteractor
        )
        self.consumer = self.member_generator.create_member()

    def test_registration_fails_when_basic_service_does_not_exist(self) -> None:
        response = self.interactor.execute(self.make_request(uuid4()))
        assert not response.is_accepted
        assert response.rejection_reason == RejectionReason.basic_service_not_found

    def test_registration_fails_when_consumer_does_not_exist(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        response = self.interactor.execute(self.make_request(bs, consumer=uuid4()))
        assert not response.is_accepted
        assert response.rejection_reason == RejectionReason.consumer_does_not_exist

    def test_registration_fails_when_consumer_is_provider(self) -> None:
        bs = self.basic_service_generator.create_basic_service(member=self.consumer)
        response = self.interactor.execute(self.make_request(bs))
        assert not response.is_accepted
        assert response.rejection_reason == RejectionReason.consumer_is_provider

    def test_registration_fails_when_consumer_balance_is_insufficient(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        assert self.balance_checker.get_member_account_balance(self.consumer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)
        response = self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        assert not response.is_accepted
        assert response.rejection_reason == RejectionReason.insufficient_balance

    def test_no_transfer_is_created_when_consumer_balance_is_insufficient(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        assert not self.get_basic_service_consumption_transfers()

    def test_registration_succeeds_with_unlimited_overdraw(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)
        response = self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        assert response.is_accepted
        assert response.rejection_reason is None

    def test_successful_registration_creates_exactly_one_transfer_of_correct_type(
        self,
    ) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfers = self.get_basic_service_consumption_transfers()
        assert len(transfers) == 1

    def test_transfer_debits_consumer_account(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        consumer = self.database_gateway.get_members().with_id(self.consumer).first()
        assert consumer
        assert transfer.debit_account == consumer.account

    def test_transfer_credits_provider_account(self) -> None:
        provider = self.member_generator.create_member()
        bs = self.basic_service_generator.create_basic_service(member=provider)
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        provider_record = self.database_gateway.get_members().with_id(provider).first()
        assert provider_record
        assert transfer.credit_account == provider_record.account

    def test_transfer_value_equals_request_amount(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1.5")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        assert transfer.value == Decimal("1.5")

    def test_transfer_date_equals_now(self) -> None:
        self.datetime_service.freeze_time()
        bs = self.basic_service_generator.create_basic_service()
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        assert transfer.date == self.datetime_service.now()

    def test_multiple_registrations_create_multiple_transfers(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        assert len(self.get_basic_service_consumption_transfers()) == 3

    def make_request(
        self,
        basic_service: UUID,
        amount: Decimal = Decimal("1"),
        consumer: UUID | None = None,
    ) -> RegisterPrivateConsumptionOfBasicServiceRequest:
        if consumer is None:
            consumer = self.consumer
        return RegisterPrivateConsumptionOfBasicServiceRequest(
            consumer=consumer,
            basic_service=basic_service,
            amount=amount,
        )

    def get_basic_service_consumption_transfers(self) -> list[Transfer]:
        return [
            t
            for t in self.database_gateway.get_transfers()
            if t.type == TransferType.private_consumption_of_basic_service
        ]
