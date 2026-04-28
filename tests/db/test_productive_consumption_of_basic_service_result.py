from decimal import Decimal
from typing import Optional
from uuid import UUID

from tests.db.base_test_case import DatabaseTestCase
from workers_control.core import records
from workers_control.core.transfers import TransferType


class ProductiveConsumptionOfBasicServiceTests(DatabaseTestCase):
    def _create_consumption(
        self,
        *,
        consumer: Optional[records.Company] = None,
        basic_service: Optional[UUID] = None,
        amount: Decimal = Decimal(1),
    ) -> records.ProductiveConsumptionOfBasicService:
        if consumer is None:
            consumer = self.company_generator.create_company_record()
        if basic_service is None:
            basic_service = self.basic_service_generator.create_basic_service()
        provider_id = (
            self.database_gateway.get_basic_services().with_id(basic_service).first()
        )
        assert provider_id
        provider = (
            self.database_gateway.get_members().with_id(provider_id.provider).first()
        )
        assert provider
        transfer = self.transfer_generator.create_transfer(
            debit_account=consumer.raw_material_account,
            credit_account=provider.account,
            value=amount,
            type=TransferType.productive_consumption_of_basic_service,
        )
        return self.database_gateway.create_productive_consumption_of_basic_service(
            basic_service=basic_service,
            transfer=transfer.id,
        )

    def test_that_by_default_no_consumptions_of_basic_service_are_in_db(self) -> None:
        assert not self.database_gateway.get_productive_consumptions_of_basic_service()

    def test_that_a_consumption_is_in_db_after_one_was_created(self) -> None:
        self._create_consumption()
        assert self.database_gateway.get_productive_consumptions_of_basic_service()

    def test_that_retrieved_consumption_references_the_specified_basic_service(
        self,
    ) -> None:
        basic_service = self.basic_service_generator.create_basic_service()
        self._create_consumption(basic_service=basic_service)
        consumption = (
            self.database_gateway.get_productive_consumptions_of_basic_service().first()
        )
        assert consumption
        assert consumption.basic_service == basic_service

    def test_that_retrieved_consumption_references_an_existing_transfer(self) -> None:
        self._create_consumption()
        consumption = (
            self.database_gateway.get_productive_consumptions_of_basic_service().first()
        )
        assert consumption
        transfer_ids = {t.id for t in self.database_gateway.get_transfers()}
        assert consumption.transfer in transfer_ids

    def test_that_two_different_consumptions_reference_different_transfers(
        self,
    ) -> None:
        self._create_consumption()
        self._create_consumption()
        consumption_1, consumption_2 = list(
            self.database_gateway.get_productive_consumptions_of_basic_service()
        )
        assert consumption_1.transfer != consumption_2.transfer

    def test_can_filter_consumptions_by_consumer(self) -> None:
        company = self.company_generator.create_company_record()
        other_company = self.company_generator.create_company_record()
        self._create_consumption(consumer=company)
        consumptions = (
            self.database_gateway.get_productive_consumptions_of_basic_service()
        )
        assert consumptions.where_consumer_is_company(company.id)
        assert not consumptions.where_consumer_is_company(other_company.id)

    def test_can_retrieve_basic_service_and_transfer_with_consumption(self) -> None:
        self._create_consumption()
        result = (
            self.database_gateway.get_productive_consumptions_of_basic_service()
            .joined_with_transfer_and_basic_service()
            .first()
        )
        assert result
        consumption, transfer, basic_service = result
        assert consumption.transfer == transfer.id
        assert consumption.basic_service == basic_service.id

    def test_that_amount_of_transfer_equals_amount_specified_when_creating_the_consumption(
        self,
    ) -> None:
        expected_amount = Decimal("5")
        self._create_consumption(amount=expected_amount)
        result = (
            self.database_gateway.get_productive_consumptions_of_basic_service()
            .joined_with_transfer_and_basic_service()
            .first()
        )
        assert result
        _, transfer, _ = result
        assert transfer.value == expected_amount

    def test_can_combine_filtering_and_joining_of_consumptions_with_transfer_and_basic_service(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self._create_consumption(consumer=company)
        assert (
            self.database_gateway.get_productive_consumptions_of_basic_service()
            .where_consumer_is_company(company.id)
            .joined_with_transfer_and_basic_service()
        )
