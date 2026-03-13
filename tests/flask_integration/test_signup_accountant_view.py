from parameterized import parameterized

from workers_control.core.interactors.send_accountant_registration_token import (
    SendAccountantRegistrationTokenInteractor,
)

from .base_test_case import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.send_token_interactor = self.injector.get(
            SendAccountantRegistrationTokenInteractor
        )

    @parameterized.expand(
        [
            (True, 200),
            (False, 200),
        ]
    )
    def test_get_request_leads_to_200_response_with_valid_and_invalid_token(
        self, is_valid: bool, expected_status: int
    ) -> None:
        token = (
            self.token_service.generate_token("test@test.test")
            if is_valid
            else "invalid token"
        )
        response = self.client.get(self.get_route(token))
        self.assertEqual(response.status_code, expected_status)

    def test_post_request_leads_to_redirects_with_invalid_token(self) -> None:
        token = "invalid token"
        response = self.client.post(self.get_route(token))
        assert response.status_code == 302

    def test_post_request_returns_400_with_valid_token_but_unknown_email(self) -> None:
        token = self.token_service.generate_token("unknown@test.test")
        response = self.client.post(self.get_route(token))
        assert response.status_code == 400

    def get_route(self, token: str) -> str:
        return f"/accountant/signup/{token}"
