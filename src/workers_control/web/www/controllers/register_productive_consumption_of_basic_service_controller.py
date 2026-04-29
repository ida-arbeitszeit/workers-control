from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from workers_control.core.interactors import (
    register_productive_consumption_of_basic_service,
)
from workers_control.web.forms import RegisterProductiveConsumptionOfBasicServiceForm
from workers_control.web.request import Request
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.www.controllers.register_productive_consumption_of_basic_service_form_validator import (
    RegisterProductiveConsumptionOfBasicServiceFormValidator as Validator,
)


@dataclass
class FormError:
    form: RegisterProductiveConsumptionOfBasicServiceForm


ImportFormDataResult = (
    register_productive_consumption_of_basic_service.Request | FormError
)


@dataclass
class RegisterProductiveConsumptionOfBasicServiceController:
    translator: Translator
    session: Session
    validator: Validator

    def import_form_data(self, request: Request) -> ImportFormDataResult:
        basic_service_id: UUID
        amount: Decimal
        basic_service_id_errors: list[str] = []
        amount_errors: list[str] = []
        match self.validator.validate_basic_service_id_string(
            request.get_form("basic_service_id") or ""
        ):
            case UUID() as basic_service_id:
                pass
            case list() as basic_service_id_errors:
                pass
        match self.validator.validate_amount_string(request.get_form("amount") or ""):
            case Decimal() as amount:
                pass
            case list() as amount_errors:
                pass
        if basic_service_id_errors or amount_errors:
            return self.create_form_error(
                request,
                basic_service_id_errors=basic_service_id_errors,
                amount_errors=amount_errors,
            )
        consumer = self.session.get_current_user()
        assert consumer
        return register_productive_consumption_of_basic_service.Request(
            consumer=consumer,
            basic_service=basic_service_id,
            amount=amount,
        )

    def create_form_error(
        self,
        request: Request,
        *,
        basic_service_id_errors: list[str] | None = None,
        amount_errors: list[str] | None = None,
    ) -> FormError:
        if basic_service_id_errors is None:
            basic_service_id_errors = []
        if amount_errors is None:
            amount_errors = []
        return FormError(
            form=RegisterProductiveConsumptionOfBasicServiceForm(
                basic_service_id_value=request.get_form("basic_service_id") or "",
                basic_service_id_errors=basic_service_id_errors,
                amount_value=request.get_form("amount") or "",
                amount_errors=amount_errors,
            )
        )
