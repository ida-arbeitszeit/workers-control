from dataclasses import dataclass

from workers_control.core.interactors.get_productive_consumption_details import (
    GetProductiveConsumptionDetailsInteractor,
)
from workers_control.core.records import ConsumptionType
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.session import UserRole
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class ProductiveConsumptionDetailsPresenter:
    @dataclass
    class ViewModel:
        consumption_date: str
        plan_name: str
        plan_description: str
        consumption_type: str
        amount: str
        price_per_unit: str
        price_total: str
        plan_details_url: str
        navbar_items: list[NavbarItem]

    datetime_formatter: DatetimeFormatter
    translator: Translator
    url_index: UrlIndex

    def present(
        self, response: GetProductiveConsumptionDetailsInteractor.Response
    ) -> ViewModel:
        return self.ViewModel(
            consumption_date=self.datetime_formatter.format_datetime(
                date=response.consumption_date,
                fmt="%d.%m.%Y",
            ),
            plan_name=response.plan_name,
            plan_description=response.plan_description,
            consumption_type=self._format_consumption_type(response.consumption_type),
            amount=str(response.amount),
            price_per_unit=str(round(response.paid_price_per_unit, 2)),
            price_total=str(round(response.paid_price_total, 2)),
            plan_details_url=self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=response.plan_id
            ),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("My consumptions"),
                    url=self.url_index.get_company_consumptions_url(),
                ),
                NavbarItem(
                    text=self.translator.gettext("Consumption"),
                    url=None,
                ),
            ],
        )

    def _format_consumption_type(self, consumption_type: ConsumptionType) -> str:
        if consumption_type == ConsumptionType.raw_materials:
            return self.translator.gettext("Liquid means of production")
        else:
            return self.translator.gettext("Fixed means of production")
