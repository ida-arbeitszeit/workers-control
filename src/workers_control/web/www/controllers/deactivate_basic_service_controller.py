from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors import deactivate_basic_service
from workers_control.core.repositories import DatabaseGateway
from workers_control.web.session import Session


@dataclass
class InvalidRequest:
    status_code: int


@dataclass
class DeactivateBasicServiceController:
    session: Session
    database_gateway: DatabaseGateway

    def process_request(
        self, basic_service_id: UUID
    ) -> deactivate_basic_service.Request | InvalidRequest:
        user_id = self.session.get_current_user()
        assert user_id
        owned = (
            self.database_gateway.get_basic_services()
            .of_provider(user_id)
            .with_id(basic_service_id)
            .first()
        )
        if owned is None:
            return InvalidRequest(status_code=404)
        return deactivate_basic_service.Request(basic_service=basic_service_id)
