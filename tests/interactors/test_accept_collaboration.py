from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from tests.datetime_service import datetime_utc
from workers_control.core.interactors.accept_collaboration import (
    AcceptCollaborationInteractor,
    AcceptCollaborationRequest,
)
from workers_control.core.interactors.get_plan_details import GetPlanDetailsInteractor
from workers_control.core.records import ProductionCosts

from ..base_test_case import BaseTestCase


class AcceptCollaborationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accept_collaboration = self.injector.get(AcceptCollaborationInteractor)
        self.get_plan_details_interactor = self.injector.get(GetPlanDetailsInteractor)

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        requester = self.company_generator.create_company_record()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=uuid4(), collaboration_id=collaboration
        )
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_not_found

    def test_error_is_raised_when_collaboration_does_not_exist(self) -> None:
        requester = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan, collaboration_id=uuid4()
        )
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.collaboration_not_found
        )

    def test_error_is_raised_when_plan_is_already_in_collaboration(self) -> None:
        requester = self.company_generator.create_company_record()
        collaboration1 = self.collaboration_generator.create_collaboration()
        collaboration2 = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(collaboration=collaboration1)
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan, collaboration_id=collaboration2
        )
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_has_collaboration
        )

    def test_error_is_raised_when_plan_is_public_plan(self) -> None:
        requester = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan(is_public_service=True)
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan, collaboration_id=collaboration
        )
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_is_public_service
        )

    def test_error_is_raised_when_collaboration_was_not_requested(self) -> None:
        requester = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan, collaboration_id=collaboration
        )
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.collaboration_was_not_requested
        )

    def test_error_is_raised_when_requester_is_not_coordinator_of_collaboration(
        self,
    ) -> None:
        requester = self.company_generator.create_company_record()
        coordinator = self.company_generator.create_company_record()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        plan = self.plan_generator.create_plan(requested_collaboration=collaboration)
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan, collaboration_id=collaboration
        )
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_coordinator
        )

    def test_possible_to_add_plan_to_collaboration(self) -> None:
        requester = self.company_generator.create_company_record()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_collaboration=collaboration)
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan, collaboration_id=collaboration
        )
        response = self.accept_collaboration.execute(request)
        assert not response.is_rejected

    def test_collaboration_is_added_to_plan(self) -> None:
        requester = self.company_generator.create_company_record()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_collaboration=collaboration)
        request = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan, collaboration_id=collaboration
        )
        response = self.accept_collaboration.execute(request)
        assert not response.is_rejected
        self.assert_plan_in_collaboration(plan, collaboration)

    def test_two_collaborating_plans_have_same_prices(self) -> None:
        requester = self.company_generator.create_company_record()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(20), Decimal(30)),
            requested_collaboration=collaboration,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
            requested_collaboration=collaboration,
        )
        request1 = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan1, collaboration_id=collaboration
        )
        request2 = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan2, collaboration_id=collaboration
        )
        self.accept_collaboration.execute(request1)
        self.accept_collaboration.execute(request2)
        assert self.price_checker.get_price_per_unit(
            plan1
        ) == self.price_checker.get_price_per_unit(plan2)

    def test_price_of_collaborating_plans_is_correctly_calculated(self) -> None:
        requester = self.company_generator.create_company_record()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
            amount=10,
            requested_collaboration=collaboration,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(5), Decimal(3), Decimal(2)),
            amount=10,
            requested_collaboration=collaboration,
        )
        request1 = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan1, collaboration_id=collaboration
        )
        request2 = AcceptCollaborationRequest(
            requester_id=requester.id, plan_id=plan2, collaboration_id=collaboration
        )
        self.accept_collaboration.execute(request1)
        self.accept_collaboration.execute(request2)
        # In total costs of 30h and 20 units -> price should be 1.5h per unit
        assert (
            self.price_checker.get_price_per_unit(plan1)
            == self.price_checker.get_price_per_unit(plan2)
            == Decimal("1.5")
        )

    def test_that_collaboration_cannot_be_accepted_twice(self) -> None:
        requester = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_collaboration=collaboration)
        request = AcceptCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        self.accept_collaboration.execute(request)
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected

    def test_that_collaboration_cannot_be_accepted_for_expired_plans(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        requester = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            requested_collaboration=collaboration, timeframe=1
        )
        request = AcceptCollaborationRequest(
            requester_id=requester, plan_id=plan, collaboration_id=collaboration
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.accept_collaboration.execute(request)
        assert response.is_rejected

    def assert_plan_in_collaboration(self, plan: UUID, collaboration: UUID) -> None:
        request = GetPlanDetailsInteractor.Request(plan)
        summary_response = self.get_plan_details_interactor.get_plan_details(request)
        assert summary_response
        assert summary_response.plan_details
        assert summary_response.plan_details.collaboration == collaboration
