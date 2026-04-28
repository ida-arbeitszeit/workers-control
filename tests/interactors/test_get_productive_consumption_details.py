from decimal import Decimal
from uuid import UUID, uuid4

from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors.get_productive_consumption_details import (
    GetProductiveConsumptionDetailsInteractor,
)
from workers_control.core.records import ConsumptionType


class TestGetProductiveConsumptionDetails(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetProductiveConsumptionDetailsInteractor)

    def test_that_none_is_returned_for_unknown_consumption_id(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.get_details(
            GetProductiveConsumptionDetailsInteractor.Request(
                consumption_id=uuid4(),
                company=company,
            )
        )
        assert response is None

    def test_that_response_is_returned_for_own_resource_consumption(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            product_name="My Product",
            description="A description",
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company, plan=plan, amount=2
        )
        consumption_id = self._get_only_productive_consumption_id()
        response = self.interactor.get_details(
            GetProductiveConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                company=company,
            )
        )
        assert response is not None
        assert response.plan_id == plan
        assert response.plan_name == "My Product"
        assert response.plan_description == "A description"
        assert response.amount == 2

    def test_that_consumption_type_is_raw_materials_for_resource_consumption(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company
        )
        consumption_id = self._get_only_productive_consumption_id()
        response = self.interactor.get_details(
            GetProductiveConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                company=company,
            )
        )
        assert response is not None
        assert response.consumption_type == ConsumptionType.raw_materials

    def test_that_consumption_type_is_means_of_prod_for_fixed_means_consumption(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.consumption_generator.create_fixed_means_consumption(
            consumer=company,
        )
        consumption_id = self._get_only_productive_consumption_id()
        response = self.interactor.get_details(
            GetProductiveConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                company=company,
            )
        )
        assert response is not None
        assert response.consumption_type == ConsumptionType.means_of_prod

    def test_that_paid_price_per_unit_is_total_divided_by_amount(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company, plan=plan, amount=4
        )
        consumption_id = self._get_only_productive_consumption_id()
        response = self.interactor.get_details(
            GetProductiveConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                company=company,
            )
        )
        assert response is not None
        assert response.paid_price_per_unit == response.paid_price_total / Decimal(4)

    def test_that_none_is_returned_when_a_different_company_requests_the_consumption(
        self,
    ) -> None:
        owner = self.company_generator.create_company()
        other = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=owner
        )
        consumption_id = self._get_only_productive_consumption_id()
        response = self.interactor.get_details(
            GetProductiveConsumptionDetailsInteractor.Request(
                consumption_id=consumption_id,
                company=other,
            )
        )
        assert response is None

    def _get_only_productive_consumption_id(self) -> UUID:
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        return consumption.id
