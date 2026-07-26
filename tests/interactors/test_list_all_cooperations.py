from datetime import timedelta
from uuid import UUID

from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors.list_all_cooperations import (
    ListAllCooperationsInteractor,
    ListAllCooperationsResponse,
)


class ListAllCooperationsInteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListAllCooperationsInteractor)

    def coop_in_response(
        self, cooperation_id: UUID, response: ListAllCooperationsResponse
    ) -> bool:
        return any([coop.id == cooperation_id for coop in response.cooperations])

    def test_empty_list_is_returned_when_there_are_no_cooperations(
        self,
    ) -> None:
        response = self.interactor.execute()
        assert len(response.cooperations) == 0

    def test_one_empty_cooperation_is_returned_if_there_is_one_coop_without_plans(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        response = self.interactor.execute()
        assert len(response.cooperations) == 1
        assert response.cooperations[0].plan_count == 0
        assert self.coop_in_response(cooperation, response)

    def test_one_returned_cooperation_shows_correct_info(self) -> None:
        expected_cooperation_name = "Test Cooperation"
        plan = self.plan_generator.create_plan()
        cooperation = self.cooperation_generator.create_cooperation(
            plans=[plan], name=expected_cooperation_name
        )
        response = self.interactor.execute()
        assert len(response.cooperations) == 1
        assert self.coop_in_response(cooperation, response)
        assert response.cooperations[0].plan_count == 1
        assert response.cooperations[0].id == cooperation
        assert response.cooperations[0].name == expected_cooperation_name

    def test_one_cooperation_with_correct_plan_count_is_returned_if_there_is_one_coop_with_2_plans(
        self,
    ) -> None:
        plan1 = self.plan_generator.create_plan()
        plan2 = self.plan_generator.create_plan()
        cooperation = self.cooperation_generator.create_cooperation(
            plans=[plan1, plan2]
        )
        response = self.interactor.execute()
        assert response.cooperations[0].plan_count == 2
        assert self.coop_in_response(cooperation, response)

    def test_that_expired_plans_are_not_included_in_plan_count(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        plan = self.plan_generator.create_plan(timeframe=1)
        self.cooperation_generator.create_cooperation(plans=[plan])
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.execute()
        assert response.cooperations[0].plan_count == 0
