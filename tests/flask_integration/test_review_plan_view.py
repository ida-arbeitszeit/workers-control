from uuid import uuid4

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class ReviewPlanViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (None, 302),
            (LogInUser.company, 302),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_get_requests(
        self, login: LogInUser | None, expected_code: int
    ) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.assert_response_has_expected_code(
            url=f"/accountant/plans/{plan}/review",
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_that_get_returns_404_for_a_nonexistent_plan(self) -> None:
        self.login_accountant()
        response = self.client.get(f"/accountant/plans/{uuid4()}/review")
        self.assertEqual(response.status_code, 404)

    def test_that_posting_approve_redirects_and_approves_the_plan(self) -> None:
        self.login_accountant()
        plan = self.plan_generator.create_plan(approved=False)
        response = self.client.post(
            f"/accountant/plans/{plan}/review",
            data={"decision": "approve"},
        )
        self.assertEqual(response.status_code, 302)
        plan_record = self.database_gateway.get_plans().with_id(plan).first()
        assert plan_record is not None
        assert plan_record.is_approved

    def test_that_posting_reject_redirects_and_rejects_the_plan(self) -> None:
        self.login_accountant()
        plan = self.plan_generator.create_plan(approved=False)
        response = self.client.post(
            f"/accountant/plans/{plan}/review",
            data={"decision": "reject"},
        )
        self.assertEqual(response.status_code, 302)
        plan_record = self.database_gateway.get_plans().with_id(plan).first()
        assert plan_record is not None
        assert plan_record.is_rejected

    def test_that_posting_without_a_decision_re_renders_the_page_with_400(self) -> None:
        self.login_accountant()
        plan = self.plan_generator.create_plan(approved=False)
        response = self.client.post(f"/accountant/plans/{plan}/review", data={})
        self.assertEqual(response.status_code, 400)
