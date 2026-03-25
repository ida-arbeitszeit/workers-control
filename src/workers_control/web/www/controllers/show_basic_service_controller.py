from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors import show_basic_service


@dataclass
class ShowBasicServiceController:
    def create_request(
        self, basic_service_id: UUID
    ) -> show_basic_service.ShowBasicServiceRequest:
        return show_basic_service.ShowBasicServiceRequest(
            basic_service_id=basic_service_id
        )
