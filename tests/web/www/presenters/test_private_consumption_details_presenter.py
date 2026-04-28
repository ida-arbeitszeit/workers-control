from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from tests.datetime_service import datetime_utc
from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.get_private_consumption_details import (
    GetPrivateConsumptionDetailsInteractor,
)
from workers_control.web.session import UserRole
from workers_control.web.www.presenters.private_consumption_details_presenter import (
    PrivateConsumptionDetailsPresenter,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(PrivateConsumptionDetailsPresenter)

    def test_that_date_is_formatted_properly(self) -> None:
        response = self._response(consumption_date=datetime_utc(2000, 1, 1))
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.consumption_date,
            self.datetime_formatter.format_datetime(
                datetime_utc(2000, 1, 1),
                fmt="%d.%m.%Y",
            ),
        )

    def test_that_plan_name_and_description_are_passed_through(self) -> None:
        response = self._response(plan_name="Bread", plan_description="Tasty")
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.plan_name, "Bread")
        self.assertEqual(view_model.plan_description, "Tasty")

    def test_that_amount_is_formatted_as_string(self) -> None:
        response = self._response(amount=5)
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.amount, "5")

    def test_that_price_per_unit_is_formatted_as_rounded_string(self) -> None:
        response = self._response(paid_price_per_unit=Decimal("2.5"))
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.price_per_unit, "2.50")

    def test_that_price_total_is_formatted_as_rounded_string(self) -> None:
        response = self._response(paid_price_total=Decimal("12"))
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.price_total, "12.00")

    def test_that_plan_details_url_points_to_member_plan_details_view(self) -> None:
        plan_id = uuid4()
        response = self._response(plan_id=plan_id)
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.plan_details_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.member, plan_id=plan_id
            ),
        )

    def _response(
        self,
        consumption_date: datetime = datetime_utc(2020, 1, 1),
        plan_id: UUID = uuid4(),
        plan_name: str = "Some product",
        plan_description: str = "Some description",
        amount: int = 1,
        paid_price_per_unit: Decimal = Decimal("1"),
        paid_price_total: Decimal = Decimal("1"),
    ) -> GetPrivateConsumptionDetailsInteractor.Response:
        return GetPrivateConsumptionDetailsInteractor.Response(
            consumption_date=consumption_date,
            plan_id=plan_id,
            plan_name=plan_name,
            plan_description=plan_description,
            amount=amount,
            paid_price_per_unit=paid_price_per_unit,
            paid_price_total=paid_price_total,
        )
