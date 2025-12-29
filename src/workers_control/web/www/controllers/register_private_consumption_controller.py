from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.register_private_consumption import (
    RegisterPrivateConsumptionRequest,
)
from workers_control.web.forms import RegisterPrivateConsumptionForm
from workers_control.web.request import Request
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.controllers.register_private_consumption_form_validator import (
    RegisterPrivateConsumptionFormValidator as Validator,
)
from workers_control.web.www.response import Redirect


@dataclass
class FormError:
    form: RegisterPrivateConsumptionForm


ViewModel = RegisterPrivateConsumptionRequest | Redirect | FormError


@dataclass
class RegisterPrivateConsumptionController:
    translator: Translator
    session: Session
    url_index: UrlIndex
    validator: Validator

    def import_form_data(self, request: Request) -> ViewModel:
        plan_id: UUID
        amount: int
        plan_id_errors: list[str] = []
        amount_errors: list[str] = []
        match self.validator.validate_plan_id_string(request.get_form("plan_id") or ""):
            case UUID() as plan_id:
                pass
            case list() as plan_id_errors:
                pass
        match self.validator.validate_amount_string(request.get_form("amount") or ""):
            case int() as amount:
                pass
            case list() as amount_errors:
                pass
        if plan_id_errors or amount_errors:
            return self.create_form_error(
                request, amount_errors=amount_errors, plan_id_errors=plan_id_errors
            )
        match self.session.get_current_user():
            case None:
                return Redirect(url=self.url_index.get_member_login_url())
            case UUID() as user_id:
                return RegisterPrivateConsumptionRequest(
                    consumer=user_id, plan=plan_id, amount=amount
                )

    def create_form_error(
        self,
        request: Request,
        *,
        plan_id_errors: list[str] | None = None,
        amount_errors: list[str] | None = None,
    ) -> FormError:
        if plan_id_errors is None:
            plan_id_errors = []
        if amount_errors is None:
            amount_errors = []
        return FormError(
            form=RegisterPrivateConsumptionForm(
                plan_id_value=request.get_form("plan_id") or "",
                plan_id_errors=plan_id_errors,
                amount_value=request.get_form("amount") or "",
                amount_errors=amount_errors,
            )
        )
