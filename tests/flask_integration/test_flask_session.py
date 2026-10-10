from flask import url_for
from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase

PASSWORD = "password123"


class FlaskSessionTests(ViewTestCase):
    @parameterized.expand(
        [(LogInUser.member,), (LogInUser.company,), (LogInUser.accountant,)]
    )
    def test_remembered_login_outlives_the_browser_session(
        self, user: LogInUser
    ) -> None:
        self.log_in(user, remember=True)
        assert self.cookie_has_expiration_date()

    @parameterized.expand(
        [(LogInUser.member,), (LogInUser.company,), (LogInUser.accountant,)]
    )
    def test_login_that_is_not_remembered_ends_with_the_browser_session(
        self, user: LogInUser
    ) -> None:
        self.log_in(user, remember=False)
        assert not self.cookie_has_expiration_date()

    def test_remembered_login_ends_with_the_browser_session_after_logout(
        self,
    ) -> None:
        self.log_in(LogInUser.member, remember=True)
        self.client.get("/logout")
        assert not self.cookie_has_expiration_date()

    def test_user_cannot_access_dashboard_after_logout(self) -> None:
        self.log_in(LogInUser.member, remember=False)
        self.client.get("/logout")
        response = self.client.get("/member/dashboard")
        assert response.status_code == 302

    def log_in(self, user: LogInUser, remember: bool) -> None:
        email = self.email_generator.get_random_email()
        if user == LogInUser.member:
            self.member_generator.create_member(email=email, password=PASSWORD)
            url = "/login-member"
        elif user == LogInUser.company:
            self.company_generator.create_company(email=email, password=PASSWORD)
            url = "/company/login"
        else:
            self.accountant_generator.create_accountant(
                email_address=email, password=PASSWORD
            )
            url = "/accountant/login"
        data = dict(email=email, password=PASSWORD)
        if remember:
            data["remember"] = "y"
        response = self.client.post(url, data=data)
        assert response.status_code == 302

    def cookie_has_expiration_date(self) -> bool:
        cookie = self.client.get_cookie("session", domain="test.name")
        assert cookie
        return cookie.expires is not None
