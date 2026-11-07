from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.web.forms import RegisterForm
from workers_control.web.www.controllers.register_form_validator import (
    RegisterFormData,
    RegisterFormValidator,
)


class RegisterFormValidatorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.validator = self.injector.get(RegisterFormValidator)

    def test_that_valid_form_data_is_returned_for_valid_input(self) -> None:
        request = create_request(
            email="test@cp.org", name="test name", password="test_password"
        )
        assert self.validator.validate(request) == RegisterFormData(
            email="test@cp.org", name="test name", password="test_password"
        )

    def test_that_missing_fields_are_rejected(self) -> None:
        assert isinstance(self.validator.validate(FakeRequest()), RegisterForm)

    @parameterized.expand([("invalid_email",), ("",), ("a@b",)])
    def test_that_form_with_invalid_email_is_rejected(self, email: str) -> None:
        request = create_request(email=email)
        assert isinstance(self.validator.validate(request), RegisterForm)

    def test_that_error_is_attached_to_email_field_when_email_is_invalid(
        self,
    ) -> None:
        form = self.validate_invalid(create_request(email="invalid_email"))
        assert form.email_errors == [
            self.translator.gettext("Proper email address required")
        ]

    def test_that_form_with_empty_name_is_rejected(self) -> None:
        request = create_request(name="")
        assert isinstance(self.validator.validate(request), RegisterForm)

    def test_that_error_is_attached_to_name_field_when_name_is_empty(self) -> None:
        form = self.validate_invalid(create_request(name=""))
        assert form.name_errors == [self.translator.gettext("Name is required")]

    def test_that_form_with_password_of_seven_characters_is_rejected(self) -> None:
        request = create_request(password="1234567")
        assert isinstance(self.validator.validate(request), RegisterForm)

    def test_that_form_with_password_of_eight_characters_is_accepted(self) -> None:
        request = create_request(password="12345678")
        assert isinstance(self.validator.validate(request), RegisterFormData)

    def test_that_error_is_attached_to_password_field_when_password_is_too_short(
        self,
    ) -> None:
        form = self.validate_invalid(create_request(password="short"))
        assert form.password_errors == [
            self.translator.gettext(
                "The password must be at least 8 characters in length"
            )
        ]

    def test_that_form_with_different_repeated_password_is_rejected(self) -> None:
        request = create_request(
            password="test_password", repeat_password="other_password"
        )
        assert isinstance(self.validator.validate(request), RegisterForm)

    def test_that_error_is_attached_to_repeat_password_field_when_passwords_do_not_match(
        self,
    ) -> None:
        form = self.validate_invalid(
            create_request(password="test_password", repeat_password="other_password")
        )
        assert form.repeat_password_errors == [
            self.translator.gettext("Passwords must match")
        ]
        assert not form.password_errors

    def test_that_errors_are_attached_to_all_invalid_fields(self) -> None:
        form = self.validate_invalid(
            create_request(
                email="invalid_email",
                name="",
                password="short",
                repeat_password="other",
            )
        )
        assert form.email_errors
        assert form.name_errors
        assert form.password_errors
        assert form.repeat_password_errors

    def test_that_entered_email_and_name_are_kept_in_rejected_form(self) -> None:
        form = self.validate_invalid(
            create_request(email="test@cp.org", name="test name", password="short")
        )
        assert form.email_value == "test@cp.org"
        assert form.name_value == "test name"

    def validate_invalid(self, request: FakeRequest) -> RegisterForm:
        result = self.validator.validate(request)
        assert isinstance(result, RegisterForm)
        return result


def create_request(
    *,
    email: str = "test@test.test",
    name: str = "testname",
    password: str = "testpassword",
    repeat_password: str | None = None,
) -> FakeRequest:
    request = FakeRequest()
    request.set_form("email", email)
    request.set_form("name", name)
    request.set_form("password", password)
    request.set_form(
        "repeat_password", password if repeat_password is None else repeat_password
    )
    return request
