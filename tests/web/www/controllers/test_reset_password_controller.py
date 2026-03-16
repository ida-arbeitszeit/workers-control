from datetime import timedelta

from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.controllers.reset_password_controller import (
    ResetPasswordController,
)


class ResetPasswordControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ResetPasswordController)

    def test_validate_token_returns_none_for_invalid_token(self) -> None:
        result = self.controller.validate_token("invalid-token")
        self.assertIsNone(result)

    def test_validate_token_returns_email_for_valid_token(self) -> None:
        email = "test@test.test"
        token = self.token_service.generate_token(email)
        result = self.controller.validate_token(token)
        self.assertEqual(result, email)

    def test_validate_token_returns_none_for_expired_token(self) -> None:
        self.datetime_service.freeze_time()
        email = "test@test.test"
        token = self.token_service.generate_token(email)
        self.datetime_service.advance_time(timedelta(minutes=16))
        result = self.controller.validate_token(token)
        self.assertIsNone(result)

    def test_create_request_returns_none_for_invalid_token(self) -> None:
        result = self.controller.create_request("invalid-token", "new-password")
        self.assertIsNone(result)

    def test_create_request_returns_request_for_valid_token(self) -> None:
        email = "test@test.test"
        token = self.token_service.generate_token(email)
        result = self.controller.create_request(token, "new-password")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.email_address, email)
        self.assertEqual(result.new_password, "new-password")

    def test_create_request_returns_none_for_expired_token(self) -> None:
        self.datetime_service.freeze_time()
        email = "test@test.test"
        token = self.token_service.generate_token(email)
        self.datetime_service.advance_time(timedelta(minutes=16))
        result = self.controller.create_request(token, "new-password")
        self.assertIsNone(result)
