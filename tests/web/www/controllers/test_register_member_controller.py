from tests.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.register_member import RegisterMemberInteractor
from workers_control.web.forms import RegisterForm
from workers_control.web.www.controllers.register_member_controller import (
    RegisterMemberController,
)


class RegisterMemberControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterMemberController)

    def test_that_no_interactor_request_is_created_when_form_is_invalid(self) -> None:
        result = self.controller.create_request(create_request(email="invalid_email"))
        assert not isinstance(result, RegisterMemberInteractor.Request)

    def test_that_form_with_errors_is_returned_when_form_is_invalid(self) -> None:
        result = self.controller.create_request(create_request(email="invalid_email"))
        assert isinstance(result, RegisterForm)
        assert result.email_errors

    def test_that_strings_are_taken_as_literal_strings_in_request(
        self,
    ) -> None:
        result = self.controller.create_request(
            create_request(email="user@cp.org", name="test_name", password="very_safe"),
        )
        assert isinstance(result, RegisterMemberInteractor.Request)
        self.assertEqual(result.email, "user@cp.org")
        self.assertEqual(result.name, "test_name")
        self.assertEqual(result.password, "very_safe")


def create_request(
    *,
    email: str = "someone@cp.org",
    name: str = "Someone",
    password: str = "super_safe_pw",
) -> FakeRequest:
    request = FakeRequest()
    request.set_form("email", email)
    request.set_form("name", name)
    request.set_form("password", password)
    request.set_form("repeat_password", password)
    return request
