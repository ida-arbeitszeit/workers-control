from datetime import timedelta
from uuid import UUID

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_utc
from workers_control.core.interactors.list_all_collaborations import (
    ListAllCollaborationsInteractor,
    ListAllCollaborationsResponse,
)


class ListAllCollaborationsInteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListAllCollaborationsInteractor)

    def collab_in_response(
        self, collaboration_id: UUID, response: ListAllCollaborationsResponse
    ) -> bool:
        return any(
            [collab.id == collaboration_id for collab in response.collaborations]
        )

    def test_empty_list_is_returned_when_there_are_no_collaborations(
        self,
    ) -> None:
        response = self.interactor.execute()
        assert len(response.collaborations) == 0

    def test_one_empty_collaboration_is_returned_if_there_is_one_collab_without_plans(
        self,
    ) -> None:
        collaboration = self.collaboration_generator.create_collaboration()
        response = self.interactor.execute()
        assert len(response.collaborations) == 1
        assert response.collaborations[0].plan_count == 0
        assert self.collab_in_response(collaboration, response)

    def test_one_returned_collaboration_shows_correct_info(self) -> None:
        expected_collaboration_name = "Test Collaboration"
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(
            plans=[plan], name=expected_collaboration_name
        )
        response = self.interactor.execute()
        assert len(response.collaborations) == 1
        assert self.collab_in_response(collaboration, response)
        assert response.collaborations[0].plan_count == 1
        assert response.collaborations[0].id == collaboration
        assert response.collaborations[0].name == expected_collaboration_name

    def test_one_collaboration_with_correct_plan_count_is_returned_if_there_is_one_collab_with_2_plans(
        self,
    ) -> None:
        plan1 = self.plan_generator.create_plan()
        plan2 = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(
            plans=[plan1, plan2]
        )
        response = self.interactor.execute()
        assert response.collaborations[0].plan_count == 2
        assert self.collab_in_response(collaboration, response)

    def test_that_expired_plans_are_not_included_in_plan_count(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        plan = self.plan_generator.create_plan(timeframe=1)
        self.collaboration_generator.create_collaboration(plans=[plan])
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.execute()
        assert response.collaborations[0].plan_count == 0
