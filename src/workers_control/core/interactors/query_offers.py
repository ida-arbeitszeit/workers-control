from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from workers_control.core import records
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import (
    BasicServiceResult,
    DatabaseGateway,
    PlanResult,
)
from workers_control.core.services.price_calculator import PriceCalculator


class OfferFilter(enum.Enum):
    by_offer_id = enum.auto()
    by_offer_name = enum.auto()


class OfferSorting(enum.Enum):
    by_activation = enum.auto()
    by_provider_name = enum.auto()


@dataclass
class OfferQueryResponse:
    results: List[QueriedOffer]
    total_results: int
    request: QueryOffersRequest


@dataclass
class QueriedOffer:
    id: UUID
    name: str
    description: str
    provider_name: str
    provider_id: UUID
    created_or_approved_on: datetime
    is_basic_service: bool
    price_per_unit: Optional[Decimal] = None
    is_public_service: bool = False
    is_cooperating: bool = False
    is_expired: bool = False


@dataclass
class QueryOffersRequest:
    query_string: Optional[str]
    filter_category: OfferFilter
    sorting_category: OfferSorting
    include_expired_plans: bool
    include_basic_services: bool
    offset: Optional[int] = None
    limit: Optional[int] = None


@dataclass
class QueryOffersInteractor:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway
    price_calculator: PriceCalculator

    def execute(self, request: QueryOffersRequest) -> OfferQueryResponse:
        plan_offers, plan_total = self._query_plans(request)
        if request.include_basic_services:
            bs_offers, bs_total = self._query_basic_services(request)
        else:
            bs_offers, bs_total = [], 0
        merged = plan_offers + bs_offers
        merged.sort(key=self._sort_key(request.sorting_category))
        offset = request.offset or 0
        end = offset + request.limit if request.limit is not None else len(merged)
        merged = merged[offset:end]
        return OfferQueryResponse(
            results=merged,
            total_results=plan_total + bs_total,
            request=request,
        )

    def _query_plans(
        self, request: QueryOffersRequest
    ) -> tuple[list[QueriedOffer], int]:
        now = self.datetime_service.now()
        plans = self.database_gateway.get_plans().that_were_approved_before(now)
        if not request.include_expired_plans:
            plans = plans.that_will_expire_after(now)
        plans = self._apply_plan_filter(
            plans, request.query_string, request.filter_category
        )
        total = len(plans)
        plans = self._apply_plan_sorting(plans, request.sorting_category)
        joined = plans.joined_with_planner_and_cooperation()
        results = [
            self._plan_to_offer(plan, planner, cooperation)
            for plan, planner, cooperation in joined
        ]
        return results, total

    def _query_basic_services(
        self, request: QueryOffersRequest
    ) -> tuple[list[QueriedOffer], int]:
        basic_services = self.database_gateway.get_basic_services()
        basic_services = self._apply_basic_service_filter(
            basic_services, request.query_string, request.filter_category
        )
        total = len(basic_services)
        basic_services = self._apply_basic_service_sorting(
            basic_services, request.sorting_category
        )
        joined = basic_services.joined_with_provider()
        results = [
            self._basic_service_to_offer(basic_service, provider)
            for basic_service, provider in joined
        ]
        return results, total

    def _apply_plan_filter(
        self, plans: PlanResult, query: Optional[str], filter_by: OfferFilter
    ) -> PlanResult:
        if query is None:
            return plans
        if filter_by == OfferFilter.by_offer_id:
            return plans.with_id_containing(query)
        return plans.with_product_name_containing(query)

    def _apply_plan_sorting(
        self, plans: PlanResult, sort_by: OfferSorting
    ) -> PlanResult:
        if sort_by == OfferSorting.by_provider_name:
            return plans.ordered_by_planner_name()
        return plans.ordered_by_approval_date(ascending=False)

    def _apply_basic_service_filter(
        self,
        basic_services: BasicServiceResult,
        query: Optional[str],
        filter_by: OfferFilter,
    ) -> BasicServiceResult:
        if query is None:
            return basic_services
        if filter_by == OfferFilter.by_offer_id:
            return basic_services.with_id_containing(query)
        return basic_services.with_name_containing(query)

    def _apply_basic_service_sorting(
        self,
        basic_services: BasicServiceResult,
        sort_by: OfferSorting,
    ) -> BasicServiceResult:
        if sort_by == OfferSorting.by_provider_name:
            return basic_services.ordered_by_provider_name()
        return basic_services.ordered_by_creation_date(ascending=False)

    def _sort_key(self, sort_by: OfferSorting):
        if sort_by == OfferSorting.by_provider_name:
            return lambda offer: offer.provider_name.lower()
        return lambda offer: -offer.created_or_approved_on.timestamp()

    def _plan_to_offer(
        self,
        plan: records.Plan,
        planner: records.Company,
        cooperation: Optional[records.Cooperation],
    ) -> QueriedOffer:
        price_per_unit = self.price_calculator.calculate_price(plan.id)
        assert plan.approval_date
        return QueriedOffer(
            id=plan.id,
            name=plan.prd_name,
            description=plan.description,
            provider_name=planner.name,
            provider_id=plan.planner,
            created_or_approved_on=plan.approval_date,
            is_basic_service=False,
            price_per_unit=price_per_unit,
            is_public_service=plan.is_public_service,
            is_cooperating=bool(cooperation),
            is_expired=plan.is_expired_as_of(self.datetime_service.now()),
        )

    def _basic_service_to_offer(
        self,
        basic_service: records.BasicService,
        provider: records.Member,
    ) -> QueriedOffer:
        return QueriedOffer(
            id=basic_service.id,
            name=basic_service.name,
            description=basic_service.description,
            provider_name=provider.name,
            provider_id=basic_service.provider,
            created_or_approved_on=basic_service.created_on,
            is_basic_service=True,
        )
