from dataclasses import dataclass

from workers_control.core.email import is_possibly_an_email_address
from workers_control.web.forms import RegisterForm
from workers_control.web.translator import Translator

MINIMUM_PASSWORD_LENGTH = 8


@dataclass
class RegisterFormValidator:
    translator: Translator

    def validate(self, form: RegisterForm) -> bool:
        is_valid = True
        if not is_possibly_an_email_address(form.email_field.get_value()):
            form.email_field.attach_error(
                self.translator.gettext("Proper email address required")
            )
            is_valid = False
        if not form.name_field.get_value():
            form.name_field.attach_error(self.translator.gettext("Name is required"))
            is_valid = False
        password = form.password_field.get_value()
        if len(password) < MINIMUM_PASSWORD_LENGTH:
            form.password_field.attach_error(
                self.translator.gettext(
                    "The password must be at least 8 characters in length"
                )
            )
            is_valid = False
        if password != form.repeat_password_field.get_value():
            form.password_field.attach_error(
                self.translator.gettext("Passwords must match")
            )
            is_valid = False
        return is_valid
