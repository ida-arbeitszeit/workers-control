from dataclasses import dataclass

from workers_control.core.email import is_possibly_an_email_address
from workers_control.web.forms import RegisterForm
from workers_control.web.request import Request
from workers_control.web.translator import Translator

MINIMUM_PASSWORD_LENGTH = 8


@dataclass
class RegisterFormData:
    email: str
    name: str
    password: str


@dataclass
class RegisterFormValidator:
    translator: Translator

    def validate(self, request: Request) -> RegisterFormData | RegisterForm:
        email = request.get_form("email") or ""
        name = request.get_form("name") or ""
        password = request.get_form("password") or ""
        repeat_password = request.get_form("repeat_password") or ""
        form = RegisterForm(email_value=email, name_value=name)
        if not is_possibly_an_email_address(email):
            form.email_errors.append(
                self.translator.gettext("Proper email address required")
            )
        if not name:
            form.name_errors.append(self.translator.gettext("Name is required"))
        if len(password) < MINIMUM_PASSWORD_LENGTH:
            form.password_errors.append(
                self.translator.gettext(
                    "The password must be at least 8 characters in length"
                )
            )
        if password != repeat_password:
            form.repeat_password_errors.append(
                self.translator.gettext("Passwords must match")
            )
        if (
            form.email_errors
            or form.name_errors
            or form.password_errors
            or form.repeat_password_errors
        ):
            return form
        return RegisterFormData(email=email, name=name, password=password)
