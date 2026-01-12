from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase

URL = "/user/show_payout_factor_details"


class UserAccessTests(ViewTestCase):
    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
        ]
    )
    def test_get_200_for_logged_in_users(
        self, login: LogInUser | None, expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_get_302_for_unauthenticated_users(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=None,
            expected_code=302,
        )
