from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.select_private_consumption import (
    Request as InteractorRequest,
)
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator


@dataclass
class SelectPrivateConsumptionController:
    class InputDataError(Exception):
        pass

    notifier: Notifier
    translator: Translator

    def process_input_data(self, request: Request) -> InteractorRequest:
        plan_id = self._process_plan_id(request)
        amount = self._process_amount(request)
        return InteractorRequest(plan_id=plan_id, amount=amount)

    def _process_plan_id(self, request: Request) -> UUID | None:
        plan_id_from_query_string = request.query_string().get_last_value("plan_id")
        plan_id_from_form = request.get_form("plan_id")
        if not plan_id_from_query_string and not plan_id_from_form:
            return None
        elif plan_id_from_query_string:
            return self._convert_string_to_uuid(plan_id_from_query_string)
        else:
            assert plan_id_from_form
            return self._convert_string_to_uuid(plan_id_from_form)

    def _convert_string_to_uuid(self, input_string: str) -> UUID:
        try:
            return UUID(input_string)
        except ValueError:
            self.notifier.display_warning(
                self.translator.gettext("The provided plan ID is not a valid UUID.")
            )
            raise self.InputDataError()

    def _process_amount(self, request: Request) -> int | None:
        amount_from_query_string = request.query_string().get_last_value("amount")
        amount_from_form = request.get_form("amount")
        if not amount_from_query_string and not amount_from_form:
            return None
        elif amount_from_query_string:
            return self._convert_string_to_int(amount_from_query_string)
        else:
            assert amount_from_form
            return self._convert_string_to_int(amount_from_form)

    def _convert_string_to_int(self, input_string: str) -> int:
        try:
            return int(input_string)
        except ValueError:
            self.notifier.display_warning(
                self.translator.gettext("The provided amount is not a valid integer.")
            )
            raise self.InputDataError()
