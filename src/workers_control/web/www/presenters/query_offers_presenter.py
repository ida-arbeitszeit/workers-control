from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from workers_control.core.interactors.query_offers import (
    OfferQueryResponse,
    QueriedOffer,
)
from workers_control.web.pagination import Pagination, Paginator
from workers_control.web.request import Request
from workers_control.web.session import Session, UserRole
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex, UserUrlIndex


@dataclass
class ResultTableRow:
    offer_details_url: str
    provider_url: str
    provider_name: str
    name: str
    description: str
    price_per_unit: str
    is_basic_service: bool
    is_public_service: bool
    is_cooperating: bool
    is_expired: bool
    is_own_plan: bool
    is_own_basic_service: bool
    show_consumption_icon: bool
    is_consumption_disabled: bool
    consumption_url: str


@dataclass
class ResultsTable:
    rows: list[ResultTableRow]


@dataclass
class QueryOffersViewModel:
    total_results: int
    results: ResultsTable
    show_results: bool
    pagination: Pagination


@dataclass
class QueryOffersPresenter:
    user_url_index: UserUrlIndex
    url_index: UrlIndex
    translator: Translator
    request: Request
    session: Session

    def present(self, response: OfferQueryResponse) -> QueryOffersViewModel:
        user_role = self.session.get_user_role()
        current_user = self.session.get_current_user()
        return QueryOffersViewModel(
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

    def get_empty_view_model(self) -> QueryOffersViewModel:
        return QueryOffersViewModel(
            total_results=0,
            results=ResultsTable(rows=[]),
            show_results=False,
            pagination=Pagination(is_visible=False, pages=[]),
        )

    def _build_row(
        self,
        result: QueriedOffer,
        user_role: Optional[UserRole],
        current_user: Optional[UUID],
    ) -> ResultTableRow:
        if result.is_basic_service:
            return self._build_basic_service_row(result, user_role, current_user)
        return self._build_plan_row(result, user_role, current_user)

    def _build_basic_service_row(
        self,
        result: QueriedOffer,
        user_role: Optional[UserRole],
        current_user: Optional[UUID],
    ) -> ResultTableRow:
        is_own_basic_service = (
            user_role == UserRole.member and current_user == result.provider_id
        )
        if user_role == UserRole.member and not is_own_basic_service:
            consumption_url = (
                self.url_index.get_register_private_consumption_of_basic_service_url(
                    basic_service_id=result.id
                )
            )
            is_consumption_disabled = False
        elif user_role == UserRole.company:
            consumption_url = (
                self.url_index.get_register_productive_consumption_of_basic_service_url(
                    basic_service_id=result.id
                )
            )
            is_consumption_disabled = False
        else:
            consumption_url = ""
            is_consumption_disabled = True
        return ResultTableRow(
            offer_details_url=self.url_index.get_basic_service_url(result.id),
            provider_url="",
            provider_name=result.provider_name,
            name=result.name,
            description=self._format_description(result.description),
            price_per_unit="",
            is_basic_service=True,
            is_public_service=False,
            is_cooperating=False,
            is_expired=False,
            is_own_plan=False,
            is_own_basic_service=is_own_basic_service,
            show_consumption_icon=user_role in (UserRole.member, UserRole.company),
            is_consumption_disabled=is_consumption_disabled,
            consumption_url=consumption_url,
        )

    def _build_plan_row(
        self,
        result: QueriedOffer,
        user_role: Optional[UserRole],
        current_user: Optional[UUID],
    ) -> ResultTableRow:
        is_own_plan = (
            user_role == UserRole.company and current_user == result.provider_id
        )
        if user_role == UserRole.member:
            consumption_url = self.url_index.get_register_private_consumption_url(
                plan_id=result.id
            )
        elif user_role == UserRole.company:
            consumption_url = self.url_index.get_register_productive_consumption_url(
                plan_id=result.id
            )
        else:
            consumption_url = ""
        assert result.price_per_unit is not None
        return ResultTableRow(
            offer_details_url=self.user_url_index.get_plan_details_url(result.id),
            provider_url=self.url_index.get_company_summary_url(
                company_id=result.provider_id,
            ),
            provider_name=result.provider_name,
            name=result.name,
            description=self._format_description(result.description),
            price_per_unit=str(round(result.price_per_unit, 2)),
            is_basic_service=False,
            is_public_service=result.is_public_service,
            is_cooperating=result.is_cooperating,
            is_expired=result.is_expired,
            is_own_plan=is_own_plan,
            is_own_basic_service=False,
            show_consumption_icon=user_role in (UserRole.member, UserRole.company),
            is_consumption_disabled=result.is_expired or is_own_plan,
            consumption_url=consumption_url,
        )

    @staticmethod
    def _format_description(description: str) -> str:
        return "".join(description.splitlines())[:150]

    def _create_pagination(self, response: OfferQueryResponse) -> Pagination:
        paginator = Paginator(
            request=self.request,
            total_results=response.total_results,
        )
        return Pagination(
            is_visible=paginator.number_of_pages > 1,
            pages=paginator.get_pages(),
        )
