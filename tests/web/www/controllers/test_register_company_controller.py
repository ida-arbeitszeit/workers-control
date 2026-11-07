from tests.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.register_company import RegisterCompany
from workers_control.web.forms import RegisterForm
from workers_control.web.www.controllers.register_company_controller import (
    RegisterCompanyController,
)


class RegisterCompanyControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterCompanyController)

    def test_that_no_interactor_request_is_created_when_form_is_invalid(self) -> None:
        result = self.controller.create_request(create_request(email="invalid_email"))
        assert not isinstance(result, RegisterCompany.Request)

    def test_that_form_with_errors_is_returned_when_form_is_invalid(self) -> None:
        result = self.controller.create_request(create_request(email="invalid_email"))
        assert isinstance(result, RegisterForm)
        assert result.email_errors

    def test_that_valid_email_from_form_is_used_in_interactor_request(self) -> None:
        expected_emails = ["test@cp.org", "other@cp.org"]
        for expected_email in expected_emails:
            result = self.controller.create_request(
                create_request(email=expected_email)
            )
            assert isinstance(result, RegisterCompany.Request)
            assert result.email == expected_email

    def test_that_name_from_form_is_used_in_interactor_request(self) -> None:
        expected_names = ["testname123", "other name"]
        for expected_name in expected_names:
            result = self.controller.create_request(create_request(name=expected_name))
            assert isinstance(result, RegisterCompany.Request)
            assert result.name == expected_name

    def test_that_password_from_form_is_use_in_interactor_request(self) -> None:
        expected_passwords = ["admin123", "password"]
        for expected_password in expected_passwords:
            result = self.controller.create_request(
                create_request(password=expected_password)
            )
            assert isinstance(result, RegisterCompany.Request)
            assert result.password == expected_password


def create_request(
    *,
    email: str = "test@test.test",
    name: str = "testname",
    password: str = "testpassword",
) -> FakeRequest:
    request = FakeRequest()
    request.set_form("email", email)
    request.set_form("name", name)
    request.set_form("password", password)
    request.set_form("repeat_password", password)
    return request
