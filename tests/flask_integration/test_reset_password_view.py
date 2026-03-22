from .base_test_case import ViewTestCase


class ResetPasswordViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = "member@test.test"
        self.old_password = "old_password123"
        self.new_password = "new_password123"
        self.member_generator.create_member(
            email=self.email, password=self.old_password
        )
        self.valid_token = self.token_service.generate_token(self.email)

    def _url(self, token: str) -> str:
        return f"/reset-password/{token}"

    def test_get_with_valid_token_returns_200(self) -> None:
        response = self.client.get(self._url(self.valid_token))
        self.assertEqual(response.status_code, 200)

    def test_get_with_invalid_token_returns_200(self) -> None:
        response = self.client.get(self._url("invalid-token"))
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_token_and_valid_password_returns_302(self) -> None:
        response = self.client.post(
            self._url(self.valid_token),
            data=dict(
                password=self.new_password,
                repeat_password=self.new_password,
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_post_with_valid_token_and_too_short_password_returns_200(self) -> None:
        response = self.client.post(
            self._url(self.valid_token),
            data=dict(
                password="short",
                repeat_password="short",
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_token_and_mismatched_passwords_returns_200(self) -> None:
        response = self.client.post(
            self._url(self.valid_token),
            data=dict(
                password=self.new_password,
                repeat_password="different_password",
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_post_with_invalid_token_and_valid_password_returns_200(self) -> None:
        response = self.client.post(
            self._url("invalid-token"),
            data=dict(
                password=self.new_password,
                repeat_password=self.new_password,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_successful_reset_allows_login_with_new_password(self) -> None:
        self.client.post(
            self._url(self.valid_token),
            data=dict(
                password=self.new_password,
                repeat_password=self.new_password,
            ),
        )
        response = self.client.post(
            "/login-member",
            data=dict(email=self.email, password=self.new_password),
        )
        self.assertEqual(response.status_code, 302)

    def test_successful_reset_sends_confirmation_email(self) -> None:
        with self.email_service.record_messages() as outbox:
            self.client.post(
                self._url(self.valid_token),
                data=dict(
                    password=self.new_password,
                    repeat_password=self.new_password,
                ),
            )
            self.assertEqual(len(outbox), 1)
