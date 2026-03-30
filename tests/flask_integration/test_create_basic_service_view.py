from typing import Optional

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class UserAccessGetTests(ViewTestCase):
    URL = "/member/create_basic_service"

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


class UserAccessPostTests(ViewTestCase):
    URL = "/member/create_basic_service"

    @parameterized.expand(
        [
            (LogInUser.company,),
            (LogInUser.accountant,),
        ]
    )
    def test_non_member_users_get_redirected(self, login: LogInUser) -> None:
        self.assert_response_has_expected_code(
            url=self.URL,
            method="post",
            login=login,
            expected_code=302,
        )

    def test_anonymous_user_gets_redirected(self) -> None:
        self.assert_response_has_expected_code(
            url=self.URL,
            method="post",
            login=None,
            expected_code=302,
        )


class AuthenticatedMemberGetTests(ViewTestCase):
    URL = "/member/create_basic_service"

    def setUp(self) -> None:
        super().setUp()
        self.login_member()

    def test_get_returns_200(self) -> None:
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)

    def test_data_protection_warning_is_shown(self) -> None:
        response = self.client.get(self.URL)
        self.assertIn("data protection", response.text)


class AuthenticatedMemberPostTests(ViewTestCase):
    URL = "/member/create_basic_service"

    def setUp(self) -> None:
        super().setUp()
        self.login_member()

    def test_post_with_valid_data_redirects(self) -> None:
        response = self.client.post(
            self.URL,
            data=dict(name="Test Service", description="A test description"),
        )
        self.assertEqual(response.status_code, 302)

    def test_post_with_valid_data_redirects_to_basic_services_list(self) -> None:
        response = self.client.post(
            self.URL,
            data=dict(name="Test Service", description="A test description"),
        )
        assert response.location
        self.assertIn("/member/basic_services", response.location)

    def test_post_with_valid_data_creates_basic_service(self) -> None:
        member_id = self.login_member()
        self.client.post(
            self.URL,
            data=dict(name="My Service", description="My description"),
        )
        services = list(
            self.database_gateway.get_basic_services().of_provider(member_id)
        )
        self.assertEqual(len(services), 1)

    def test_post_with_empty_data_returns_400(self) -> None:
        response = self.client.post(self.URL, data={})
        self.assertEqual(response.status_code, 400)
