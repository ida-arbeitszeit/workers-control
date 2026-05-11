from typing import Optional

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/resend"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 302),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_post_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="post",
            login=login,
            expected_code=expected_code,
        )

    def test_get_returns_405_because_route_only_accepts_post(self) -> None:
        self.login_member(confirm_member=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class AuthenticatedButUnconfirmedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/resend"
        self.member = self.login_member(confirm_member=False)

    def test_authenticated_and_unconfirmed_users_get_redirected_and_mail_gets_send(
        self,
    ) -> None:
        with self.email_service.record_messages() as outbox:
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1


class ConfirmedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/resend"
        self.member = self.login_member(confirm_member=True)

    def test_already_confirmed_member_gets_redirected_and_no_mail_gets_sent(
        self,
    ) -> None:
        with self.email_service.record_messages() as outbox:
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 0


class OutboxPersistenceTests(ViewTestCase):
    def test_member_resend_commits_email_row_to_outbox(self) -> None:
        self.login_member(confirm_member=False)
        self.client.post("/member/resend")
        # Discard uncommitted state so we only see rows the request actually
        # committed.
        self.db.session.rollback()
        assert self.database_gateway.get_emails().first() is not None

    def test_company_resend_commits_email_row_to_outbox(self) -> None:
        self.login_company(confirm_company=False)
        self.client.post("/company/resend")
        self.db.session.rollback()
        assert self.database_gateway.get_emails().first() is not None
