from datetime import timedelta
from uuid import uuid4

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_utc
from workers_control.core.interactors.list_coordinations_of_company import (
    ListCoordinationsOfCompanyInteractor,
    ListCoordinationsOfCompanyRequest,
)


class ListCoordinationsOfCompanyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListCoordinationsOfCompanyInteractor)

    def test_empty_list_is_returned_if_requesting_company_does_not_exist(
        self,
    ) -> None:
        response = self.interactor.execute(
            ListCoordinationsOfCompanyRequest(company=uuid4())
        )
        assert len(response.coordinations) == 0

    def test_empty_list_is_returned_when_plans_are_not_collaborating(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        response = self.interactor.execute(
            ListCoordinationsOfCompanyRequest(company.id)
        )
        assert len(response.coordinations) == 0

    def test_empty_list_is_returned_when_requester_is_not_coordinator_of_collaboration(
        self,
    ) -> None:
        p1 = self.plan_generator.create_plan()
        p2 = self.plan_generator.create_plan()
        self.collaboration_generator.create_collaboration(plans=[p1, p2])
        company = self.company_generator.create_company_record()
        response = self.interactor.execute(
            ListCoordinationsOfCompanyRequest(company.id)
        )
        assert len(response.coordinations) == 0

    def test_collaboration_is_listed_when_requester_is_coordinator_of_collaboration(
        self,
    ) -> None:
        p1 = self.plan_generator.create_plan()
        p2 = self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        collaboration = self.collaboration_generator.create_collaboration(
            plans=[p1, p2], coordinator=company
        )
        response = self.interactor.execute(
            ListCoordinationsOfCompanyRequest(company.id)
        )
        assert len(response.coordinations) == 1
        assert response.coordinations[0].id == collaboration

    def test_only_collaborations_are_listed_where_requester_is_coordinator(
        self,
    ) -> None:
        p1 = self.plan_generator.create_plan()
        p2 = self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        expected_collaboration = self.collaboration_generator.create_collaboration(
            plans=[p1, p2], coordinator=company
        )
        self.collaboration_generator.create_collaboration()
        response = self.interactor.execute(
            ListCoordinationsOfCompanyRequest(company.id)
        )
        assert len(response.coordinations) == 1
        assert response.coordinations[0].id == expected_collaboration

    def test_that_expired_plans_are_not_counted_in_collaborations(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        coordinator = self.company_generator.create_company_record()
        p1 = self.plan_generator.create_plan(timeframe=1)
        p2 = self.plan_generator.create_plan(timeframe=5)
        self.collaboration_generator.create_collaboration(
            plans=[p1, p2], coordinator=coordinator
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.execute(
            ListCoordinationsOfCompanyRequest(coordinator.id)
        )
        assert response.coordinations[0].count_plans_in_collab == 1
