from decimal import Decimal
from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.web.www.controllers.select_private_consumption_of_basic_service_controller import (
    SelectPrivateConsumptionOfBasicServiceController,
)


class SelectPrivateConsumptionOfBasicServiceControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(
            SelectPrivateConsumptionOfBasicServiceController
        )

    def test_none_is_returned_when_no_basic_service_id_is_provided(self) -> None:
        request = FakeRequest()
        response = self.controller.process_input_data(request=request)
        assert response.basic_service_id is None

    def test_input_error_is_raised_when_basic_service_id_is_not_a_valid_uuid(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_arg("basic_service_id", "not_a_valid_uuid")
        with self.assertRaises(
            SelectPrivateConsumptionOfBasicServiceController.InputDataError
        ):
            self.controller.process_input_data(request=request)

    def test_warning_is_displayed_when_basic_service_id_is_not_a_valid_uuid(
        self,
    ) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        request.set_arg("basic_service_id", "not_a_valid_uuid")
        with self.assertRaises(
            SelectPrivateConsumptionOfBasicServiceController.InputDataError
        ):
            self.controller.process_input_data(request=request)
        assert self.notifier.warnings

    def test_basic_service_id_from_query_string_is_returned(self) -> None:
        request = FakeRequest()
        bs_id = uuid4()
        request.set_arg("basic_service_id", str(bs_id))
        response = self.controller.process_input_data(request=request)
        assert response.basic_service_id == bs_id

    def test_basic_service_id_from_form_is_returned(self) -> None:
        request = FakeRequest()
        bs_id = uuid4()
        request.set_form("basic_service_id", str(bs_id))
        response = self.controller.process_input_data(request=request)
        assert response.basic_service_id == bs_id

    def test_none_is_returned_when_no_amount_is_provided(self) -> None:
        request = FakeRequest()
        response = self.controller.process_input_data(request=request)
        assert response.amount is None

    def test_input_error_is_raised_when_amount_is_not_a_valid_number(self) -> None:
        request = FakeRequest()
        request.set_arg("amount", "not_a_valid_number")
        with self.assertRaises(
            SelectPrivateConsumptionOfBasicServiceController.InputDataError
        ):
            self.controller.process_input_data(request=request)

    def test_warning_is_displayed_when_amount_is_not_a_valid_number(self) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        request.set_arg("amount", "not_a_valid_number")
        with self.assertRaises(
            SelectPrivateConsumptionOfBasicServiceController.InputDataError
        ):
            self.controller.process_input_data(request=request)
        assert self.notifier.warnings

    def test_decimal_amount_from_query_string_is_returned(self) -> None:
        request = FakeRequest()
        request.set_arg("amount", "1.5")
        response = self.controller.process_input_data(request=request)
        assert response.amount == Decimal("1.5")

    def test_decimal_amount_from_form_is_returned(self) -> None:
        request = FakeRequest()
        request.set_form("amount", "2.25")
        response = self.controller.process_input_data(request=request)
        assert response.amount == Decimal("2.25")
