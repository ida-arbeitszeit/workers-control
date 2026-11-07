from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from tests.web.www.forms import RegisterFormImpl
from workers_control.web.www.controllers.register_form_validator import (
    RegisterFormValidator,
)


class RegisterFormValidatorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.validator = self.injector.get(RegisterFormValidator)

    def test_that_valid_form_is_accepted(self) -> None:
        form = RegisterFormImpl.create()
        assert self.validator.validate(form)

    def test_that_no_errors_are_attached_to_valid_form(self) -> None:
        form = RegisterFormImpl.create()
        self.validator.validate(form)
        assert not form.errors()

    @parameterized.expand([("invalid_email",), ("",), ("a@b",)])
    def test_that_form_with_invalid_email_is_rejected(self, email: str) -> None:
        form = RegisterFormImpl.create(email=email)
        assert not self.validator.validate(form)

    def test_that_error_is_attached_to_email_field_when_email_is_invalid(
        self,
    ) -> None:
        form = RegisterFormImpl.create(email="invalid_email")
        self.validator.validate(form)
        assert form.email_field.errors == [
            self.translator.gettext("Proper email address required")
        ]

    def test_that_form_with_empty_name_is_rejected(self) -> None:
        form = RegisterFormImpl.create(name="")
        assert not self.validator.validate(form)

    def test_that_error_is_attached_to_name_field_when_name_is_empty(self) -> None:
        form = RegisterFormImpl.create(name="")
        self.validator.validate(form)
        assert form.name_field.errors == [self.translator.gettext("Name is required")]

    def test_that_form_with_password_of_seven_characters_is_rejected(self) -> None:
        form = RegisterFormImpl.create(password="1234567")
        assert not self.validator.validate(form)

    def test_that_form_with_password_of_eight_characters_is_accepted(self) -> None:
        form = RegisterFormImpl.create(password="12345678")
        assert self.validator.validate(form)

    def test_that_error_is_attached_to_password_field_when_password_is_too_short(
        self,
    ) -> None:
        form = RegisterFormImpl.create(password="short")
        self.validator.validate(form)
        assert form.password_field.errors == [
            self.translator.gettext(
                "The password must be at least 8 characters in length"
            )
        ]

    def test_that_form_with_different_repeated_password_is_rejected(self) -> None:
        form = RegisterFormImpl.create(
            password="test_password", repeat_password="other_password"
        )
        assert not self.validator.validate(form)

    def test_that_error_is_attached_to_password_field_when_passwords_do_not_match(
        self,
    ) -> None:
        form = RegisterFormImpl.create(
            password="test_password", repeat_password="other_password"
        )
        self.validator.validate(form)
        assert form.password_field.errors == [
            self.translator.gettext("Passwords must match")
        ]

    def test_that_errors_are_attached_to_all_invalid_fields(self) -> None:
        form = RegisterFormImpl.create(
            email="invalid_email", name="", password="short", repeat_password="other"
        )
        self.validator.validate(form)
        assert form.email_field.errors
        assert form.name_field.errors
        assert len(form.password_field.errors) == 2
