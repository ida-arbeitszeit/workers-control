from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = f"/member/consumptions/{uuid4()}"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 302),
        ]
    )
    def test_correct_status_codes_for_non_members(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )


class MemberAccessTests(ViewTestCase):
    def test_logged_in_member_gets_404_for_unknown_consumption(self) -> None:
        self.login_member()
        response = self.client.get(f"/member/consumptions/{uuid4()}")
        self.assertEqual(response.status_code, 404)

    def test_logged_in_member_gets_200_for_own_plan_consumption(self) -> None:
        member = self.login_member()
        self.consumption_generator.create_private_consumption(consumer=member)
        consumption = self.database_gateway.get_private_consumptions().first()
        assert consumption
        response = self.client.get(f"/member/consumptions/{consumption.id}")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_member_gets_404_for_another_members_consumption(self) -> None:
        owner = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(consumer=owner)
        consumption = self.database_gateway.get_private_consumptions().first()
        assert consumption
        self.login_member()
        response = self.client.get(f"/member/consumptions/{consumption.id}")
        self.assertEqual(response.status_code, 404)

    def test_logged_in_member_gets_404_for_a_basic_service_consumption_id(self) -> None:
        member = self.login_member()
        self.consumption_generator.create_private_consumption_of_basic_service(
            consumer=member
        )
        bs_consumption = (
            self.database_gateway.get_private_consumptions_of_basic_service().first()
        )
        assert bs_consumption
        response = self.client.get(f"/member/consumptions/{bs_consumption.id}")
        self.assertEqual(response.status_code, 404)


class UnconfirmedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member(confirm_member=False)
        self.url = f"/member/consumptions/{uuid4()}"

    def test_unconfirmed_member_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
