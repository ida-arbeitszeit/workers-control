from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.controllers.request_password_reset_controller import (
    RequestPasswordResetController,
)


class RequestPasswordResetControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RequestPasswordResetController)

    def test_returns_none_when_account_does_not_exist(self) -> None:
        result = self.controller.create_password_reset_request("nobody@test.test")
        self.assertIsNone(result)

    def test_returns_request_when_member_account_exists(self) -> None:
        email = "member@test.test"
        self.member_generator.create_member(email=email)
        result = self.controller.create_password_reset_request(email)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.email_address, email)

    def test_returns_request_when_company_account_exists(self) -> None:
        email = "company@test.test"
        self.company_generator.create_company(email=email)
        result = self.controller.create_password_reset_request(email)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.email_address, email)

    def test_returns_request_when_accountant_account_exists(self) -> None:
        email = "accountant@test.test"
        self.accountant_generator.create_accountant(email_address=email)
        result = self.controller.create_password_reset_request(email)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.email_address, email)

    def test_request_contains_generated_token(self) -> None:
        email = "member@test.test"
        self.member_generator.create_member(email=email)
        result = self.controller.create_password_reset_request(email)
        assert result is not None
        self.assertTrue(result.reset_token)
