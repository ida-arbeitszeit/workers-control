from dataclasses import dataclass

from workers_control.core.interactors.register_member import RegisterMemberInteractor
from workers_control.web.forms import RegisterForm
from workers_control.web.www.controllers.register_form_validator import (
    RegisterFormValidator,
)


@dataclass
class RegisterMemberController:
    validator: RegisterFormValidator

    def create_request(
        self, form: RegisterForm
    ) -> RegisterMemberInteractor.Request | None:
        if not self.validator.validate(form):
            return None
        return RegisterMemberInteractor.Request(
            email=form.email_field.get_value(),
            name=form.name_field.get_value(),
            password=form.password_field.get_value(),
        )
