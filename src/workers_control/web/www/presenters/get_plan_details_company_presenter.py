from dataclasses import dataclass

from workers_control.core.interactors.get_plan_details import GetPlanDetailsInteractor
from workers_control.core.services.plan_details import PlanDetails
from workers_control.web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.www.navbar import NavbarItem


@dataclass
class OwnPlanAction:
    plan_id: str
    cooperation_id: str | None


@dataclass
class GetPlanDetailsCompanyViewModel:
    details: PlanDetailsWeb
    show_own_plan_action_section: bool
    own_plan_action: OwnPlanAction


@dataclass
class GetPlanDetailsCompanyPresenter:
    plan_details_service: PlanDetailsFormatter
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
            current_user_is_planner
            and plan_details.is_active
            and plan_details.is_cooperating
        )
        view_model = GetPlanDetailsCompanyViewModel(
            details=self.plan_details_service.format_plan_details(plan_details),
            show_own_plan_action_section=show_own_plan_action_section,
            own_plan_action=self._create_own_plan_action_section(plan_details),
        )
        return view_model

    def _create_own_plan_action_section(self, plan: PlanDetails) -> OwnPlanAction:
        section = OwnPlanAction(
            plan_id=str(plan.plan_id),
            cooperation_id=str(plan.cooperation) if plan.cooperation else None,
        )
        return section
