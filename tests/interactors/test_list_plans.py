from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.list_active_plans_of_company import (
    ListActivePlansOfCompanyInteractor,
    ListPlansResponse,
)
from workers_control.core.records import Company


class ListPlansTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.list_plans = self.injector.get(ListActivePlansOfCompanyInteractor)

    @classmethod
    def plan_in_results(cls, plan: UUID, response: ListPlansResponse) -> bool:
        return any((plan == result.id for result in response.plans))

    def test_list_plans_response_is_empty_for_nonexisting_company(self) -> None:
        response: ListPlansResponse = self.list_plans.execute(company_id=uuid4())
        assert not response.plans

    def test_list_plans_response_is_empty_for_company_without_plans(self) -> None:
        company: Company = self.company_generator.create_company_record()
        response: ListPlansResponse = self.list_plans.execute(company_id=company.id)
        assert not response.plans

    def test_list_plans_response_includes_single_plan(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response: ListPlansResponse = self.list_plans.execute(company_id=company)
        assert self.plan_in_results(plan, response)

    def test_list_plans_response_includes_multiple_plans(self) -> None:
        company = self.company_generator.create_company()
        plan1 = self.plan_generator.create_plan(planner=company)
        plan2 = self.plan_generator.create_plan(planner=company)
        response: ListPlansResponse = self.list_plans.execute(company_id=company)
        assert self.plan_in_results(plan1, response) and self.plan_in_results(
            plan2, response
        )
