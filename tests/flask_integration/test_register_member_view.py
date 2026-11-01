from typing import Optional

from parameterized import param, parameterized

from .base_test_case import LogInUser, ViewTestCase


def create_signup_form(email: str) -> dict[str, str]:
    return dict(
        email=email,
        name="test name",
        password="test_password",
        repeat_password="test_password",
    )


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/signup-member"

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (None, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_get_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )


class UserTypeChangesTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/signup-member"

    def test_user_type_in_session_is_set_to_none_when_company_accesses_page(
        self,
    ) -> None:
        self.login_company()
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "company")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])

    def test_user_type_in_session_is_set_to_none_when_accountant_accesses_page(
        self,
    ) -> None:
        self.login_accountant()
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "accountant")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])

    def test_user_type_in_session_does_not_change_when_member_accesses_page(
        self,
    ) -> None:
        self.login_member()
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")


class LoggedInUserPostTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/signup-member"

    @parameterized.expand([("new@cp.org",), ("invalid_email",)])
    def test_that_logged_in_member_is_redirected_to_dashboard(self, email: str) -> None:
        self.login_member()
        response = self.client.post(self.url, data=create_signup_form(email))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/member/dashboard")

    def test_that_logged_in_member_cannot_register_another_member(self) -> None:
        email = "new@cp.org"
        self.login_member()
        self.client.post(self.url, data=create_signup_form(email))
        assert not self.database_gateway.get_members().with_email_address(email)

    @parameterized.expand([(LogInUser.company,), (LogInUser.accountant,)])
    def test_that_other_logged_in_users_are_logged_out_when_email_is_invalid(
        self, login: LogInUser
    ) -> None:
        self.login_user(login)
        response = self.client.post(self.url, data=create_signup_form("invalid_email"))
        self.assertEqual(response.status_code, 400)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])

    def test_that_logged_in_company_can_register_as_member(self) -> None:
        self.login_company()
        response = self.client.post(self.url, data=create_signup_form("new@cp.org"))
        self.assertEqual(response.location, "/unconfirmed-member")
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")


class UnauthenticatedAndUnconfirmedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/signup-member"

    def test_correct_posting_is_possible_and_redirects_user(self) -> None:
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

    def test_correct_posting_makes_that_confirmations_mail_is_sent_to_member(
        self,
    ) -> None:
        member_email = "test2@cp.org"
        with self.email_service.record_messages() as outbox:
            response = self.client.post(
                self.url,
                data=dict(
                    email=member_email,
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                ),
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1
            assert outbox[0].sender == "test_sender@cp.org"
            assert outbox[0].recipient == member_email

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
    def test_invalid_form_posting_with_incorrect_form_does_not_redirect_user(
        self, invalid_form_data: dict
    ) -> None:
        response = self.client.post(self.url, data=invalid_form_data)
        self.assertEqual(response.status_code, 400)
