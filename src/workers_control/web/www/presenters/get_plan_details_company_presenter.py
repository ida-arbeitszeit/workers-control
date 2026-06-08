from dataclasses import dataclass

from workers_control.core.interactors.get_plan_details import GetPlanDetailsInteractor
from workers_control.web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from workers_control.web.translator import Translator
from workers_control.web.www.navbar import NavbarItem


@dataclass
class GetPlanDetailsCompanyViewModel:
    details: PlanDetailsWeb


@dataclass
class GetPlanDetailsCompanyPresenter:
    plan_details_service: PlanDetailsFormatter
    translator: Translator

    def create_navbar_items(self) -> list[NavbarItem]:
        return [NavbarItem(text=self.translator.gettext("Plan information"), url=None)]

    def present(
        self, response: GetPlanDetailsInteractor.Response
    ) -> GetPlanDetailsCompanyViewModel:
        return GetPlanDetailsCompanyViewModel(
            details=self.plan_details_service.format_plan_details(
                response.plan_details
            ),
        )
