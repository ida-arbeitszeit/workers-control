from .base_test_case import ViewTestCase


class LoginTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/accountant/login"

    def test_get_200_when_accessing_login_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_200_when_posting_to_url(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_redirected_when_posting_correct_credentials(self) -> None:
        self.accountant_generator.create_accountant(
            email_address="a@b.c", password="testpassword"
        )
        response = self.client.post(
            self.url,
            data=dict(
                email="a@b.c",
                password="testpassword",
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_get_401_when_posting_incorrect_credentials(self) -> None:
        self.accountant_generator.create_accountant(
            email_address="a@b.c", password="testpassword"
        )
        response = self.client.post(
            self.url,
            data=dict(
                email="a@b.c",
                password="wrongpassword",
            ),
        )
        self.assertEqual(response.status_code, 401)


class LoggedInUserTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/accountant/login"

    def test_logged_in_accountant_gets_redirected_to_dashboard(self) -> None:
        self.login_accountant()
        response = self.client.get(self.url)
        assert response.status_code == 302
        assert response.location == "/accountant/dashboard"

    def test_logged_in_member_sees_login_form(self) -> None:
        self.login_member()
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_logged_in_member_gets_logged_out(self) -> None:
        self.login_member()
        self.client.get(self.url)
        response = self.client.get("/member/dashboard")
        assert response.status_code == 302
