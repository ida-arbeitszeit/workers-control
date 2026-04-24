from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.web.www.controllers.select_private_consumption_controller import (
    SelectPrivateConsumptionController,
)


class SelectPrivateConsumptionControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(SelectPrivateConsumptionController)

    def test_that_none_is_returned_when_no_plan_id_is_provided(self) -> None:
        request = FakeRequest()
        response = self.controller.process_input_data(request=request)
        assert response.plan_id is None

    def test_that_input_error_is_raised_when_plan_id_is_not_a_valid_uuid(self) -> None:
        request = FakeRequest()
        request.set_arg("plan_id", "not_a_valid_uuid")
        with self.assertRaises(SelectPrivateConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)

    def test_that_a_warning_is_displayed_when_plan_id_is_not_a_valid_uuid(self) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        request.set_arg("plan_id", "not_a_valid_uuid")
        with self.assertRaises(SelectPrivateConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)
        assert self.notifier.warnings

    def test_that_plan_id_from_url_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        plan_id = uuid4()
        request.set_arg("plan_id", str(plan_id))
        response = self.controller.process_input_data(request=request)
        assert response.plan_id == plan_id

    def test_that_plan_id_from_form_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        plan_id = uuid4()
        request.set_form("plan_id", str(plan_id))
        response = self.controller.process_input_data(request=request)
        assert response.plan_id == plan_id

    def test_that_none_is_returned_when_no_amount_is_provided(self) -> None:
        request = FakeRequest()
        response = self.controller.process_input_data(request=request)
        assert response.amount is None

    def test_that_input_error_is_raised_when_amount_is_not_a_valid_number(self) -> None:
        request = FakeRequest()
        request.set_arg("amount", "not_a_valid_number")
        with self.assertRaises(SelectPrivateConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)

    def test_that_a_warning_is_displayed_when_amount_is_not_a_valid_number(
        self,
    ) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        request.set_arg("amount", "not_a_valid_number")
        with self.assertRaises(SelectPrivateConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)
        assert self.notifier.warnings

    def test_that_amount_from_url_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        amount = 10
        request.set_arg("amount", str(amount))
        response = self.controller.process_input_data(request=request)
        assert response.amount == amount

    def test_that_amount_from_form_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        amount = 10
        request.set_form("amount", str(amount))
        response = self.controller.process_input_data(request=request)
        assert response.amount == amount
