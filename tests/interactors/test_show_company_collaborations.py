from datetime import timedelta
from uuid import uuid4

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_utc
from workers_control.core.interactors.show_company_collaborations import (
    Request,
    ShowCompanyCollaborationsInteractor,
)


class InboundCollaborationRequestsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ShowCompanyCollaborationsInteractor)

    def test_emtpy_list_is_returned_when_collaboration_is_not_found(self) -> None:
        response = self.interactor.show_company_collaborations(Request(uuid4()))
        assert len(response.inbound_collaboration_requests) == 0

    def test_empty_list_is_returned_when_there_are_no_requests_for_coordinator(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company_record()
        collab = self.collaboration_generator.create_collaboration()
        self.plan_generator.create_plan(requested_collaboration=collab)
        response = self.interactor.show_company_collaborations(Request(coordinator.id))
        assert len(response.inbound_collaboration_requests) == 0

    def test_correct_plans_are_returned_when_plans_request_collaboration(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company()
        collab = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        requesting_plan1 = self.plan_generator.create_plan(
            requested_collaboration=collab
        )
        requesting_plan2 = self.plan_generator.create_plan(
            requested_collaboration=collab
        )
        response = self.interactor.show_company_collaborations(Request(coordinator))
        assert len(response.inbound_collaboration_requests) == 2
        assert requesting_plan1 in [
            request.plan_id for request in response.inbound_collaboration_requests
        ]
        assert requesting_plan2 in [
            request.plan_id for request in response.inbound_collaboration_requests
        ]

    def test_that_requests_for_expired_plans_are_not_shown(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        coordinator = self.company_generator.create_company_record()
        collab = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        self.plan_generator.create_plan(requested_collaboration=collab, timeframe=1)
        self.plan_generator.create_plan(requested_collaboration=collab, timeframe=5)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.show_company_collaborations(Request(coordinator.id))
        assert len(response.inbound_collaboration_requests) == 1


class OutboundCollabRequestsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ShowCompanyCollaborationsInteractor)

    def test_emtpy_list_is_returned_when_collaboration_is_not_found(self) -> None:
        response = self.interactor.show_company_collaborations(Request(uuid4()))
        self.assertEqual(len(response.outbound_collaboration_requests), 0)

    def test_empty_list_is_returned_when_there_are_no_outbound_requests(self) -> None:
        requester = self.company_generator.create_company()
        collab = self.collaboration_generator.create_collaboration()
        self.plan_generator.create_plan(requested_collaboration=collab)
        response = self.interactor.show_company_collaborations(Request(requester))
        self.assertEqual(len(response.outbound_collaboration_requests), 0)

    def test_correct_plans_are_returned_when_there_are_outbound_requests(self) -> None:
        requester = self.company_generator.create_company()
        collab = self.collaboration_generator.create_collaboration()
        requesting_plan1 = self.plan_generator.create_plan(
            requested_collaboration=collab, planner=requester
        )
        requesting_plan2 = self.plan_generator.create_plan(
            requested_collaboration=collab, planner=requester
        )
        response = self.interactor.show_company_collaborations(Request(requester))
        self.assertEqual(len(response.outbound_collaboration_requests), 2)
        assert requesting_plan1 in [
            request.plan_id for request in response.outbound_collaboration_requests
        ]
        assert requesting_plan2 in [
            request.plan_id for request in response.outbound_collaboration_requests
        ]

    def test_that_requests_for_expired_plans_are_not_shown(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        requester = self.company_generator.create_company()
        collab = self.collaboration_generator.create_collaboration()
        self.plan_generator.create_plan(
            requested_collaboration=collab, planner=requester, timeframe=1
        )
        self.plan_generator.create_plan(
            requested_collaboration=collab, planner=requester, timeframe=5
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.show_company_collaborations(Request(requester))
        self.assertEqual(len(response.outbound_collaboration_requests), 1)
