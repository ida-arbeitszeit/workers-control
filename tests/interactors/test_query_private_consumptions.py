from datetime import timedelta
from decimal import Decimal

from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors.query_private_consumptions import (
    ConsumptionType,
    QueryPrivateConsumptions,
    Request,
)


class TestQueryPrivateConsumptions(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_consumptions = self.injector.get(QueryPrivateConsumptions)
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)

    def test_that_no_consumption_is_returned_when_searching_an_empty_repo(self) -> None:
        member = self.member_generator.create_member()
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert not response.consumptions

    def test_that_correct_consumptions_are_returned(self) -> None:
        expected_plan = self.plan_generator.create_plan(product_name="my product")
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(
            consumer=member, plan=expected_plan
        )
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert len(response.consumptions) == 1
        assert response.consumptions[0].name == "my product"

    def test_that_plan_consumption_has_consumption_type_plan(self) -> None:
        plan = self.plan_generator.create_plan()
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(
            consumer=member, plan=plan
        )
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert response.consumptions[0].consumption_type == ConsumptionType.plan

    def test_that_basic_service_consumption_is_returned(self) -> None:
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member, amount=Decimal("3")
        )
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert len(response.consumptions) == 1
        consumption = response.consumptions[0]
        assert consumption.consumption_type == ConsumptionType.basic_service
        assert consumption.paid_price_total == Decimal("3")

    def test_that_basic_service_consumption_includes_name_and_description_of_basic_service(
        self,
    ) -> None:
        bs = self.basic_service_generator.create_basic_service(
            name="My Service", description="My service description"
        )
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member, basic_service=bs
        )
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert response.consumptions[0].name == "My Service"
        assert response.consumptions[0].description == "My service description"

    def test_that_plan_and_basic_service_consumptions_are_both_returned(self) -> None:
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(consumer=member)
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member
        )
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert len(response.consumptions) == 2
        types = {c.consumption_type for c in response.consumptions}
        assert types == {ConsumptionType.plan, ConsumptionType.basic_service}

    def test_that_consumptions_are_returned_in_correct_order(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        first_plan = self.plan_generator.create_plan(product_name="first")
        second_plan = self.plan_generator.create_plan(product_name="second")
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(
            consumer=member, plan=first_plan
        )
        self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(
            consumer=member, plan=second_plan
        )
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert response.consumptions[0].name == "second"
        assert response.consumptions[1].name == "first"

    def test_that_mixed_consumptions_are_ordered_by_date_descending(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(consumer=member)
        self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member
        )
        response = self.query_consumptions.query_private_consumptions(
            Request(member=member)
        )
        assert (
            response.consumptions[0].consumption_type == ConsumptionType.basic_service
        )
        assert response.consumptions[1].consumption_type == ConsumptionType.plan
