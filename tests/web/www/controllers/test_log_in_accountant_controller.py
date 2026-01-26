from tests.web.base_test_case import BaseTestCase
from tests.web.www.forms import LoginForm
from workers_control.web.www.controllers.log_in_accountant_controller import (
    LogInAccountantController,
)


class ControllerTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.form = LoginForm()
        self.controller = self.injector.get(LogInAccountantController)

    def test_that_email_address_is_taken_from_form(self) -> None:
        expected_email = "test@mail.test"
        form = LoginForm(email_value=expected_email)
        request = self.controller.process_login_form(form)
        self.assertEqual(request.email_address, expected_email)

    def test_that_password_is_taken_from_form(self) -> None:
        expected_password = "test password 123"
        form = LoginForm(password_value=expected_password)
        request = self.controller.process_login_form(form)
        self.assertEqual(request.password, expected_password)
