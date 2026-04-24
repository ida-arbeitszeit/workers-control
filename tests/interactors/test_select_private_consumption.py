from datetime import timedelta
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors import select_private_consumption


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            select_private_consumption.SelectPrivateConsumptionInteractor
        )

    def test_that_no_plan_response_is_returned_when_no_plan_id_is_provided(self):
        request = self.create_request()
        response = self.interactor.select_private_consumption(request)
        assert isinstance(response, select_private_consumption.NoPlanResponse)

    def test_that_invalid_plan_response_is_returned_when_plan_id_is_provided_but_plan_does_not_exist(
        self,
    ):
        request = self.create_request(plan_id=uuid4())
        response = self.interactor.select_private_consumption(request)
        assert isinstance(response, select_private_consumption.InvalidPlanResponse)

    def test_that_invalid_plan_response_is_returned_when_plan_id_is_provided_but_plan_is_not_approved(
        self,
    ):
        plan = self.plan_generator.create_plan(approved=False)
        request = self.create_request(plan_id=plan)
        response = self.interactor.select_private_consumption(request)
        assert isinstance(response, select_private_consumption.InvalidPlanResponse)

    def test_that_invalid_plan_response_is_returned_when_plan_id_is_provided_but_plan_is_expired(
        self,
    ):
        self.datetime_service.freeze_time()
        plan = self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        request = self.create_request(plan_id=plan)
        response = self.interactor.select_private_consumption(request)
        assert isinstance(response, select_private_consumption.InvalidPlanResponse)

    def test_that_valid_plan_response_is_returned_when_plan_id_is_provided_and_plan_exists(
        self,
    ):
        plan = self.plan_generator.create_plan()
        request = self.create_request(plan_id=plan)
        response = self.interactor.select_private_consumption(request)
        assert isinstance(response, select_private_consumption.ValidPlanResponse)

    @parameterized.expand([(None,), (0,), (1,), (2,)])
    def test_that_amount_from_request_is_passed_to_response(self, amount: int | None):
        request = self.create_request(amount=amount)
        response = self.interactor.select_private_consumption(request)
        assert response.amount == amount

    def test_that_plan_id_of_valid_plan_response_is_the_same_as_the_provided_plan_id(
        self,
    ):
        plan = self.plan_generator.create_plan()
        request = self.create_request(plan_id=plan)
        response = self.interactor.select_private_consumption(request)
        assert response.plan_id == plan

    @parameterized.expand([("Plan Name 1",), ("Plan Name 2",)])
    def test_that_plan_name_of_valid_plan_response_is_the_same_as_the_provided_plan_name(
        self, plan_name: str
    ):
        plan = self.plan_generator.create_plan(product_name=plan_name)
        request = self.create_request(plan_id=plan)
        response = self.interactor.select_private_consumption(request)
        assert isinstance(response, select_private_consumption.ValidPlanResponse)
        assert response.plan_name == plan_name

    @parameterized.expand([("Plan Description 1",), ("Plan Description 2",)])
    def test_that_plan_description_of_valid_plan_response_is_the_same_as_the_provided_plan_description(
        self, plan_description: str
    ):
        plan = self.plan_generator.create_plan(description=plan_description)
        request = self.create_request(plan_id=plan)
        response = self.interactor.select_private_consumption(request)
        assert isinstance(response, select_private_consumption.ValidPlanResponse)
        assert response.plan_description == plan_description

    def create_request(
        self,
        plan_id: UUID | None = None,
        amount: int | None = None,
    ) -> select_private_consumption.Request:
        return select_private_consumption.Request(plan_id=plan_id, amount=amount)
