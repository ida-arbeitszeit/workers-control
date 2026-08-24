from datetime import datetime
from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_utc
from workers_control.core.interactors.list_coordinations_of_collaboration import (
    CoordinationInfo,
    ListCoordinationsOfCollaborationInteractor,
)
from workers_control.web.www.presenters.list_coordinations_of_collaboration_presenter import (
    ListCoordinationsOfCollaborationPresenter,
)


class ListCoordinationsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListCoordinationsOfCollaborationPresenter)

    def test_presenter_shows_correct_collaboration_name(self) -> None:
        expected_collaboration_name = "Some collab test name"
        response = self.get_interactor_response_with_one_coordination(
            collaboration_name=expected_collaboration_name
        )
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(view_model.collaboration_name, expected_collaboration_name)

    def test_presenter_shows_correct_collaboration_url(self) -> None:
        expected_collaboration = uuid4()
        expected_url = self.url_index.get_collab_summary_url(
            collab_id=expected_collaboration
        )
        response = self.get_interactor_response_with_one_coordination(
            collaboration_id=expected_collaboration
        )
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(view_model.collaboration_url, expected_url)

    def test_presenter_shows_no_coordinations_when_interactor_response_has_none(
        self,
    ) -> None:
        response = self.get_interactor_response_with_zero_coordinations()
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertFalse(view_model.has_coordinations)

    def test_presenter_shows_coordinations_when_interactor_response_has_some(
        self,
    ) -> None:
        response = self.get_interactor_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertTrue(view_model.has_coordinations)

    def test_presenter_shows_one_coordinations_when_interactor_response_has_one(
        self,
    ) -> None:
        response = self.get_interactor_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertTrue(view_model.has_coordinations)
        self.assertEqual(len(view_model.coordinations), 1)

    def test_presenter_shows_correct_coordinator_name(self) -> None:
        response = self.get_interactor_response_with_one_coordination(
            coordinator_name="fake coordinator name"
        )
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(
            view_model.coordinations[0].coordinator_name, "fake coordinator name"
        )

    def test_presenter_shows_correct_coordinator_url(self) -> None:
        expected_coordinator = uuid4()
        expected_url = self.url_index.get_company_summary_url(
            company_id=expected_coordinator
        )
        response = self.get_interactor_response_with_one_coordination(
            coordinator_id=expected_coordinator
        )
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(view_model.coordinations[0].coordinator_url, expected_url)

    def test_presenter_shows_correct_start_time(self) -> None:
        expected_start_time = datetime_utc(2020, 1, 1, 12, 0)
        expected_formatted_start_time = self.datetime_formatter.format_datetime(
            date=expected_start_time,
            fmt="%d.%m.%Y %H:%M",
        )
        response = self.get_interactor_response_with_one_coordination(
            start_time=expected_start_time
        )
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(
            view_model.coordinations[0].start_time, expected_formatted_start_time
        )

    def test_presenter_shows_correct_end_time_if_coordination_has_none(self) -> None:
        response = ListCoordinationsOfCollaborationInteractor.Response(
            coordinations=[
                CoordinationInfo(
                    coordinator_id=uuid4(),
                    coordinator_name="fake name",
                    start_time=datetime_utc(2020, 1, 1, 12, 0),
                    end_time=None,
                )
            ],
            collaboration_id=uuid4(),
            collaboration_name="Some collab test name",
        )
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(view_model.coordinations[0].end_time, "-")

    def test_presenter_shows_correct_end_time_if_coordination_has_some(self) -> None:
        expected_end_time = datetime_utc(2022, 3, 10, 13, 0)
        expected_formatted_end_time = self.datetime_formatter.format_datetime(
            date=expected_end_time,
            fmt="%d.%m.%Y %H:%M",
        )
        response = self.get_interactor_response_with_one_coordination(
            end_time=expected_end_time
        )
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(
            view_model.coordinations[0].end_time, expected_formatted_end_time
        )

    def test_presenter_shows_correct_amount_of_navbar_items(self) -> None:
        response = self.get_interactor_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(len(view_model.navbar_items), 2)

    def test_first_navbar_item_is_correct(self) -> None:
        response = self.get_interactor_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(
            view_model.navbar_items[0].url,
            self.url_index.get_collab_summary_url(
                collab_id=response.collaboration_id,
            ),
        )
        self.assertEqual(
            view_model.navbar_items[0].text, self.translator.gettext("Collaboration")
        )

    def test_second_navbar_item_is_correct(self) -> None:
        response = self.get_interactor_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_collaboration(response)
        self.assertEqual(view_model.navbar_items[1].url, None)
        self.assertEqual(
            view_model.navbar_items[1].text, self.translator.gettext("Coordinators")
        )

    def get_interactor_response_with_zero_coordinations(
        self,
    ) -> ListCoordinationsOfCollaborationInteractor.Response:
        return ListCoordinationsOfCollaborationInteractor.Response(
            coordinations=[],
            collaboration_id=uuid4(),
            collaboration_name="Some collab test name",
        )

    def get_interactor_response_with_one_coordination(
        self,
        coordinator_id: UUID = uuid4(),
        coordinator_name: str = "fake coordinator name",
        start_time: datetime = datetime_utc(2020, 1, 1, 12, 0),
        end_time: datetime = datetime_utc(2022, 3, 10, 13, 0),
        collaboration_id: UUID = uuid4(),
        collaboration_name: str = "Some collab test name",
    ) -> ListCoordinationsOfCollaborationInteractor.Response:
        return ListCoordinationsOfCollaborationInteractor.Response(
            coordinations=[
                CoordinationInfo(
                    coordinator_id=coordinator_id,
                    coordinator_name=coordinator_name,
                    start_time=start_time,
                    end_time=end_time,
                )
            ],
            collaboration_id=collaboration_id,
            collaboration_name=collaboration_name,
        )
