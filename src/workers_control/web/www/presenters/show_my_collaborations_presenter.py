from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from workers_control.core.interactors.list_coordinations_of_company import (
    CooperationInfo,
    ListCoordinationsOfCompanyResponse,
)
from workers_control.core.interactors.list_my_cooperating_plans import (
    ListMyCooperatingPlansInteractor,
)
from workers_control.core.interactors.show_company_cooperations import (
    InboundCoopRequest,
    OutboundCoopRequest,
    Response,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class ListOfCoordinationsRow:
    collab_id: str
    collab_creation_date: str
    collab_name: str
    collab_definition: List[str]
    count_plans_in_collab: str
    collab_summary_url: str


@dataclass
class ListOfInboundCollaborationRequestsRow:
    collab_id: str
    collab_name: str
    plan_id: str
    plan_name: str
    plan_url: str
    planner_name: str
    planner_url: str


@dataclass
class ListOfOutboundCollaborationRequestsRow:
    plan_id: str
    plan_name: str
    plan_url: str
    collab_id: str
    collab_name: str


@dataclass
class CollaboratingPlan:
    plan_id: str
    plan_name: str
    plan_url: str
    collab_id: str
    collab_name: str
    collab_url: str


@dataclass
class ListOfMyCollaboratingPlans:
    rows: List[CollaboratingPlan]


@dataclass
class ListOfCoordinationsTable:
    rows: List[ListOfCoordinationsRow]


@dataclass
class ListOfInboundCollaborationRequestsTable:
    rows: List[ListOfInboundCollaborationRequestsRow]


@dataclass
class ListOfOutboundCollaborationRequestsTable:
    rows: List[ListOfOutboundCollaborationRequestsRow]


@dataclass
class ShowMyCollaborationsViewModel:
    list_of_coordinations: ListOfCoordinationsTable
    list_of_inbound_collab_requests: ListOfInboundCollaborationRequestsTable
    list_of_outbound_collab_requests: ListOfOutboundCollaborationRequestsTable
    list_of_my_collaborating_plans: ListOfMyCollaboratingPlans

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShowMyCollaborationsPresenter:
    url_index: UrlIndex
    translator: Translator

    def create_navbar_items(self) -> list[NavbarItem]:
        return [NavbarItem(text=self.translator.gettext("My collaborations"), url=None)]

    def present(
        self,
        *,
        list_coord_response: ListCoordinationsOfCompanyResponse,
        show_company_collaborations_response: Response,
        list_my_collaborating_plans_response: ListMyCooperatingPlansInteractor.Response,
    ) -> ShowMyCollaborationsViewModel:
        list_of_coordinations = ListOfCoordinationsTable(
            rows=[
                self._display_coordination_table_row(collab)
                for collab in list_coord_response.coordinations
            ]
        )
        list_of_inbound_collab_requests = ListOfInboundCollaborationRequestsTable(
            rows=[
                self._display_inbound_collab_requests(plan)
                for plan in show_company_collaborations_response.inbound_cooperation_requests
            ]
        )

        list_of_outbound_collab_requests = ListOfOutboundCollaborationRequestsTable(
            rows=[
                self._display_outbound_collab_requests(plan)
                for plan in show_company_collaborations_response.outbound_cooperation_requests
            ]
        )
        list_of_my_collaborating_plans = ListOfMyCollaboratingPlans(
            rows=[
                self._display_my_collaborating_plans(plan)
                for plan in list_my_collaborating_plans_response.cooperating_plans
            ]
        )
        return ShowMyCollaborationsViewModel(
            list_of_coordinations,
            list_of_inbound_collab_requests,
            list_of_outbound_collab_requests,
            list_of_my_collaborating_plans,
        )

    def _display_coordination_table_row(
        self, collab: CooperationInfo
    ) -> ListOfCoordinationsRow:
        return ListOfCoordinationsRow(
            collab_id=str(collab.id),
            collab_creation_date=str(collab.creation_date),
            collab_name=collab.name,
            collab_definition=collab.definition.splitlines(),
            count_plans_in_collab=str(collab.count_plans_in_coop),
            collab_summary_url=self.url_index.get_collab_summary_url(
                collab_id=collab.id
            ),
        )

    def _display_inbound_collab_requests(
        self, plan: InboundCoopRequest
    ) -> ListOfInboundCollaborationRequestsRow:
        return ListOfInboundCollaborationRequestsRow(
            collab_id=str(plan.coop_id),
            collab_name=plan.coop_name,
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_details_url(plan_id=plan.plan_id),
            planner_name=plan.planner_name,
            planner_url=self.url_index.get_company_summary_url(
                company_id=plan.planner_id
            ),
        )

    def _display_outbound_collab_requests(
        self, plan: OutboundCoopRequest
    ) -> ListOfOutboundCollaborationRequestsRow:
        return ListOfOutboundCollaborationRequestsRow(
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_details_url(plan_id=plan.plan_id),
            collab_id=str(plan.coop_id),
            collab_name=plan.coop_name,
        )

    def _display_my_collaborating_plans(
        self, plan: ListMyCooperatingPlansInteractor.CooperatingPlan
    ) -> CollaboratingPlan:
        return CollaboratingPlan(
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_details_url(plan_id=plan.plan_id),
            collab_id=str(plan.coop_id),
            collab_name=plan.coop_name,
            collab_url=self.url_index.get_collab_summary_url(collab_id=plan.coop_id),
        )
