from typing import Optional

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/consumptions"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 200),
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


class CompanyWithConsumptionsTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/consumptions"

    def test_logged_in_company_gets_200_after_consuming_a_basic_service(self) -> None:
        company = self.login_company()
        self.consumption_generator.create_productive_consumption_of_basic_service(
            consumer=company
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class UnconfirmedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company(confirm_company=False)
        self.url = "/company/consumptions"

    def test_unconfirmed_company_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
