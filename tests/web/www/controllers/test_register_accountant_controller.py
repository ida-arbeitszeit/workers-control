from datetime import timedelta
from typing import Optional

from tests.datetime_service import datetime_utc
from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.controllers.register_accountant_controller import (
    RegisterAccountantController,
)


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterAccountantController)

    def _valid_token(self) -> str:
        return self.token_service.generate_token("test@test.test")

    def test_that_name_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(name="test name")
        result = self.controller.create_interactor_request(form, self._valid_token())
        assert result
        assert result.request.name == "test name"

    def test_that_password_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(password="test password")
        result = self.controller.create_interactor_request(form, self._valid_token())
        assert result
        assert result.request.password == "test password"

    def test_that_email_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(email="test email")
        result = self.controller.create_interactor_request(form, self._valid_token())
        assert result
        assert result.request.email == "test email"

    def test_that_random_string_is_not_a_valid_token(self) -> None:
        form = FakeForm()
        assert not self.controller.create_interactor_request(form, "random string 123")

    def test_that_valid_token_returns_encoded_email(self) -> None:
        expected_email = "test@test.test"
        token = self.token_service.generate_token(expected_email)
        result = self.controller.create_interactor_request(FakeForm(), token)
        assert result
        assert result.token_email == expected_email

    def test_token_valid_after_23_hours_and_59_minutes(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        token = self.token_service.generate_token("test@test.test")
        self.datetime_service.advance_time(timedelta(hours=23, minutes=59))
        assert self.controller.create_interactor_request(FakeForm(), token)

    def test_token_not_valid_after_1_day_and_1_minute(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        token = self.token_service.generate_token("test@test.test")
        self.datetime_service.advance_time(timedelta(days=1, minutes=1))
        assert not self.controller.create_interactor_request(FakeForm(), token)


class FakeForm:
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        if name is None:
            name = "test name"
        if password is None:
            password = "test password"
        if email is None:
            email = "test@test.test"
        self.name = name
        self.password = password
        self.email = email

    def get_email_address(self) -> str:
        return self.email

    def get_password(self) -> str:
        return self.password

    def get_name(self) -> str:
        return self.name
