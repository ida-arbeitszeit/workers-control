from parameterized import param, parameterized

from .base_test_case import LogInUser, ViewTestCase


def create_signup_form(email: str) -> dict[str, str]:
    return dict(
        email=email,
        name="test name",
        password="test_password",
        repeat_password="test_password",
    )


class AuthenticatedMemberGetTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member()
        self.url = "/company/signup"

    def test_authenticated_member_gets_200_when_accessing_company_page(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_type_in_session_is_set_to_none_when_member_accesses_company_page(
        self,
    ) -> None:
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])


class LoggedInUserPostTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/signup"

    @parameterized.expand([("new@cp.org",), ("invalid_email",)])
    def test_that_logged_in_company_is_redirected_to_dashboard(
        self, email: str
    ) -> None:
        self.login_company()
        response = self.client.post(self.url, data=create_signup_form(email))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/company/dashboard")

    def test_that_logged_in_company_cannot_register_another_company(self) -> None:
        email = "new@cp.org"
        self.login_company()
        self.client.post(self.url, data=create_signup_form(email))
        assert not self.database_gateway.get_companies().with_email_address(email)

    @parameterized.expand([(LogInUser.member,), (LogInUser.accountant,)])
    def test_that_other_logged_in_users_are_logged_out_when_email_is_invalid(
        self, login: LogInUser
    ) -> None:
        self.login_user(login)
        response = self.client.post(self.url, data=create_signup_form("invalid_email"))
        self.assertEqual(response.status_code, 400)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])

    def test_that_logged_in_member_can_register_as_company(self) -> None:
        self.login_member()
        response = self.client.post(self.url, data=create_signup_form("new@cp.org"))
        self.assertEqual(response.location, "/company/unconfirmed")
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "company")


class UnauthenticatedAndUnconfirmedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/signup"

    def test_unauthenticated_and_unconfirmed_company_gets_200(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_posting_is_possible_and_redirects_company(self) -> None:
        response = self.client.post(
            self.url,
            data=dict(
                email="test@cp.org",
                name="test name",
                password="test_password",
                repeat_password="test_password",
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_correct_posting_makes_that_confirmations_mail_is_sent_to_company(
        self,
    ) -> None:
        company_email = "test2@cp.org"
        with self.email_service.record_messages() as outbox:
            response = self.client.post(
                self.url,
                data=dict(
                    email=company_email,
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                ),
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1
            assert outbox[0].sender == "test_sender@cp.org"
            assert outbox[0].recipient == company_email

    @parameterized.expand(
        [
            param(
                dict(
                    email="test@cp.org",
                    name="test name",
                    password="test_password",
                    repeat_password="not_same_password",
                )
            ),
            param(
                dict(
                    email="test@cp.org",
                    name="test name",
                    password="short",
                    repeat_password="short",
                )
            ),
            param(
                dict(
                    email="test@cp.org",
                    name="",
                    password="test_password",
                    repeat_password="test_password",
                )
            ),
            param(
                dict(
                    email="invalid_email",
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                )
            ),
            param(
                dict(
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                )
            ),
        ]
    )
    def test_invalid_form_posting_with_incorrect_form_does_not_redirect_company(
        self, invalid_form_data: dict
    ) -> None:
        response = self.client.post(self.url, data=invalid_form_data)
        self.assertEqual(response.status_code, 400)
