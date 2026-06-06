from dataclasses import dataclass

from workers_control.core.interactors.get_plan_details import GetPlanDetailsInteractor
from workers_control.web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem

from ...translator import Translator


@dataclass
class GetPlanDetailsAccountantViewModel:
    details: PlanDetailsWeb


@dataclass
class GetPlanDetailsAccountantPresenter:
    trans: Translator
    plan_details_service: PlanDetailsFormatter
    url_index: UrlIndex

    def create_navbar_items(self) -> list[NavbarItem]:
        return [NavbarItem(text=self.trans.gettext("Plan information"), url=None)]

    def present(
        self, response: GetPlanDetailsInteractor.Response
    ) -> GetPlanDetailsAccountantViewModel:
        return GetPlanDetailsAccountantViewModel(
            details=self.plan_details_service.format_plan_details(
                response.plan_details
            ),
        )
