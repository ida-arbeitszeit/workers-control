from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from workers_control.core.interactors import (
    register_productive_consumption_of_basic_service,
)
from workers_control.core.records import SocialAccounting, Transfer
from workers_control.core.transfers import TransferType

from ..datetime_service import datetime_utc
from .base_test_case import BaseTestCase


class RegisterProductiveConsumptionOfBasicServiceTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            register_productive_consumption_of_basic_service.RegisterProductiveConsumptionOfBasicServiceInteractor
        )
        self.social_accounting = self.injector.get(SocialAccounting)
        self.consumer = self.company_generator.create_company()

    def test_registration_fails_when_basic_service_does_not_exist(self) -> None:
        response = self.interactor.execute(self.make_request(uuid4()))
        assert not response.is_accepted
        assert (
            response.rejection_reason
            == register_productive_consumption_of_basic_service.RejectionReason.basic_service_not_found
        )

    def test_registration_succeeds_when_basic_service_exists(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        response = self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        assert response.is_accepted
        assert response.rejection_reason is None

    def test_successful_registration_creates_exactly_one_transfer_of_correct_type(
        self,
    ) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfers = self.get_basic_service_consumption_transfers()
        assert len(transfers) == 1
        assert transfers[0].type == TransferType.productive_consumption_of_basic_service

    def test_transfer_debits_consumer_raw_material_account(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        consumer = self.database_gateway.get_companies().with_id(self.consumer).first()
        assert consumer
        assert transfer.debit_account == consumer.raw_material_account

    def test_transfer_credits_provider_account(self) -> None:
        provider = self.member_generator.create_member()
        bs = self.basic_service_generator.create_basic_service(member=provider)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        provider_record = self.database_gateway.get_members().with_id(provider).first()
        assert provider_record
        assert transfer.credit_account == provider_record.account

    def test_transfer_value_equals_request_amount(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1.5")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        assert transfer.value == Decimal("1.5")

    def test_transfer_date_equals_now(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2026, 1, 1))
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        transfer = self.get_basic_service_consumption_transfers()[0]
        assert transfer.date == self.datetime_service.now()

    def test_multiple_registrations_create_multiple_transfers(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        assert len(self.get_basic_service_consumption_transfers()) == 3

    def test_successful_registration_creates_productive_consumption_record(
        self,
    ) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        consumption_transfer = self.get_basic_service_consumption_transfers()[0]
        tax_transfer = self.get_tax_transfers()[0]
        records = list(
            self.database_gateway.get_productive_consumptions_of_basic_service()
        )
        assert len(records) == 1
        assert records[0].basic_service == bs
        assert records[0].transfer_of_consumption == consumption_transfer.id
        assert records[0].transfer_of_taxes == tax_transfer.id

    def test_successful_consumption_creates_tax_transfer_of_correct_type(
        self,
    ) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        tax_transfers = self.get_tax_transfers()
        assert len(tax_transfers) == 1

    def test_tax_transfer_debits_provider_account(self) -> None:
        provider = self.member_generator.create_member()
        bs = self.basic_service_generator.create_basic_service(member=provider)
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        tax_transfer = self.get_tax_transfers()[0]
        provider_record = self.database_gateway.get_members().with_id(provider).first()
        assert provider_record
        assert tax_transfer.debit_account == provider_record.account

    def test_tax_transfer_credits_psf_account(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("1")))
        tax_transfer = self.get_tax_transfers()[0]
        assert tax_transfer.credit_account == self.social_accounting.account_psf

    def test_with_fic_of_one_no_taxes_are_deducted(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("3")))
        tax_transfer = self.get_tax_transfers()[0]
        assert tax_transfer.value == Decimal(0)

    def test_with_fic_of_one_half_tax_value_is_half_of_amount(self) -> None:
        self.economic_scenarios.setup_environment_with_fic(Decimal("0.5"))
        bs = self.basic_service_generator.create_basic_service()
        self.interactor.execute(self.make_request(bs, amount=Decimal("3")))
        tax_transfer = self.get_tax_transfers()[0]
        assert tax_transfer.value == Decimal("1.5")

    def test_no_tax_transfer_is_created_when_basic_service_does_not_exist(self) -> None:
        self.interactor.execute(self.make_request(uuid4()))
        assert not self.get_tax_transfers()

    def make_request(
        self,
        basic_service: UUID,
        amount: Decimal = Decimal("1"),
        consumer: UUID | None = None,
    ) -> register_productive_consumption_of_basic_service.Request:
        if consumer is None:
            consumer = self.consumer
        return register_productive_consumption_of_basic_service.Request(
            consumer=consumer,
            basic_service=basic_service,
            amount=amount,
        )

    def get_basic_service_consumption_transfers(self) -> list[Transfer]:
        return [
            t
            for t in self.database_gateway.get_transfers()
            if t.type == TransferType.productive_consumption_of_basic_service
        ]

    def get_tax_transfers(self) -> list[Transfer]:
        return [
            t
            for t in self.database_gateway.get_transfers()
            if t.type == TransferType.taxes
        ]
