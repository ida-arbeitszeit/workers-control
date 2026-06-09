from uuid import UUID, uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.get_plan_for_review import (
    GetPlanForReviewInteractor as Interactor,
)
from workers_control.web.www.presenters.get_plan_for_review_presenter import (
    GetPlanForReviewPresenter,
)


class GetPlanForReviewPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPlanForReviewPresenter)

    def test_that_product_name_is_shown(self) -> None:
        view_model = self.presenter.present(self._response(product_name="test product"))
        assert view_model.product_name == "test product"

    def test_that_plan_details_url_is_set_correctly(self) -> None:
        plan_id = uuid4()
        view_model = self.presenter.present(self._response(plan_id=plan_id))
        assert view_model.plan_details_url == self.url_index.get_plan_details_url(
            plan_id=plan_id
        )

    def test_that_review_form_action_url_is_set_correctly(self) -> None:
        plan_id = uuid4()
        view_model = self.presenter.present(self._response(plan_id=plan_id))
        assert view_model.review_form_action_url == self.url_index.get_plan_review_url(
            plan_id
        )

    def test_that_navbar_links_back_to_the_unreviewed_plans_list(self) -> None:
        view_model = self.presenter.present(self._response())
        assert (
            view_model.navbar_items[0].url
            == self.url_index.get_unreviewed_plans_list_view_url()
        )

    def test_that_current_page_is_the_last_navbar_item_without_a_link(self) -> None:
        view_model = self.presenter.present(self._response())
        assert view_model.navbar_items[-1].url is None

    def _response(
        self,
        *,
        product_name: str = "test product",
        plan_id: UUID | None = None,
    ) -> Interactor.Response:
        if plan_id is None:
            plan_id = uuid4()
        return Interactor.Response(plan_id=plan_id, product_name=product_name)
