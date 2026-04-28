from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from tests.datetime_service import datetime_utc
from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors import query_private_consumptions as interactor
from workers_control.web.www.presenters.private_consumptions_presenter import (
    PrivateConsumptionsPresenter,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(PrivateConsumptionsPresenter)

    def test_that_date_is_formatted_properly(self) -> None:
        response = self._response_with_plan_consumption(
            consumption_timestamp=datetime_utc(2000, 1, 1)
        )
        view_model = self.presenter.present_private_consumptions(response)
        self.assertEqual(
            view_model.consumptions[0].consumption_date,
            self.datetime_formatter.format_datetime(
                datetime_utc(2000, 1, 1),
                fmt="%d.%m.%Y",
            ),
        )

    def test_that_plan_consumption_type_is_translated_as_plan(self) -> None:
        response = self._response_with_plan_consumption()
        view_model = self.presenter.present_private_consumptions(response)
        self.assertEqual(
            view_model.consumptions[0].consumption_type,
            self.translator.gettext("Plan"),
        )

    def test_that_basic_service_consumption_type_is_translated(self) -> None:
        response = self._response_with_basic_service_consumption()
        view_model = self.presenter.present_private_consumptions(response)
        self.assertEqual(
            view_model.consumptions[0].consumption_type,
            self.translator.gettext("Basic service"),
        )

    def test_that_basic_service_consumption_shows_paid_price_total_as_rounded_hours_paid(
        self,
    ) -> None:
        response = self._response_with_basic_service_consumption(
            price_total=Decimal("3")
        )
        view_model = self.presenter.present_private_consumptions(response)
        self.assertEqual(view_model.consumptions[0].hours_paid, "3.00")

    def test_that_basic_service_consumption_uses_basic_service_name_and_description(
        self,
    ) -> None:
        response = self._response_with_basic_service_consumption(
            name="My Service", description="A nice service"
        )
        view_model = self.presenter.present_private_consumptions(response)
        consumption = view_model.consumptions[0]
        self.assertEqual(consumption.name, "My Service")
        self.assertEqual(consumption.description, "A nice service")

    def test_that_plan_consumption_has_a_details_url(self) -> None:
        consumption_id = uuid4()
        response = self._response_with_plan_consumption(consumption_id=consumption_id)
        view_model = self.presenter.present_private_consumptions(response)
        self.assertEqual(
            view_model.consumptions[0].details_url,
            self.url_index.get_my_private_consumption_details_url(
                consumption_id=consumption_id
            ),
        )

    def test_that_basic_service_consumption_has_no_details_url(self) -> None:
        response = self._response_with_basic_service_consumption()
        view_model = self.presenter.present_private_consumptions(response)
        self.assertIsNone(view_model.consumptions[0].details_url)

    def _response_with_plan_consumption(
        self,
        consumption_timestamp: datetime = datetime_utc(2020, 1, 1),
        consumption_id: UUID = uuid4(),
    ) -> interactor.Response:
        return interactor.Response(
            consumptions=[
                interactor.Consumption(
                    id=consumption_id,
                    consumption_type=interactor.ConsumptionType.plan,
                    consumption_date=consumption_timestamp,
                    name="test product",
                    description="test product description",
                    paid_price_total=Decimal("1"),
                )
            ]
        )

    def _response_with_basic_service_consumption(
        self,
        consumption_timestamp: datetime = datetime_utc(2020, 1, 1),
        price_total: Decimal = Decimal("1"),
        name: str = "Some Service",
        description: str = "A description",
    ) -> interactor.Response:
        return interactor.Response(
            consumptions=[
                interactor.Consumption(
                    id=uuid4(),
                    consumption_type=interactor.ConsumptionType.basic_service,
                    consumption_date=consumption_timestamp,
                    name=name,
                    description=description,
                    paid_price_total=price_total,
                )
            ]
        )
