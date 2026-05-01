from decimal import Decimal
from uuid import UUID, uuid4

from tests.data_generators import ConsumptionGenerator
from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.query_company_consumptions import (
    Consumption,
    ConsumptionKind,
    QueryCompanyConsumptionsInteractor,
    Response,
)
from workers_control.web.www.presenters.company_consumptions_presenter import (
    CompanyConsumptionsPresenter,
    ViewModel,
)


class TestPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_consumptions = self.injector.get(QueryCompanyConsumptionsInteractor)
        self.consumption_generator = self.injector.get(ConsumptionGenerator)
        self.presenter = self.injector.get(CompanyConsumptionsPresenter)

    def test_show_consumptions_from_company(self) -> None:
        now = self.datetime_service.now()
        response = Response(
            consumptions=[
                Consumption(
                    id=uuid4(),
                    consumption_date=now,
                    plan_id=uuid4(),
                    product_name="Produkt A",
                    product_description="Beschreibung für Produkt A.",
                    kind=ConsumptionKind.plan_with_raw_materials,
                    paid_price_total=Decimal("2532.69"),
                ),
                Consumption(
                    id=uuid4(),
                    consumption_date=now,
                    plan_id=uuid4(),
                    product_name="Produkt A",
                    product_description="Beschreibung für Produkt A.",
                    kind=ConsumptionKind.plan_with_means_of_prod,
                    paid_price_total=Decimal("100000"),
                ),
            ]
        )
        presentation = self.presenter.present(response)  # DUT

        assert isinstance(presentation, ViewModel)

        assert presentation.consumptions[
            0
        ].consumption_date == self.datetime_formatter.format_datetime(
            now, fmt="%d.%m.%Y"
        )
        assert presentation.consumptions[0].product_name == "Produkt A"
        assert (
            presentation.consumptions[0].product_description
            == "Beschreibung für Produkt A."
        )
        assert presentation.consumptions[0].consumption_type == self.translator.gettext(
            "Liquid means of production"
        )
        assert presentation.consumptions[0].hours_paid == "2532.69"

        assert presentation.consumptions[
            1
        ].consumption_date == self.datetime_formatter.format_datetime(
            now, fmt="%d.%m.%Y"
        )
        assert presentation.consumptions[1].product_name == "Produkt A"
        assert (
            presentation.consumptions[1].product_description
            == "Beschreibung für Produkt A."
        )
        assert presentation.consumptions[1].consumption_type == self.translator.gettext(
            "Fixed means of production"
        )
        assert presentation.consumptions[1].hours_paid == "100000.00"

    def test_show_consumptions_if_there_is_one_consumption(self) -> None:
        consuming_company = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consuming_company
        )
        interactor_response = self.query_consumptions.execute(company=consuming_company)
        view_model = self.presenter.present(interactor_response)
        assert view_model.show_consumptions

    def test_do_not_show_consumptions_if_there_is_no_consumption_of_querying_company(
        self,
    ) -> None:
        interactor_response = Response(consumptions=[])
        view_model = self.presenter.present(interactor_response)
        assert not view_model.show_consumptions

    def test_that_details_url_points_to_company_consumption_details(self) -> None:
        consumption_id = uuid4()
        response = self._response_with_one_plan_consumption(
            consumption_id=consumption_id
        )
        view_model = self.presenter.present(response)
        assert view_model.consumptions[
            0
        ].details_url == self.url_index.get_company_consumption_details_url(
            consumption_id=consumption_id
        )

    def test_basic_service_consumption_renders_consumption_type_label(self) -> None:
        response = self._response_with_one_basic_service_consumption()
        view_model = self.presenter.present(response)
        assert view_model.consumptions[0].consumption_type == self.translator.gettext(
            "Basic service"
        )

    def test_basic_service_consumption_has_no_details_url(self) -> None:
        response = self._response_with_one_basic_service_consumption()
        view_model = self.presenter.present(response)
        assert view_model.consumptions[0].details_url is None

    def test_basic_service_consumption_uses_total_price_for_hours_paid(self) -> None:
        response = self._response_with_one_basic_service_consumption(
            paid_price_total=Decimal("12.34")
        )
        view_model = self.presenter.present(response)
        assert view_model.consumptions[0].hours_paid == "12.34"

    def _response_with_one_plan_consumption(self, consumption_id: UUID) -> Response:
        return Response(
            consumptions=[
                Consumption(
                    id=consumption_id,
                    consumption_date=self.datetime_service.now(),
                    plan_id=uuid4(),
                    product_name="Produkt A",
                    product_description="Beschreibung für Produkt A.",
                    kind=ConsumptionKind.plan_with_raw_materials,
                    paid_price_total=Decimal("1"),
                )
            ]
        )

    def _response_with_one_basic_service_consumption(
        self, paid_price_total: Decimal = Decimal("1")
    ) -> Response:
        return Response(
            consumptions=[
                Consumption(
                    id=uuid4(),
                    consumption_date=self.datetime_service.now(),
                    plan_id=None,
                    product_name="My Basic Service",
                    product_description="A description.",
                    kind=ConsumptionKind.basic_service,
                    paid_price_total=paid_price_total,
                )
            ]
        )
