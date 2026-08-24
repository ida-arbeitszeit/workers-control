from typing import Optional
from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.list_all_cooperations import (
    ListAllCooperationsResponse,
    ListedCooperation,
)
from workers_control.web.www.presenters.list_all_collaborations_presenter import (
    ListAllCollaborationsPresenter,
)


class ListMessagesPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListAllCollaborationsPresenter)
        self.session.login_company(company=uuid4())

    def test_view_model_contains_no_collaboration_and_does_not_show_result_when_non_were_provided(
        self,
    ) -> None:
        response = ListAllCooperationsResponse(cooperations=[])
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_results)
        self.assertFalse(view_model.collaborations)

    def test_view_model_contains_and_shows_collab_when_one_was_provided(self) -> None:
        response = self._create_response_with_one_collaboration()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.collaborations)
        self.assertTrue(view_model.show_results)

    def test_name_is_propagated_to_view_model(self) -> None:
        expected_name = "test123"
        view_model = self.presenter.present(
            self._create_response_with_one_collaboration(name=expected_name)
        )
        self.assertEqual(view_model.collaborations[0].name, expected_name)

    def test_plan_count_is_propagated_to_view_model(self) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_collaboration(plan_count=10)
        )
        self.assertEqual(view_model.collaborations[0].plan_count, "10")

    def test_correct_collab_summary_url_is_displayed_in_view_model(self) -> None:
        collab_id = uuid4()
        expected_url = self.url_index.get_collab_summary_url(collab_id=collab_id)
        view_model = self.presenter.present(
            self._create_response_with_one_collaboration(collab_id=collab_id)
        )
        self.assertEqual(expected_url, view_model.collaborations[0].collab_summary_url)

    def _create_response_with_one_collaboration(
        self,
        collab_id: Optional[UUID] = None,
        name: str = "collab name",
        plan_count: int = 3,
    ) -> ListAllCooperationsResponse:
        if collab_id is None:
            collab_id = uuid4()
        return ListAllCooperationsResponse(
            cooperations=[
                ListedCooperation(
                    id=collab_id,
                    name=name,
                    plan_count=plan_count,
                )
            ]
        )


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListAllCollaborationsPresenter)

    def test_navbar_shows_all_collaborations_as_current_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].text, self.translator.gettext("All collaborations"))
        self.assertIsNone(items[0].url)
