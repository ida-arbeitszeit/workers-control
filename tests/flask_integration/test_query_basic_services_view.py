from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser

from .base_test_case import ViewTestCase

URL = "/user/query_basic_services"


class UserAccessTests(ViewTestCase):
    @parameterized.expand(
        [
            (LogInUser.accountant,),
            (LogInUser.company,),
            (LogInUser.member,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_authenticated_users_receive_200_on_get_request(
        self, login: Optional[LogInUser]
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=200,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant,),
            (LogInUser.company,),
            (LogInUser.member,),
        ]
    )
    def test_that_authenticated_users_receive_200_when_there_is_a_basic_service(
        self, login: Optional[LogInUser]
    ) -> None:
        self.basic_service_generator.create_basic_service()
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=200,
        )

    def test_that_anonymous_users_get_redirected_on_get_request(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=None,
            expected_code=302,
        )


class QueryBasicServicesTests(ViewTestCase):
    def test_that_service_name_appears_in_response(self) -> None:
        self.login_member()
        expected_name = f"Service-{uuid4()}"
        self.basic_service_generator.create_basic_service(name=expected_name)
        response = self.client.get(URL)
        assert expected_name in response.text

    def test_that_search_filters_by_name(self) -> None:
        self.login_member()
        expected_name = f"Haircut-{uuid4()}"
        unexpected_name = f"Plumbing-{uuid4()}"
        self.basic_service_generator.create_basic_service(name=expected_name)
        self.basic_service_generator.create_basic_service(name=unexpected_name)
        response = self.client.get(URL, query_string={"search": expected_name})
        assert expected_name in response.text
        assert unexpected_name not in response.text
