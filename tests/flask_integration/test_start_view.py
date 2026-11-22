from typing import Optional

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 200),
            (LogInUser.company, 302),
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

    @parameterized.expand(
        [
            (LogInUser.accountant, "/accountant/dashboard"),
            (LogInUser.company, "/company/dashboard"),
            (LogInUser.member, "/member/dashboard"),
        ]
    )
    def test_logged_in_users_are_redirected_to_their_dashboard(
        self, login: LogInUser, expected_target_url: str
    ) -> None:
        self.login_user(login)
        response = self.client.get(self.url)
        assert response.status_code == 302
        assert response.location == expected_target_url


class LogoTests(ViewTestCase):
    def test_that_getting_logo_route_yields_200(self) -> None:
        response = self.client.get("/static/logo.svg")
        assert response.status_code == 200

    def test_that_logo_is_shown_on_start_page(self) -> None:
        response = self.client.get("/")
        assert 'src="/static/logo.svg"' in response.text
