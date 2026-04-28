from decimal import Decimal
from uuid import UUID, uuid4

from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors.get_private_consumption_details import (
    GetPrivateConsumptionDetailsInteractor,
)


class TestGetPrivateConsumptionDetails(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetPrivateConsumptionDetailsInteractor)
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)

    def test_that_none_is_returned_for_unknown_consumption_id(self) -> None:
        member = self.member_generator.create_member()
        response = self.interactor.get_details(
            GetPrivateConsumptionDetailsInteractor.Request(
                consumption_id=uuid4(),
                member=member,
            )
        )
        assert response is None

    def test_that_response_is_returned_for_own_plan_consumption(self) -> None:
        member = self.member_generator.create_member()
        plan = self.plan_generator.create_plan(
            product_name="My Product",
            description="A description",
        )
        self.consumption_generator.create_private_consumption(
            consumer=member, plan=plan, amount=2
        )
        consumption_id = self._get_only_private_consumption_id()
        response = self.interactor.get_details(
            GetPrivateConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                member=member,
            )
        )
        assert response is not None
        assert response.plan_id == plan
        assert response.plan_name == "My Product"
        assert response.plan_description == "A description"
        assert response.amount == 2

    def test_that_paid_price_per_unit_is_total_divided_by_amount(self) -> None:
        member = self.member_generator.create_member()
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_private_consumption(
            consumer=member, plan=plan, amount=4
        )
        consumption_id = self._get_only_private_consumption_id()
        response = self.interactor.get_details(
            GetPrivateConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                member=member,
            )
        )
        assert response is not None
        assert response.paid_price_per_unit == response.paid_price_total / Decimal(4)

    def test_that_none_is_returned_when_a_different_member_requests_the_consumption(
        self,
    ) -> None:
        owner = self.member_generator.create_member()
        other = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(consumer=owner)
        consumption_id = self._get_only_private_consumption_id()
        response = self.interactor.get_details(
            GetPrivateConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                member=other,
            )
        )
        assert response is None

    def test_that_none_is_returned_for_a_basic_service_consumption_id(self) -> None:
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member
        )
        bs_consumption = (
            self.database_gateway.get_private_consumptions_of_basic_service().first()
        )
        assert bs_consumption
        response = self.interactor.get_details(
            GetPrivateConsumptionDetailsInteractor.Request(
                consumption_id=bs_consumption.id,
                member=member,
            )
        )
        assert response is None

    def _get_only_private_consumption_id(self) -> UUID:
        consumption = self.database_gateway.get_private_consumptions().first()
        assert consumption
        return consumption.id
