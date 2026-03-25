from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    @parameterized.expand(
        [
            (LogInUser.accountant, 404),
            (LogInUser.company, 404),
            (LogInUser.member, 404),
        ]
    )
    def test_get_404_for_logged_in_users_when_basic_service_does_not_exist(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        url = f"/user/basic_service/{uuid4()}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_get_302_for_unauthenticated_users_when_basic_service_does_not_exist(
        self,
    ) -> None:
        url = f"/user/basic_service/{uuid4()}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=None,
            expected_code=302,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
        ]
    )
    def test_get_200_for_logged_in_users_when_basic_service_exists(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        basic_service_id = self.basic_service_generator.create_basic_service()
        url = f"/user/basic_service/{basic_service_id}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_get_302_for_unauthenticated_users_when_basic_service_exists(self) -> None:
        basic_service_id = self.basic_service_generator.create_basic_service()
        url = f"/user/basic_service/{basic_service_id}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=None,
            expected_code=302,
        )
