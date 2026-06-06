from uuid import uuid4

from workers_control.core.interactors.get_plan_for_review import (
    GetPlanForReviewInteractor,
)

from .base_test_case import BaseTestCase


class GetPlanForReviewInteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetPlanForReviewInteractor)

    def test_that_none_is_returned_for_a_nonexistent_plan(self) -> None:
        response = self.interactor.get_plan_for_review(
            GetPlanForReviewInteractor.Request(plan=uuid4())
        )
        assert response is None

    def test_that_an_existing_plan_is_returned(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.interactor.get_plan_for_review(
            GetPlanForReviewInteractor.Request(plan=plan)
        )
        assert response is not None
        assert response.plan_id == plan

    def test_that_the_product_name_of_the_plan_is_returned(self) -> None:
        plan = self.plan_generator.create_plan(product_name="test product name")
        response = self.interactor.get_plan_for_review(
            GetPlanForReviewInteractor.Request(plan=plan)
        )
        assert response is not None
        assert response.product_name == "test product name"
