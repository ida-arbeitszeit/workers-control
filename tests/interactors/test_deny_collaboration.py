from datetime import timedelta
from uuid import uuid4

from tests.datetime_service import datetime_utc
from workers_control.core.interactors.deny_collaboration import (
    DenyCollaborationInteractor,
    DenyCollaborationRequest,
    DenyCollaborationResponse,
)
from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationInteractor,
    RequestCollaborationRequest,
)

from ..base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.deny_collaboration = self.injector.get(DenyCollaborationInteractor)
        self.request_collaboration = self.injector.get(RequestCollaborationInteractor)

    def test_error_is_raises_when_plan_does_not_exist(self) -> None:
        requester = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = DenyCollaborationRequest(
            requester_id=requester, plan_id=uuid4(), collaboration_id=collaboration
        )
        response = self.deny_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == DenyCollaborationResponse.RejectionReason.plan_not_found
        )

    def test_error_is_raised_when_collaboration_does_not_exist(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        request = DenyCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=uuid4()
        )
        response = self.deny_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.collaboration_not_found
        )

    def test_error_is_raised_when_collaboration_was_not_requested(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = DenyCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.deny_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.collaboration_was_not_requested
        )

    def test_error_is_raised_when_requester_is_not_coordinator_of_collaboration(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        coordinator = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        plan = self.plan_generator.create_plan(requested_collaboration=collaboration)
        request = DenyCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.deny_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_coordinator
        )

    def test_possible_to_deny_collaboration(self) -> None:
        requester = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_collaboration=collaboration)
        request = DenyCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.deny_collaboration.execute(request)
        assert not response.is_rejected

    def test_possible_to_request_collaboration_again_after_collaboration_has_been_denied(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_collaboration=collaboration)
        request = DenyCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        self.deny_collaboration.execute(request)
        request_request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        self.request_collaboration.execute(request_request)

    def test_that_collaboration_for_inactive_plans_cannot_be_denied(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        requester = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            requested_collaboration=collaboration, timeframe=1
        )
        self.datetime_service.advance_time(timedelta(days=2))
        request = DenyCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.deny_collaboration.execute(request)
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_is_inactive
