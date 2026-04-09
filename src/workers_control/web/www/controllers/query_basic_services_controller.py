from dataclasses import dataclass
from typing import Optional, Protocol

from workers_control.core.interactors.query_basic_services import (
    QueryBasicServicesRequest,
)
from workers_control.web.pagination import DEFAULT_PAGE_SIZE, calculate_current_offset
from workers_control.web.request import Request


class QueryBasicServicesFormData(Protocol):
    def get_query_string(self) -> str: ...


@dataclass
class QueryBasicServicesController:
    def import_form_data(
        self,
        form: Optional[QueryBasicServicesFormData] = None,
        request: Optional[Request] = None,
    ) -> QueryBasicServicesRequest:
        if form is None:
            query = None
        else:
            query = form.get_query_string().strip() or None
        offset = (
            calculate_current_offset(request=request, limit=DEFAULT_PAGE_SIZE)
            if request
            else 0
        )
        return QueryBasicServicesRequest(
            query_string=query,
            offset=offset,
            limit=DEFAULT_PAGE_SIZE,
        )
