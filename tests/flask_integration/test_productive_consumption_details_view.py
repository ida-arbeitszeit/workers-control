from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = f"/company/consumptions/{uuid4()}"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_for_non_companies(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )


class CompanyAccessTests(ViewTestCase):
    def test_logged_in_company_gets_404_for_unknown_consumption(self) -> None:
        self.login_company()
        response = self.client.get(f"/company/consumptions/{uuid4()}")
        self.assertEqual(response.status_code, 404)

    def test_logged_in_company_gets_200_for_own_resource_consumption(self) -> None:
        company = self.login_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company
        )
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        response = self.client.get(f"/company/consumptions/{consumption.id}")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_company_gets_404_for_another_companys_consumption(self) -> None:
        owner = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=owner
        )
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        self.login_company()
        response = self.client.get(f"/company/consumptions/{consumption.id}")
        self.assertEqual(response.status_code, 404)


class UnconfirmedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company(confirm_company=False)
        self.url = f"/company/consumptions/{uuid4()}"

    def test_unconfirmed_company_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
