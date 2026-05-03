from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from workers_control.core.interactors import show_payout_factor_details
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class ViewModel:
    navbar_items: list[NavbarItem]
    payout_factor: str
    window_size_in_days: str
    window_start: str
    window_end: str
    plot_url: str
    plans: list[PlanRow]
    basic_services_summary: str


@dataclass
class PlanRow:
    row_index: str
    shortened_plan_name: str
    plan_url: str
    is_public: bool
    coverage: str


@dataclass
class ShowPayoutFactorDetailsPresenter:
    datetime_formatter: DatetimeFormatter
    translator: Translator
    url_index: UrlIndex
    session: Session

    def present(self, response: show_payout_factor_details.Response) -> ViewModel:
        return ViewModel(
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Global statistics"),
                    url=self.url_index.get_global_statistics_url(),
                ),
                NavbarItem(
                    text=self.translator.gettext("Payout Factor Details"),
                    url=None,
                ),
            ],
            payout_factor=str(round(response.payout_factor, 2)),
            window_size_in_days=str(response.window_size_in_days),
            window_start=self.datetime_formatter.format_datetime(response.window_start),
            window_end=self.datetime_formatter.format_datetime(response.window_end),
            plot_url=self.url_index.get_payout_factor_details_bar_plot_url(),
            plans=[
                self._convert_plan(i, plan) for i, plan in enumerate(response.plans)
            ],
            basic_services_summary=self._build_basic_services_summary(
                response.basic_service_consumptions
            ),
        )

    def _build_basic_services_summary(
        self,
        consumptions: list[show_payout_factor_details.BasicServiceConsumptionData],
    ) -> str:
        count = len(consumptions)
        total_value = sum((c.value for c in consumptions), Decimal(0))
        return self.translator.gettext(
            "Basic services consumed in window: %(count)s" " (total hours: %(value)s)."
        ) % {"count": count, "value": f"{total_value:.2f}"}

    def _convert_plan(
        self, i: int, plan: show_payout_factor_details.PlanData
    ) -> PlanRow:
        user_role = self.session.get_user_role()
        return PlanRow(
            row_index=str(i),
            shortened_plan_name=plan.name[:30],
            plan_url=self.url_index.get_plan_details_url(
                user_role=user_role, plan_id=plan.id_
            ),
            is_public=plan.is_public_service,
            coverage=f"{plan.coverage * 100:.0f}%",
        )
