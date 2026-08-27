from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors import get_collab_summary
from workers_control.core.interactors.end_collaboration import (
    EndCollaborationInteractor,
    EndCollaborationRequest,
    EndCollaborationResponse,
)


class TestEndCollaboration(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.end_collaboration = self.injector.get(EndCollaborationInteractor)
        self.requester = self.company_generator.create_company()
        self.get_collab_summary_interactor = self.injector.get(
            get_collab_summary.GetCollabSummaryInteractor
        )

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        collaboration = self.collaboration_generator.create_collaboration()
        request = EndCollaborationRequest(
            requester_id=self.requester,
            plan_id=uuid4(),
            collaboration_id=collaboration,
        )
        response = self.end_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCollaborationResponse.RejectionReason.plan_not_found
        )

    def test_error_is_raised_when_collaboration_does_not_exist(self) -> None:
        plan = self.plan_generator.create_plan()
        request = EndCollaborationRequest(
            requester_id=self.requester, plan_id=plan, collaboration_id=uuid4()
        )
        response = self.end_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCollaborationResponse.RejectionReason.collaboration_not_found
        )

    def test_error_is_raised_when_plan_has_no_collaboration(self) -> None:
        collaboration = self.collaboration_generator.create_collaboration()
        plan = self.plan_generator.create_plan(collaboration=None)
        request = EndCollaborationRequest(
            requester_id=self.requester,
            plan_id=plan,
            collaboration_id=collaboration,
        )
        response = self.end_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCollaborationResponse.RejectionReason.plan_has_no_collaboration
        )

    def test_error_is_raised_when_requester_is_neither_coordinator_nor_planner(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(plans=[plan])

        request = EndCollaborationRequest(
            requester_id=self.requester,
            plan_id=plan,
            collaboration_id=collaboration,
        )
        response = self.end_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCollaborationResponse.RejectionReason.requester_is_not_authorized
        )

    def test_ending_of_collaboration_is_successful_when_requester_is_planner(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.requester)
        collaboration = self.collaboration_generator.create_collaboration(plans=[plan])

        request = EndCollaborationRequest(
            requester_id=self.requester,
            plan_id=plan,
            collaboration_id=collaboration,
        )
        response = self.end_collaboration.execute(request)
        assert not response.is_rejected

    def test_ending_of_collaboration_is_successful_when_requester_is_coordinator(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(
            plans=[plan], coordinator=self.requester
        )

        request = EndCollaborationRequest(
            requester_id=self.requester,
            plan_id=plan,
            collaboration_id=collaboration,
        )
        response = self.end_collaboration.execute(request)
        assert not response.is_rejected

    def test_ending_of_collaboration_is_successful_and_plan_deleted_from_collab(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.requester)
        collaboration = self.collaboration_generator.create_collaboration(plans=[plan])
        request = EndCollaborationRequest(
            requester_id=self.requester,
            plan_id=plan,
            collaboration_id=collaboration,
        )
        response = self.end_collaboration.execute(request)
        assert not response.is_rejected
        assert not self.is_plan_in_collaboration(plan, collaboration)

    def is_plan_in_collaboration(self, plan: UUID, collaboration: UUID) -> bool:
        requester = self.company_generator.create_company()
        request = get_collab_summary.GetCollabSummaryRequest(
            collab_id=collaboration,
            requester_id=requester,
        )
        response = self.get_collab_summary_interactor.execute(request)
        assert response
        return any([plan == p.plan_id for p in response.plans])
