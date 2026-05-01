from dataclasses import dataclass

from workers_control.core.interactors import query_company_consumptions
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    @dataclass
    class Consumption:
        consumption_date: str
        product_name: str
        product_description: str
        consumption_type: str
        hours_paid: str
        details_url: str | None

    consumptions: list[Consumption]
    show_consumptions: bool


@dataclass
class CompanyConsumptionsPresenter:
    datetime_formatter: DatetimeFormatter
    translator: Translator
    url_index: UrlIndex

    def present(
        self, interactor_response: query_company_consumptions.Response
    ) -> ViewModel:
        consumptions = [
            self._format_consumption(consumption)
            for consumption in interactor_response.consumptions
        ]
        show_consumptions = True if (len(consumptions) > 0) else False
        return ViewModel(consumptions=consumptions, show_consumptions=show_consumptions)

    def _format_consumption(
        self, consumption: query_company_consumptions.Consumption
    ) -> ViewModel.Consumption:
        return ViewModel.Consumption(
            consumption_date=self.datetime_formatter.format_datetime(
                date=consumption.consumption_date,
                fmt="%d.%m.%Y",
            ),
            product_name=consumption.product_name,
            product_description=consumption.product_description,
            consumption_type=self._format_consumption_type(consumption.kind),
            hours_paid=str(round(consumption.paid_price_total, 2)),
            details_url=self._details_url(consumption),
        )

    def _format_consumption_type(
        self, kind: query_company_consumptions.ConsumptionKind
    ) -> str:
        if kind == query_company_consumptions.ConsumptionKind.plan_with_raw_materials:
            return self.translator.gettext("Liquid means of production")
        elif kind == query_company_consumptions.ConsumptionKind.plan_with_means_of_prod:
            return self.translator.gettext("Fixed means of production")
        else:
            return self.translator.gettext("Basic service")

    def _details_url(
        self, consumption: query_company_consumptions.Consumption
    ) -> str | None:
        if consumption.kind == query_company_consumptions.ConsumptionKind.basic_service:
            return None
        return self.url_index.get_company_consumption_details_url(
            consumption_id=consumption.id
        )
