from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from uuid import UUID

from workers_control.core.interactors.select_productive_consumption_of_basic_service import (
    Request as InteractorRequest,
)
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator


@dataclass
class SelectProductiveConsumptionOfBasicServiceController:
    class InputDataError(Exception):
        pass

    notifier: Notifier
    translator: Translator

    def process_input_data(self, request: Request) -> InteractorRequest:
        basic_service_id = self._process_basic_service_id(request)
        amount = self._process_amount(request)
        return InteractorRequest(basic_service_id=basic_service_id, amount=amount)

    def _process_basic_service_id(self, request: Request) -> UUID | None:
        from_query = request.query_string().get_last_value("basic_service_id")
        from_form = request.get_form("basic_service_id")
        if not from_query and not from_form:
            return None
        elif from_query:
            return self._convert_string_to_uuid(from_query)
        else:
            assert from_form
            return self._convert_string_to_uuid(from_form)

    def _convert_string_to_uuid(self, input_string: str) -> UUID:
        try:
            return UUID(input_string)
        except ValueError:
            self.notifier.display_warning(
                self.translator.gettext(
                    "The provided basic service ID is not a valid UUID."
                )
            )
            raise self.InputDataError()

    def _process_amount(self, request: Request) -> Decimal | None:
        from_query = request.query_string().get_last_value("amount")
        from_form = request.get_form("amount")
        if not from_query and not from_form:
            return None
        elif from_query:
            return self._convert_string_to_decimal(from_query)
        else:
            assert from_form
            return self._convert_string_to_decimal(from_form)

    def _convert_string_to_decimal(self, input_string: str) -> Decimal:
        try:
            return Decimal(input_string)
        except InvalidOperation:
            self.notifier.display_warning(
                self.translator.gettext("The provided amount is not a valid number.")
            )
            raise self.InputDataError()
