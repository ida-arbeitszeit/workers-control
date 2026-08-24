from uuid import UUID

from workers_control.core.interactors import show_company_collaborations
from workers_control.core.interactors.cancel_collaboration_solicitation import (
    CancelCollaborationSolicitationInteractor,
    CancelCollaborationSolicitationRequest,
)

from ..base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(CancelCollaborationSolicitationInteractor)
        self.show_company_collaborations = self.injector.get(
            show_company_collaborations.ShowCompanyCollaborationsInteractor
        )

    def test_that_false_is_returned_when_requester_is_not_planner(self) -> None:
        plan = self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        response = self.interactor.execute(
            CancelCollaborationSolicitationRequest(company.id, plan)
        )
        assert not response

    def test_that_false_is_returned_when_plan_has_no_pending_requests(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.interactor.execute(
            CancelCollaborationSolicitationRequest(company, plan)
        )
        assert not response

    def test_that_plan_is_not_requesting_collaboration_after_cancelation_was_requested(
        self,
    ) -> None:
        collab = self.collaboration_generator.create_collaboration()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company, requested_collaboration=collab
        )
        self.interactor.execute(CancelCollaborationSolicitationRequest(company, plan))
        assert not self._is_plan_requesting_collaboration(plan=plan, planner=company)

    def test_that_true_is_returned_when_collab_request_gets_canceled(self) -> None:
        collab = self.collaboration_generator.create_collaboration()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company, requested_collaboration=collab
        )
        response = self.interactor.execute(
            CancelCollaborationSolicitationRequest(company, plan)
        )
        assert response

    def _is_plan_requesting_collaboration(self, plan: UUID, planner: UUID) -> bool:
        response = self.show_company_collaborations.show_company_collaborations(
            show_company_collaborations.Request(company=planner)
        )
        return any(
            plan == collab_request.plan_id
            for collab_request in response.outbound_collaboration_requests
        )
