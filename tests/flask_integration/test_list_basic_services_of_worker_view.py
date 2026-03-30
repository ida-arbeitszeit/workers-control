from typing import Optional

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    URL = "/member/basic_services"

    @parameterized.expand(
        [
            (LogInUser.member, 200),
        ]
    )
    def test_get_expected_code_for_logged_in_users(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.URL,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    @parameterized.expand(
        [
            (LogInUser.company,),
            (LogInUser.accountant,),
        ]
    )
    def test_non_member_users_get_redirected(self, login: LogInUser) -> None:
        self.assert_response_has_expected_code(
            url=self.URL,
            method="get",
            login=login,
            expected_code=302,
        )

    def test_anonymous_user_gets_redirected(self) -> None:
        self.assert_response_has_expected_code(
            url=self.URL,
            method="get",
            login=None,
            expected_code=302,
        )

    def test_page_renders_successfully_with_basic_services(self) -> None:
        member_id = self.login_member()
        self.basic_service_generator.create_basic_service(member=member_id)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
