from .base_test_case import ViewTestCase


class RequestPasswordResetViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/request-password-reset"

    def test_get_returns_200(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_with_empty_form_returns_200(self) -> None:
        response = self.client.post(self.url, data=dict())
        self.assertEqual(response.status_code, 200)

    def test_post_with_existing_member_email_returns_302(self) -> None:
        email = "member@test.test"
        self.member_generator.create_member(email=email, password="password123")
        response = self.client.post(self.url, data=dict(email=email))
        self.assertEqual(response.status_code, 302)

    def test_post_with_existing_company_email_returns_302(self) -> None:
        email = "company@test.test"
        self.company_generator.create_company(email=email, password="password123")
        response = self.client.post(self.url, data=dict(email=email))
        self.assertEqual(response.status_code, 302)

    def test_post_with_nonexistent_email_returns_302(self) -> None:
        response = self.client.post(self.url, data=dict(email="nobody@test.test"))
        self.assertEqual(response.status_code, 302)

    def test_post_with_existing_member_email_sends_reset_email(self) -> None:
        email = "member@test.test"
        self.member_generator.create_member(email=email, password="password123")
        with self.email_service.record_messages() as outbox:
            self.client.post(self.url, data=dict(email=email))
            self.assertEqual(len(outbox), 1)

    def test_post_with_nonexistent_email_sends_no_email(self) -> None:
        with self.email_service.record_messages() as outbox:
            self.client.post(self.url, data=dict(email="nobody@test.test"))
            self.assertEqual(len(outbox), 0)
