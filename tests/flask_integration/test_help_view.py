from typing import Optional

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class HelpViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/help"

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (None, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
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


class NavigationTests(ViewTestCase):
    def test_that_home_link_points_to_start_page_for_anonymous_users(
        self,
    ) -> None:
        response = self.client.get("/help")
        assert '<a href="/" class="site-header-home"' in response.text

    @parameterized.expand(
        [
            (LogInUser.accountant, "/accountant/dashboard"),
            (LogInUser.company, "/company/dashboard"),
            (LogInUser.member, "/member/dashboard"),
        ]
    )
    def test_that_home_link_points_to_dashboard_for_logged_in_users(
        self, login: LogInUser, expected_dashboard_url: str
    ) -> None:
        self.login_user(login)
        response = self.client.get("/help")
        assert (
            f'<a href="{expected_dashboard_url}" class="site-header-home"'
            in response.text
        )
