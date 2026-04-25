from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from workers_control.core.interactors.query_plans import PlanQueryResponse, QueriedPlan
from workers_control.web.notification import Notifier
from workers_control.web.pagination import Pagination, Paginator
from workers_control.web.request import Request
from workers_control.web.session import Session, UserRole
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex, UserUrlIndex


@dataclass
class ResultTableRow:
    plan_details_url: str
    company_summary_url: str
    company_name: str
    product_name: str
    description: str
    price_per_unit: str
    is_public_service: bool
    is_cooperating: bool
    is_expired: bool
    is_own_plan: bool
    show_consumption_icon: bool
    is_consumption_disabled: bool
    consumption_url: str


@dataclass
class ResultsTable:
    rows: list[ResultTableRow]


@dataclass
class QueryPlansViewModel:
    total_results: int
    results: ResultsTable
    show_results: bool
    pagination: Pagination


@dataclass
class QueryPlansPresenter:
    user_url_index: UserUrlIndex
    url_index: UrlIndex
    user_notifier: Notifier
    translator: Translator
    request: Request
    session: Session

    def present(self, response: PlanQueryResponse) -> QueryPlansViewModel:
        if not response.results:
            self.user_notifier.display_warning(self.translator.gettext("No results."))
        user_role = self.session.get_user_role()
        current_user = self.session.get_current_user()
        return QueryPlansViewModel(
            total_results=response.total_results,
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    self._build_row(result, user_role, current_user)
                    for result in response.results
                ],
            ),
            pagination=self._create_pagination(response),
        )

    def get_empty_view_model(self) -> QueryPlansViewModel:
        return QueryPlansViewModel(
            total_results=0,
            results=ResultsTable(rows=[]),
            show_results=False,
            pagination=Pagination(is_visible=False, pages=[]),
        )

    def _build_row(
        self,
        result: QueriedPlan,
        user_role: Optional[UserRole],
        current_user: Optional[UUID],
    ) -> ResultTableRow:
        is_own_plan = (
            user_role == UserRole.company and current_user == result.company_id
        )
        show_consumption_icon = user_role in (UserRole.member, UserRole.company)
        if user_role == UserRole.member:
            consumption_url = self.url_index.get_register_private_consumption_url(
                plan_id=result.plan_id
            )
        elif user_role == UserRole.company:
            consumption_url = self.url_index.get_register_productive_consumption_url(
                plan_id=result.plan_id
            )
        else:
            consumption_url = ""
        return ResultTableRow(
            plan_details_url=self.user_url_index.get_plan_details_url(result.plan_id),
            company_summary_url=self.url_index.get_company_summary_url(
                company_id=result.company_id,
            ),
            company_name=result.company_name,
            product_name=result.product_name,
            description="".join(result.description.splitlines())[:150],
            price_per_unit=str(round(result.price_per_unit, 2)),
            is_public_service=result.is_public_service,
            is_cooperating=result.is_cooperating,
            is_expired=result.is_expired,
            is_own_plan=is_own_plan,
            show_consumption_icon=show_consumption_icon,
            is_consumption_disabled=result.is_expired or is_own_plan,
            consumption_url=consumption_url,
        )

    def _create_pagination(self, response: PlanQueryResponse) -> Pagination:
        paginator = Paginator(
            request=self.request,
            total_results=response.total_results,
        )
        return Pagination(
            is_visible=paginator.number_of_pages > 1,
            pages=paginator.get_pages(),
        )
