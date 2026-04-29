from decimal import Decimal
from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors import (
    register_productive_consumption_of_basic_service,
)
from workers_control.web.www.controllers.register_productive_consumption_of_basic_service_controller import (
    FormError,
    ImportFormDataResult,
    RegisterProductiveConsumptionOfBasicServiceController,
)


class RegisterProductiveConsumptionOfBasicServiceControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(
            RegisterProductiveConsumptionOfBasicServiceController
        )
        self.session.login_company(uuid4())

    def test_form_error_when_basic_service_id_and_amount_are_empty(self) -> None:
        result = self._process_form(basic_service_id="", amount="")
        assert isinstance(result, FormError)

    def test_amount_error_message_when_amount_is_empty(self) -> None:
        result = self._process_form(amount="")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("You must specify an amount.")
        ]

    def test_form_error_when_basic_service_id_is_empty(self) -> None:
        result = self._process_form(basic_service_id="")
        assert isinstance(result, FormError)

    def test_form_error_when_basic_service_id_is_not_a_valid_uuid(self) -> None:
        result = self._process_form(basic_service_id="1872da")
        assert isinstance(result, FormError)

    def test_form_error_when_amount_is_negative(self) -> None:
        result = self._process_form(amount="-1")
        assert isinstance(result, FormError)

    def test_form_error_when_amount_is_zero(self) -> None:
        result = self._process_form(amount="0")
        assert isinstance(result, FormError)

    def test_form_error_when_amount_contains_letters(self) -> None:
        result = self._process_form(amount="1a")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("This is not a valid number.")
        ]

    def test_basic_service_id_error_message_for_empty_string(self) -> None:
        result = self._process_form(basic_service_id="", amount="")
        assert isinstance(result, FormError)
        assert result.form.basic_service_id_errors == [
            self.translator.gettext("Basic service ID is invalid.")
        ]

    def test_basic_service_id_error_message_for_invalid_uuid(self) -> None:
        result = self._process_form(basic_service_id="aa18781hh")
        assert isinstance(result, FormError)
        assert result.form.basic_service_id_errors == [
            self.translator.gettext("Basic service ID is invalid.")
        ]

    def test_amount_error_message_for_negative_amount(self) -> None:
        result = self._process_form(amount="-1")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("Must be a number larger than zero.")
        ]

    def test_both_field_errors_present_when_both_empty(self) -> None:
        result = self._process_form(amount="", basic_service_id="")
        assert isinstance(result, FormError)
        assert result.form.basic_service_id_errors
        assert result.form.amount_errors

    @parameterized.expand([("1",), ("1.5",), ("0.25",)])
    def test_decimal_amount_is_accepted_and_returned(self, amount: str) -> None:
        result = self._process_form(amount=amount)
        assert isinstance(
            result, register_productive_consumption_of_basic_service.Request
        )
        assert result.amount == Decimal(amount)

    def test_correct_basic_service_uuid_is_returned(self) -> None:
        bs_uuid = uuid4()
        result = self._process_form(basic_service_id=str(bs_uuid))
        assert isinstance(
            result, register_productive_consumption_of_basic_service.Request
        )
        assert result.basic_service == bs_uuid

    def test_consumer_from_session_is_returned(self) -> None:
        consumer = uuid4()
        self.session.login_company(consumer)
        result = self._process_form()
        assert isinstance(
            result, register_productive_consumption_of_basic_service.Request
        )
        assert result.consumer == consumer

    def _process_form(
        self,
        basic_service_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> ImportFormDataResult:
        request = FakeRequest()
        if basic_service_id is None:
            request.set_form("basic_service_id", str(uuid4()))
        else:
            request.set_form("basic_service_id", basic_service_id)
        if amount is None:
            request.set_form("amount", "1")
        else:
            request.set_form("amount", amount)
        return self.controller.import_form_data(request=request)
