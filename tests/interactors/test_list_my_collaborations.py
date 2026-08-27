from uuid import uuid4

from workers_control.core.interactors.list_my_collaborating_plans import (
    ListMyCollaboratingPlansInteractor,
)

from ..base_test_case import BaseTestCase


class InteractorTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListMyCollaboratingPlansInteractor)

    def test_failure_is_raised_if_requesting_company_does_not_exist(self) -> None:
        with self.assertRaises(ListMyCollaboratingPlansInteractor.Failure):
            request = ListMyCollaboratingPlansInteractor.Request(company=uuid4())
            self.interactor.list_collaborations(request)

    def test_response_is_returned_if_requester_does_exist(self) -> None:
        requester = self.company_generator.create_company()
        request = ListMyCollaboratingPlansInteractor.Request(company=requester)
        result = self.interactor.list_collaborations(request=request)
        assert isinstance(result, ListMyCollaboratingPlansInteractor.Response)

    def test_no_plans_are_returned_if_requester_has_no_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCollaboratingPlansInteractor.Request(company=company)
        result = self.interactor.list_collaborations(request=request)
        assert len(result.collaborating_plans) == 0

    def test_no_plans_are_returned_if_requester_has_no_active_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCollaboratingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, approved=False)
        result = self.interactor.list_collaborations(request=request)
        assert len(result.collaborating_plans) == 0

    def test_no_plans_are_returned_if_requester_has_no_collaborating_plans(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        request = ListMyCollaboratingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, collaboration=None)
        result = self.interactor.list_collaborations(request=request)
        assert len(result.collaborating_plans) == 0

    def test_one_plan_is_returned_if_requester_has_one_active_collaborating_plan(
        self,
    ) -> None:
        collab = self.collaboration_generator.create_collaboration()
        company = self.company_generator.create_company()
        request = ListMyCollaboratingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, collaboration=collab)
        result = self.interactor.list_collaborations(request=request)
        assert len(result.collaborating_plans) == 1

    def test_returned_plan_has_correct_attributes(self) -> None:
        expected_collab_name = "Test Collaboration"
        expected_product_name = "test product name"
        collab = self.collaboration_generator.create_collaboration(
            name=expected_collab_name
        )
        company = self.company_generator.create_company()
        request = ListMyCollaboratingPlansInteractor.Request(company=company)
        plan = self.plan_generator.create_plan(
            planner=company, collaboration=collab, product_name=expected_product_name
        )
        result = self.interactor.list_collaborations(request=request)
        collaborating_plan = result.collaborating_plans[0]
        assert collaborating_plan.collab_id == collab
        assert collaborating_plan.collab_name == expected_collab_name
        assert collaborating_plan.plan_id == plan
        assert collaborating_plan.plan_name == expected_product_name

    def test_two_plans_are_returned_if_requester_has_two_active_collaborating_plan(
        self,
    ) -> None:
        collab = self.collaboration_generator.create_collaboration()
        company = self.company_generator.create_company()
        request = ListMyCollaboratingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, collaboration=collab)
        self.plan_generator.create_plan(planner=company, collaboration=collab)
        result = self.interactor.list_collaborations(request=request)
        assert len(result.collaborating_plans) == 2
