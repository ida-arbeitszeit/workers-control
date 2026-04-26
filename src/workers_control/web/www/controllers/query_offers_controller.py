from dataclasses import dataclass
from typing import Optional, Protocol

from workers_control.core.interactors.query_offers import (
    OfferFilter,
    OfferSorting,
    QueryOffersRequest,
)
from workers_control.web.pagination import DEFAULT_PAGE_SIZE, calculate_current_offset
from workers_control.web.request import Request


class QueryOffersFormData(Protocol):
    def get_query_string(self) -> str: ...

    def get_category_string(self) -> str: ...

    def get_radio_string(self) -> str: ...

    def get_include_expired_plans(self) -> bool: ...

    def get_include_basic_services(self) -> bool: ...


@dataclass
class QueryOffersController:
    def import_form_data(
        self,
        form: Optional[QueryOffersFormData] = None,
        request: Optional[Request] = None,
    ) -> QueryOffersRequest:
        if form is None:
            query = None
            filter_category = OfferFilter.by_offer_name
            sorting_category = OfferSorting.by_activation
            include_expired_plans = False
            include_basic_services = True
        else:
            query = form.get_query_string().strip() or None
            filter_category = self._import_filter_category(form)
            sorting_category = self._import_sorting_category(form)
            include_expired_plans = form.get_include_expired_plans()
            include_basic_services = form.get_include_basic_services()
        offset = (
            calculate_current_offset(request=request, limit=DEFAULT_PAGE_SIZE)
            if request
            else 0
        )
        return QueryOffersRequest(
            query_string=query,
            filter_category=filter_category,
            sorting_category=sorting_category,
            include_expired_plans=include_expired_plans,
            include_basic_services=include_basic_services,
            offset=offset,
            limit=DEFAULT_PAGE_SIZE,
        )

    def _import_filter_category(self, form: QueryOffersFormData) -> OfferFilter:
        if form.get_category_string() == "offer_id":
            return OfferFilter.by_offer_id
        return OfferFilter.by_offer_name

    def _import_sorting_category(self, form: QueryOffersFormData) -> OfferSorting:
        if form.get_radio_string() == "provider_name":
            return OfferSorting.by_provider_name
        return OfferSorting.by_activation
