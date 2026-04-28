from dataclasses import dataclass

from workers_control.core.interactors.get_private_consumption_details import (
    GetPrivateConsumptionDetailsInteractor,
)
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.session import UserRole
from workers_control.web.url_index import UrlIndex


@dataclass
class PrivateConsumptionDetailsPresenter:
    @dataclass
    class ViewModel:
        consumption_date: str
        plan_name: str
        plan_description: str
        amount: str
        price_per_unit: str
        price_total: str
        plan_details_url: str

    datetime_formatter: DatetimeFormatter
    url_index: UrlIndex

    def present(
        self, response: GetPrivateConsumptionDetailsInteractor.Response
    ) -> ViewModel:
        return self.ViewModel(
            consumption_date=self.datetime_formatter.format_datetime(
                date=response.consumption_date,
                fmt="%d.%m.%Y",
            ),
            plan_name=response.plan_name,
            plan_description=response.plan_description,
            amount=str(response.amount),
            price_per_unit=str(round(response.paid_price_per_unit, 2)),
            price_total=str(round(response.paid_price_total, 2)),
            plan_details_url=self.url_index.get_plan_details_url(
                user_role=UserRole.member, plan_id=response.plan_id
            ),
        )
