from uuid import uuid4

from parameterized import parameterized

from workers_control.core import email_notifications
from workers_control.core.interactors.accept_collaboration import (
    AcceptCollaborationInteractor,
    AcceptCollaborationRequest,
)
from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationInteractor,
    RequestCollaborationRequest,
    RequestCollaborationResponse,
)

from ..base_test_case import BaseTestCase


class RequestCollaborationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(RequestCollaborationInteractor)
        self.accept_collaboration = self.injector.get(AcceptCollaborationInteractor)
        self.requester = self.company_generator.create_company()

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        collaboration = self.collaboration_generator.create_collaboration()
        request = RequestCollaborationRequest(
            requester_id=self.requester,
            plan_id=uuid4(),
            collaboration_id=collaboration,
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCollaborationResponse.RejectionReason.plan_not_found
        )

    def test_error_is_raised_when_collaboration_does_not_exist(self) -> None:
        plan = self.plan_generator.create_plan()
        request = RequestCollaborationRequest(
            requester_id=self.requester, plan_id=plan, collaboration_id=uuid4()
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCollaborationResponse.RejectionReason.collaboration_not_found
        )

    def test_error_is_raised_when_plan_has_already_collaboration(self) -> None:
        collaboration1 = self.collaboration_generator.create_collaboration()
        collaboration2 = self.collaboration_generator.create_collaboration(
            name="name2", coordinator=self.requester
        )
        plan = self.plan_generator.create_plan(collaboration=collaboration1)
        request = RequestCollaborationRequest(
            requester_id=self.requester,
            plan_id=plan,
            collaboration_id=collaboration2,
        )

        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCollaborationResponse.RejectionReason.plan_has_collaboration
        )

    def test_error_is_raised_when_plan_is_already_requesting_collaboration(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        collaboration1 = self.collaboration_generator.create_collaboration()
        plan = self.plan_generator.create_plan(
            requested_collaboration=collaboration1,
        )
        collaboration2 = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration2
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.plan_is_already_requesting_collaboration
        )

    def test_error_is_raised_when_plan_is_public_plan(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_public_service=True)
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_is_public_service
        )

    def test_error_is_raised_when_requester_is_not_planner(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_planner
        )

    def test_requesting_collaboration_is_successful(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.interactor.execute(request)
        assert not response.is_rejected

    def test_successful_collaboration_request_returns_coordinator_data(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.interactor.execute(request)
        assert response.coordinator_name
        assert response.coordinator_email

    def test_succesfully_requesting_collaboration_makes_it_possible_to_accept_collaboration(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        self.interactor.execute(request)
        accept_collaboration_response = self.accept_collaboration.execute(
            AcceptCollaborationRequest(requester, plan, collaboration)
        )
        assert not accept_collaboration_response.is_rejected

    def test_that_after_requesting_successfully_an_email_was_sent_out(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        collaboration = self.collaboration_generator.create_collaboration()
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        messages_before_request = len(self.email_sender.get_messages_sent())
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert len(self.email_sender.get_messages_sent()) == messages_before_request + 1

    def test_that_after_requesting_successfully_a_collaboration_request_email_was_sent(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        collaboration = self.collaboration_generator.create_collaboration()
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        messages_before_request = len(self.get_collaboration_request_emails())
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert (
            len(self.get_collaboration_request_emails()) == messages_before_request + 1
        )

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_after_requesting_successfully_the_email_sent_contains_the_expected_coordinator_email_address(
        self, expected_email_address: str
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        coordinator = self.company_generator.create_company(
            email=expected_email_address
        )
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert (
            self.get_latest_collaboration_request_email().coordinator_email_address
            == expected_email_address
        )

    @parameterized.expand(
        [
            ("test name",),
            ("other name",),
        ]
    )
    def test_that_after_requesting_successfully_the_email_sent_contains_the_expected_coordinator_name(
        self, expected_name: str
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        coordinator = self.company_generator.create_company(name=expected_name)
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        request = RequestCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert (
            self.get_latest_collaboration_request_email().coordinator_name
            == expected_name
        )

    def get_latest_collaboration_request_email(
        self,
    ) -> email_notifications.CollaborationRequestEmail:
        emails = self.get_collaboration_request_emails()
        assert emails
        return emails[-1]

    def get_collaboration_request_emails(
        self,
    ) -> list[email_notifications.CollaborationRequestEmail]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.CollaborationRequestEmail)
        ]
