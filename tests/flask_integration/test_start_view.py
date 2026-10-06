from typing import Optional

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/"

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
    def test_that_start_page_does_not_show_back_button(self) -> None:
        response = self.client.get("/")
        assert '<a class="button" href="/">' not in response.text


class LogoTests(ViewTestCase):
    def test_that_getting_logo_route_yields_200(self) -> None:
        response = self.client.get("/static/logo.svg")
        assert response.status_code == 200

    def test_that_logo_is_shown_on_start_page(self) -> None:
        response = self.client.get("/")
        assert 'src="/static/logo.svg"' in response.text
