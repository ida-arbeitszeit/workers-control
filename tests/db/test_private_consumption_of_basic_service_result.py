from decimal import Decimal

from tests.control_thresholds import ControlThresholdsTestImpl
from tests.db.base_test_case import DatabaseTestCase


class PrivateConsumptionOfBasicServiceTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)

    def test_that_by_default_no_consumptions_of_basic_service_are_in_db(self) -> None:
        assert not self.database_gateway.get_private_consumptions_of_basic_service()

    def test_that_a_consumption_is_in_db_after_one_was_created(self) -> None:
        self.consumption_generator.create_private_consumption_of_basic_service()
        assert self.database_gateway.get_private_consumptions_of_basic_service()

    def test_that_retrieved_consumption_references_the_specified_basic_service(
        self,
    ) -> None:
        basic_service = self.basic_service_generator.create_basic_service()
        self.consumption_generator.create_private_consumption_of_basic_service(
            basic_service=basic_service
        )
        consumption = (
            self.database_gateway.get_private_consumptions_of_basic_service().first()
        )
        assert consumption
        assert consumption.basic_service == basic_service

    def test_that_retrieved_consumption_references_an_existing_transfer(self) -> None:
        self.consumption_generator.create_private_consumption_of_basic_service()
        consumption = (
            self.database_gateway.get_private_consumptions_of_basic_service().first()
        )
        assert consumption
        transfer_ids = {t.id for t in self.database_gateway.get_transfers()}
        assert consumption.transfer_of_consumption in transfer_ids
        assert consumption.transfer_of_taxes in transfer_ids

    def test_that_two_different_consumptions_reference_different_transfers(
        self,
    ) -> None:
        self.consumption_generator.create_private_consumption_of_basic_service()
        self.consumption_generator.create_private_consumption_of_basic_service()
        consumption_1, consumption_2 = list(
            self.database_gateway.get_private_consumptions_of_basic_service()
        )
        assert (
            consumption_1.transfer_of_consumption
            != consumption_2.transfer_of_consumption
        )

    def test_can_filter_consumptions_by_consumer(self) -> None:
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member
        )
        consumptions = self.database_gateway.get_private_consumptions_of_basic_service()
        assert consumptions.where_consumer_is_member(member)
        assert not consumptions.where_consumer_is_member(other_member)

    def test_can_retrieve_basic_service_and_transfer_with_consumption(self) -> None:
        self.consumption_generator.create_private_consumption_of_basic_service()
        result = (
            self.database_gateway.get_private_consumptions_of_basic_service()
            .joined_with_transfer_and_basic_service()
            .first()
        )
        assert result
        consumption, transfer, basic_service = result
        assert consumption.transfer_of_consumption == transfer.id
        assert consumption.basic_service == basic_service.id

    def test_that_amount_of_transfer_equals_amount_specified_when_creating_the_consumption(
        self,
    ) -> None:
        expected_amount = Decimal("5")
        self.consumption_generator.create_private_consumption_of_basic_service(
            amount=expected_amount
        )
        result = (
            self.database_gateway.get_private_consumptions_of_basic_service()
            .joined_with_transfer_and_basic_service()
            .first()
        )
        assert result
        _, transfer, _ = result
        assert transfer.value == expected_amount

    def test_can_combine_filtering_and_joining_of_consumptions_with_transfer_and_basic_service(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member
        )
        assert (
            self.database_gateway.get_private_consumptions_of_basic_service()
            .where_consumer_is_member(member)
            .joined_with_transfer_and_basic_service()
        )

    def test_can_retrieve_transfer_with_consumption(self) -> None:
        self.consumption_generator.create_private_consumption_of_basic_service()
        result = (
            self.database_gateway.get_private_consumptions_of_basic_service()
            .joined_with_transfer()
            .first()
        )
        assert result
        consumption, transfer = result
        assert consumption.transfer_of_consumption == transfer.id

    def test_that_amount_of_transfer_from_join_with_transfer_equals_amount_specified_when_creating_the_consumption(
        self,
    ) -> None:
        expected_amount = Decimal("5")
        self.consumption_generator.create_private_consumption_of_basic_service(
            amount=expected_amount
        )
        result = (
            self.database_gateway.get_private_consumptions_of_basic_service()
            .joined_with_transfer()
            .first()
        )
        assert result
        _, transfer = result
        assert transfer.value == expected_amount

    def test_can_combine_filtering_and_joining_of_consumptions_with_transfer(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member
        )
        assert (
            self.database_gateway.get_private_consumptions_of_basic_service()
            .where_consumer_is_member(member)
            .joined_with_transfer()
        )
