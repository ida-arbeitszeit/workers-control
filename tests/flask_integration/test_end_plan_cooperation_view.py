from uuid import uuid4

from .base_test_case import ViewTestCase

URL = "/company/end_plan_cooperation"


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_planner_ending_own_cooperation_is_redirected_to_my_cooperations(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.company)
        cooperation = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.client.post(
            URL,
            data={"plan_id": str(plan), "cooperation_id": str(cooperation)},
        )
        self.assertEqual(response.status_code, 302)
        assert response.location.endswith("/company/my_cooperations")

    def test_rejected_request_is_still_redirected_to_my_cooperations(
        self,
    ) -> None:
        response = self.client.post(
            URL,
            data={"plan_id": str(uuid4()), "cooperation_id": str(uuid4())},
        )
        self.assertEqual(response.status_code, 302)
        assert response.location.endswith("/company/my_cooperations")
