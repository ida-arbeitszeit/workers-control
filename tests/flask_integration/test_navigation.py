from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class NavigationTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/help"

    @parameterized.expand(
        [
            (LogInUser.accountant,),
            (LogInUser.company,),
            (LogInUser.member,),
        ]
    )
    def test_logged_in_users_see_link_to_their_user_account(
        self, login: LogInUser
    ) -> None:
        self.login_user(login)
        response = self.client.get(self.url)
        assert 'href="/user/account"' in response.text

    def test_anonymous_users_see_no_link_to_a_user_account(self) -> None:
        response = self.client.get(self.url)
        assert 'href="/user/account"' not in response.text
