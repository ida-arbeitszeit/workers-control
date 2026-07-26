from typing import Optional
from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.list_plans_with_pending_review import (
    ListPlansWithPendingReviewInteractor as Interactor,
)
from workers_control.web.www.presenters.list_plans_with_pending_review_presenter import (
    ListPlansWithPendingReviewPresenter,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListPlansWithPendingReviewPresenter)

    def test_that_plan_overview_is_not_shown_when_there_are_no_plans_in_response(
        self,
    ) -> None:
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_empty_response()
        )
        self.assertFalse(view_model.show_plan_list)

    def test_that_plan_overview_is_shown_when_there_is_one_plan_in_response(
        self,
    ) -> None:
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan()
        )
        self.assertTrue(view_model.show_plan_list)

    def test_that_product_name_is_listed_correctly_with_one_plan(self) -> None:
        expected_product_name = "test product name"
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan(product_name=expected_product_name)
        )
        self.assertEqual(view_model.plans[0].product_name, expected_product_name)

    def test_that_planner_name_is_listed_correctly_with_one_plan(self) -> None:
        expected_planner_name = "test planner name 123"
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan(planner_name=expected_planner_name)
        )
        self.assertEqual(view_model.plans[0].planner_name, expected_planner_name)

    def test_that_review_url_is_set_correctly(self) -> None:
        plan_id = uuid4()
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan(plan_id=plan_id)
        )
        assert view_model.plans[
            0
        ].review_plan_url == self.url_index.get_plan_review_url(plan_id)

    def test_that_plan_details_url_is_set_correctly(self) -> None:
        plan_id = uuid4()
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan(plan_id=plan_id)
        )
        assert view_model.plans[
            0
        ].plan_details_url == self.url_index.get_plan_details_url(plan_id=plan_id)

    def test_that_company_summary_url_is_set_correctly(self) -> None:
        planner_id = uuid4()
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan(planner_id=planner_id)
        )
        assert view_model.plans[
            0
        ].company_summary_url == self.url_index.get_company_summary_url(
            company_id=planner_id
        )

    def _get_empty_response(self) -> Interactor.Response:
        return Interactor.Response(plans=[])

    def _get_response_with_one_plan(
        self,
        *,
        product_name: str = "test product",
        planner_name: str = "example company",
        plan_id: Optional[UUID] = None,
        planner_id: Optional[UUID] = None,
    ) -> Interactor.Response:
        if plan_id is None:
            plan_id = uuid4()
        if planner_id is None:
            planner_id = uuid4()
        return Interactor.Response(
            plans=[
                Interactor.Plan(
                    id=plan_id,
                    product_name=product_name,
                    planner_name=planner_name,
                    planner_id=planner_id,
                )
            ]
        )


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListPlansWithPendingReviewPresenter)

    def test_navbar_shows_list_unreviewed_plans_as_current_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0].text, self.translator.gettext("List unreviewed plans")
        )
        self.assertIsNone(items[0].url)
