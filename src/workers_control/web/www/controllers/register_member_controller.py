from dataclasses import dataclass

from workers_control.core.interactors.register_member import RegisterMemberInteractor
from workers_control.web.forms import RegisterForm
from workers_control.web.request import Request
from workers_control.web.www.controllers.register_form_validator import (
    RegisterFormData,
    RegisterFormValidator,
)


@dataclass
class RegisterMemberController:
    validator: RegisterFormValidator

    def create_request(
        self, request: Request
    ) -> RegisterMemberInteractor.Request | RegisterForm:
        match self.validator.validate(request):
            case RegisterForm() as form:
                return form
            case RegisterFormData(email=email, name=name, password=password):
                return RegisterMemberInteractor.Request(
                    email=email, name=name, password=password
                )
