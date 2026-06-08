from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors.get_plan_details import GetPlanDetailsInteractor
from workers_control.core.services.plan_details import PlanDetails
from workers_control.web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.www.navbar import NavbarItem

from ...url_index import UrlIndex


@dataclass
class OwnPlanAction:
    is_cooperating: bool
    plan_id: str
    cooperation_id: str | None
    request_coop_url: Optional[str]


@dataclass
class GetPlanDetailsCompanyViewModel:
    details: PlanDetailsWeb
    show_own_plan_action_section: bool
    own_plan_action: OwnPlanAction


@dataclass
class GetPlanDetailsCompanyPresenter:
    plan_details_service: PlanDetailsFormatter
    url_index: UrlIndex
    session: Session
    translator: Translator

    def create_navbar_items(self) -> list[NavbarItem]:
        return [NavbarItem(text=self.translator.gettext("Plan information"), url=None)]

    def present(
        self, response: GetPlanDetailsInteractor.Response
    ) -> GetPlanDetailsCompanyViewModel:
        plan_details = response.plan_details
        current_user = self.session.get_current_user()
        assert current_user
        current_user_is_planner = response.plan_details.planner_id == current_user
        show_own_plan_action_section = (
            current_user_is_planner and plan_details.is_active
        )
        view_model = GetPlanDetailsCompanyViewModel(
            details=self.plan_details_service.format_plan_details(plan_details),
            show_own_plan_action_section=show_own_plan_action_section,
            own_plan_action=self._create_own_plan_action_section(plan_details),
        )
        return view_model

    def _create_own_plan_action_section(self, plan: PlanDetails) -> OwnPlanAction:
        section = OwnPlanAction(
            is_cooperating=plan.is_cooperating,
            plan_id=str(plan.plan_id),
            cooperation_id=str(plan.cooperation) if plan.cooperation else None,
            request_coop_url=(
                self.url_index.get_request_coop_url()
                if not plan.is_cooperating
                else None
            ),
        )
        return section
