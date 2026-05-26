from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase

URL = "/user/change-name"
AUTHENTICATED_USER_LOGINS = [
    (LogInUser.member,),
    (LogInUser.unconfirmed_member,),
    (LogInUser.company,),
    (LogInUser.unconfirmed_company,),
    (LogInUser.accountant,),
]


class ChangeUserNameViewTests(ViewTestCase):
    @parameterized.expand(AUTHENTICATED_USER_LOGINS)
    def test_that_authenticated_users_get_400_response_on_post_without_data(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="POST",
            expected_code=400,
            login=login,
        )

    @parameterized.expand(AUTHENTICATED_USER_LOGINS)
    def test_that_authenticated_users_get_200_with_get_request(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="GET",
            expected_code=200,
            login=login,
        )

    def test_that_unauthenticated_user_gets_redirect_on_get(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="GET",
            expected_code=302,
            login=None,
        )

    def test_that_unauthenticated_user_gets_403_on_post(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="POST",
            expected_code=403,
            login=None,
        )

    def test_that_member_gets_redirected_on_successful_name_change(self) -> None:
        password = "123password"
        self.login_member(password=password)
        response = self.client.post(
            URL,
            data={"new_name": "New Member Name", "current_password": password},
        )
        assert response.status_code == 302

    def test_that_member_gets_400_with_wrong_password(self) -> None:
        password = "123password"
        self.login_member(password=password)
        response = self.client.post(
            URL,
            data={"new_name": "New Name", "current_password": password + "wrong"},
        )
        assert response.status_code == 400

    def test_that_member_sees_password_error_message_with_wrong_password(self) -> None:
        password = "123password"
        self.login_member(password=password)
        response = self.client.post(
            URL,
            data={"new_name": "New Name", "current_password": password + "wrong"},
        )
        assert "The password is incorrect." in response.text


class SentEmailTests(ViewTestCase):
    def test_that_one_confirmation_email_is_sent_after_successful_change(self) -> None:
        password = "123password"
        email = "user@test.test"
        self.login_member(email=email, password=password)
        with self.email_service.record_messages() as outbox:
            response = self.client.post(
                URL,
                data={"new_name": "Renamed", "current_password": password},
            )
            assert response.status_code == 302
            assert len(outbox) == 1
            assert outbox[0].recipient == email
