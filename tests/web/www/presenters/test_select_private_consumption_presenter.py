from uuid import UUID, uuid4

from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors import select_private_consumption
from workers_control.web.www.presenters.select_private_consumption_presenter import (
    SelectPrivateConsumptionPresenter,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(SelectPrivateConsumptionPresenter)

    @parameterized.expand([(None,), (5,), (10,)])
    def test_that_no_plan_response_gets_rendered_correctly(
        self, amount: int | None
    ) -> None:
        response = select_private_consumption.NoPlanResponse(amount=amount)
        view_model = self.presenter.render_response(response)
        assert view_model.valid_plan_selected is False
        assert view_model.plan_id is None
        assert view_model.plan_name is None
        assert view_model.plan_description is None
        assert view_model.amount == amount
        assert view_model.status_code == 200

    def test_that_warning_is_displayed_when_plan_is_invalid(self) -> None:
        assert not self.notifier.warnings
        response = select_private_consumption.InvalidPlanResponse(amount=5)
        self.presenter.render_response(response)
        assert self.notifier.warnings

    @parameterized.expand([(None,), (5,), (10,)])
    def test_that_invalid_plan_response_gets_rendered_correctly(
        self, amount: int | None
    ) -> None:
        response = select_private_consumption.InvalidPlanResponse(amount=amount)
        view_model = self.presenter.render_response(response)
        assert view_model.valid_plan_selected is False
        assert view_model.plan_id is None
        assert view_model.plan_name is None
        assert view_model.plan_description is None
        assert view_model.amount == amount
        assert view_model.status_code == 404

    @parameterized.expand(
        [
            (uuid4(), 5, "Plan Name", "Plan Description"),
            (uuid4(), 10, "Plan Name", "Plan Description"),
            (uuid4(), None, "Plan Name", "Plan Description"),
        ]
    )
    def test_that_valid_plan_response_gets_rendered_correctly(
        self,
        plan_id: UUID,
        amount: int | None,
        plan_name: str,
        plan_description: str,
    ) -> None:
        response = select_private_consumption.ValidPlanResponse(
            plan_id=plan_id,
            amount=amount,
            plan_name=plan_name,
            plan_description=plan_description,
        )
        view_model = self.presenter.render_response(response)
        assert view_model.valid_plan_selected is True
        assert view_model.plan_id == str(plan_id)
        assert view_model.plan_name == plan_name
        assert view_model.plan_description == plan_description
        assert view_model.amount == amount
        assert view_model.status_code == 200
