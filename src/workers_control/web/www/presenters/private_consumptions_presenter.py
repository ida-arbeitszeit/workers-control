from dataclasses import dataclass
from typing import List, Optional

from workers_control.core.interactors.query_private_consumptions import (
    Consumption,
    ConsumptionType,
    Response,
)
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class PrivateConsumptionsPresenter:
    @dataclass
    class ViewModel:
        @dataclass
        class Consumption:
            consumption_type: str
            consumption_date: str
            name: str
            description: str
            hours_paid: str
            details_url: Optional[str]

        is_consumptions_visible: bool
        consumptions: List[Consumption]

    datetime_formatter: DatetimeFormatter
    translator: Translator
    url_index: UrlIndex

    def present_private_consumptions(self, response: Response) -> ViewModel:
        return self.ViewModel(
            is_consumptions_visible=bool(response.consumptions),
            consumptions=[
                self._present_consumption(consumption)
                for consumption in response.consumptions
            ],
        )

    def _present_consumption(self, consumption: Consumption) -> ViewModel.Consumption:
        return self.ViewModel.Consumption(
            consumption_type=self._format_type(consumption.consumption_type),
            consumption_date=self.datetime_formatter.format_datetime(
                date=consumption.consumption_date,
                fmt="%d.%m.%Y",
            ),
            name=consumption.name,
            description=consumption.description,
            hours_paid=str(round(consumption.paid_price_total, 2)),
            details_url=(
                self.url_index.get_my_private_consumption_details_url(
                    consumption_id=consumption.id
                )
                if consumption.consumption_type == ConsumptionType.plan
                else None
            ),
        )

    def _format_type(self, consumption_type: ConsumptionType) -> str:
        match consumption_type:
            case ConsumptionType.plan:
                return self.translator.gettext("Plan")
            case ConsumptionType.basic_service:
                return self.translator.gettext("Basic service")
