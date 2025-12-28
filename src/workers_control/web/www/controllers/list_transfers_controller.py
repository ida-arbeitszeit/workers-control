from dataclasses import dataclass

from workers_control.core.interactors.list_transfers import Request as InteractorRequest
from workers_control.web.pagination import (
    DEFAULT_PAGE_SIZE,
    calculate_current_offset,
)
from workers_control.web.request import Request


@dataclass
class ListTransfersController:
    request: Request

    def create_interactor_request(self) -> InteractorRequest:
        offset = calculate_current_offset(request=self.request, limit=DEFAULT_PAGE_SIZE)
        return InteractorRequest(
            offset=offset,
            limit=DEFAULT_PAGE_SIZE,
        )
